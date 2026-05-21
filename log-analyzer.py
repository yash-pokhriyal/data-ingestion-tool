import sys
import os
import re
import json
import argparse
from collections import defaultdict, Counter
from datetime import datetime

# =========================================================
# CONFIGURATION
# =========================================================

TOP_SLOW_ENDPOINTS = 5
TOP_ERROR_PATTERNS = 5
ASCII_BAR_WIDTH = 25

# =========================================================
# TIMESTAMP NORMALIZATION
# =========================================================

SUPPORTED_TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y/%m/%d %H:%M:%S",
    "%d-%b-%Y %H:%M:%S"
]


def parse_timestamp(ts):

    if not ts:
        return None

    ts = ts.strip()

    # Unix epoch
    if ts.isdigit() and len(ts) == 10:
        try:
            return datetime.utcfromtimestamp(int(ts))
        except Exception:
            return None

    for fmt in SUPPORTED_TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue

    return None


# =========================================================
# RESPONSE TIME NORMALIZATION
# =========================================================

def parse_response_time(rt_str):

    if not rt_str:
        return 0

    rt_str = str(rt_str).strip().lower()

    try:

        if rt_str.endswith("ms"):
            return int(abs(float(rt_str[:-2])))

        if rt_str.endswith("s"):
            return int(abs(float(rt_str[:-1])) * 1000)

        return int(abs(float(rt_str)))

    except (ValueError, TypeError):
        return 0


# =========================================================
# PATH NORMALIZATION
# =========================================================

def normalize_path(path):

    if not path:
        return "UNKNOWN"

    path = re.sub(r"/\d+(?=/|$)", "/{id}", path)

    path = re.sub(
        r"/[0-9a-fA-F\-]{8,}(?=/|$)",
        "/{id}",
        path
    )

    return path


# =========================================================
# REGEX PATTERNS
# =========================================================

TIMESTAMP_REGEX = re.compile(
    r"""^(
        \d{4}[-/]\d{2}[-/]\d{2} |
        \d{2}-[A-Za-z]{3}-\d{4} |
        \d{10}
    )""",
    re.VERBOSE
)

STANDARD_LOG_REGEX = re.compile(
    r"""
    ^
    (\S+(?:\s+\S+)?)         # timestamp
    \s+
    (\S+)                    # ip
    \s+
    ([A-Z]+)                 # method
    \s+
    (\S+)                    # path
    \s+
    (\d+|-)                  # status
    \s+
    (\S+)                    # response time
    (.*)?                    # extra fields
    $
    """,
    re.VERBOSE
)

STACK_TRACE_HINTS = (
    "traceback",
    "exception",
    "error:",
    "fatal",
    "panic"
)

# =========================================================
# ASCII CHART
# =========================================================

def build_ascii_bar(value, max_value):

    if max_value <= 0:
        return ""

    scaled = int((value / max_value) * ASCII_BAR_WIDTH)

    return "█" * scaled


# =========================================================
# PERCENTILE CALCULATION
# =========================================================

def percentile(values, pct):

    if not values:
        return 0

    values = sorted(values)

    index = int((pct / 100) * len(values))

    index = min(index, len(values) - 1)

    return values[index]


# =========================================================
# JSON PROCESSING
# =========================================================

def process_json_log(raw_line, metrics):

    try:

        data = json.loads(raw_line)

        metrics["json_lines"] += 1
        metrics["parsed_lines"] += 1

        path = normalize_path(data.get("path", "UNKNOWN"))

        status = str(data.get("status", "UNKNOWN"))

        duration = parse_response_time(
            data.get("duration", "0")
        )

        timestamp = parse_timestamp(
            str(data.get("timestamp", ""))
        )

        if timestamp:
            metrics["timestamps"].append(timestamp)

        metrics["status_counts"][status] += 1
        metrics["endpoint_times"][path].append(duration)
        metrics["all_durations"].append(duration)

        if status.startswith(("4", "5")):
            incident = f"JSON {path} -> HTTP {status}"
            metrics["error_patterns"][incident] += 1

        return True

    except json.JSONDecodeError:

        metrics["json_parse_failures"] += 1
        metrics["malformed_lines"] += 1

        return False


# =========================================================
# STANDARD LOG PROCESSING
# =========================================================

def process_standard_log(raw_line, metrics):

    match = STANDARD_LOG_REGEX.match(raw_line)

    if not match:
        metrics["malformed_lines"] += 1
        return False

    (
        timestamp_raw,
        ip,
        method,
        path,
        status,
        duration_raw,
        extra
    ) = match.groups()

    metrics["parsed_lines"] += 1

    timestamp = parse_timestamp(timestamp_raw)

    if timestamp:
        metrics["timestamps"].append(timestamp)

    if status == "-":
        status = "MISSING"

    norm_path = normalize_path(path)

    duration_ms = parse_response_time(duration_raw)

    metrics["status_counts"][status] += 1
    metrics["endpoint_times"][norm_path].append(duration_ms)
    metrics["all_durations"].append(duration_ms)

    metrics["slow_requests"].append(
        (duration_ms, method, norm_path, status)
    )

    if status.startswith(("4", "5")) or status == "MISSING":
        incident = f"{method} {norm_path} -> HTTP {status}"
        metrics["error_patterns"][incident] += 1

    return True


# =========================================================
# REPORT EXPORT
# =========================================================

def export_json_report(metrics, output_file):

    export_data = {
        "total_lines": metrics["total_lines"],
        "parsed_lines": metrics["parsed_lines"],
        "malformed_lines": metrics["malformed_lines"],
        "empty_lines": metrics["empty_lines"],
        "json_lines": metrics["json_lines"],
        "stack_trace_incidents": metrics["stack_trace_incidents"],
        "status_distribution": dict(metrics["status_counts"]),
        "top_errors": dict(metrics["error_patterns"])
    }

    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)


# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze_logs(file_path, json_output=None):

    if not os.path.exists(file_path):
        print(f"\n❌ ERROR: File not found -> {file_path}\n")
        sys.exit(1)

    metrics = {
        "total_lines": 0,
        "parsed_lines": 0,
        "malformed_lines": 0,
        "empty_lines": 0,
        "json_lines": 0,
        "json_parse_failures": 0,
        "stack_trace_lines": 0,
        "stack_trace_incidents": 0,
        "status_counts": Counter(),
        "endpoint_times": defaultdict(list),
        "error_patterns": Counter(),
        "slow_requests": [],
        "all_durations": [],
        "timestamps": []
    }

    in_stack_trace = False

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as log_file:

        for raw_line in log_file:

            metrics["total_lines"] += 1

            raw_line = raw_line.strip()

            # Empty lines
            if not raw_line:
                metrics["empty_lines"] += 1
                in_stack_trace = False
                continue

            # Stack trace detection
            lower_line = raw_line.lower()

            if (
                not TIMESTAMP_REGEX.match(raw_line)
                and not raw_line.startswith("{")
            ):

                if any(hint in lower_line for hint in STACK_TRACE_HINTS):

                    metrics["stack_trace_lines"] += 1

                    if not in_stack_trace:
                        metrics["stack_trace_incidents"] += 1
                        in_stack_trace = True

                    continue

            in_stack_trace = False

            # JSON logs
            if raw_line.startswith("{"):
                process_json_log(raw_line, metrics)
                continue

            # Standard logs
            process_standard_log(raw_line, metrics)

    render_report(file_path, metrics)

    if json_output:
        export_json_report(metrics, json_output)
        print(f"\n📁 JSON metrics exported -> {json_output}")


# =========================================================
# REPORTING
# =========================================================

def render_report(file_path, metrics):

    print("\n" + "═" * 70)
    print("        🚀 PRODUCTION LOG ANALYTICS REPORT 🚀")
    print("═" * 70)

    print(f"📂 Source File            : {os.path.basename(file_path)}")
    print(f"📦 Total Lines            : {metrics['total_lines']}")
    print(f"✅ Parsed Entries         : {metrics['parsed_lines']}")
    print(f"⚠️  Malformed Entries     : {metrics['malformed_lines']}")
    print(f"📭 Empty Lines            : {metrics['empty_lines']}")
    print(f"⚙️  JSON Log Entries      : {metrics['json_lines']}")
    print(f"❌ JSON Parse Failures    : {metrics['json_parse_failures']}")

    print(
        f"🔥 Stack Trace Incidents  : "
        f"{metrics['stack_trace_incidents']} "
        f"({metrics['stack_trace_lines']} lines)"
    )

    print("\n" + "─" * 70)

    # STATUS DISTRIBUTION
    print("\n📊 HTTP STATUS DISTRIBUTION\n")

    if metrics["status_counts"]:

        max_status = max(metrics["status_counts"].values())

        for status, count in sorted(metrics["status_counts"].items()):

            bar = build_ascii_bar(count, max_status)

            print(f"[{status:<8}] {count:<6} {bar}")

    # LATENCY METRICS
    print("\n⚡ LATENCY METRICS\n")

    durations = metrics["all_durations"]

    if durations:

        avg_latency = sum(durations) / len(durations)

        print(f"Average Latency : {avg_latency:.2f}ms")
        print(f"P95 Latency     : {percentile(durations, 95)}ms")
        print(f"P99 Latency     : {percentile(durations, 99)}ms")
        print(f"Max Latency     : {max(durations)}ms")

    # SLOW ENDPOINTS
    print("\n🐢 TOP SLOWEST ENDPOINTS\n")

    averages = []

    for endpoint, durations in metrics["endpoint_times"].items():

        avg_duration = sum(durations) / len(durations)

        averages.append(
            (
                endpoint,
                avg_duration,
                len(durations)
            )
        )

    averages.sort(key=lambda x: x[1], reverse=True)

    for endpoint, avg_duration, count in averages[:TOP_SLOW_ENDPOINTS]:

        print(
            f"[{count:<5} reqs] "
            f"{endpoint:<35} "
            f"{avg_duration:>8.2f}ms"
        )

    # ERROR PATTERNS
    print("\n🚨 TOP ERROR PATTERNS\n")

    for incident, count in metrics["error_patterns"].most_common(
        TOP_ERROR_PATTERNS
    ):

        print(f"{count:<5}x  {incident}")

    # SLOW REQUESTS
    print("\n⏱ TOP SLOWEST REQUESTS\n")

    metrics["slow_requests"].sort(reverse=True)

    for duration, method, path, status in metrics["slow_requests"][:5]:

        print(
            f"{duration:>6}ms  "
            f"{method:<6} "
            f"{path:<35} "
            f"HTTP {status}"
        )

    print("\n" + "═" * 70 + "\n")


# =========================================================
# ENTRYPOINT
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Production Grade Log Analyzer"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Target log file path"
    )

    parser.add_argument(
        "--json-output",
        required=False,
        help="Optional JSON metrics export file"
    )

    args = parser.parse_args()

    analyze_logs(
        file_path=args.file,
        json_output=args.json_output
    )


if __name__ == "__main__":
    main()