import os
import random
import time
import json
import argparse
from datetime import datetime, timedelta

# =========================================================
# CONFIGURATION
# =========================================================

METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

PATHS = [
    "/api/users",
    "/api/login",
    "/api/users/{id}",
    "/api/products",
    "/api/checkout/{id}/pay",
    "/dashboard",
    "/assets/static/main.css"
]

STATUS_CODES = [
    "200",
    "201",
    "204",
    "400",
    "401",
    "403",
    "404",
    "500",
    "503"
]

IPS = [
    "192.168.1.42",
    "10.0.0.7",
    "172.16.0.5",
    "184.22.109.5",
    "127.0.0.1"
]

USER_AGENTS = [
    "Mozilla/5.0",
    "curl/8.0",
    "PostmanRuntime/7.36",
    "Python-requests/2.31",
    "Chrome/124.0"
]

REFERRERS = [
    "https://google.com/search?q=api",
    "https://dashboard.internal",
    "https://example.com/login",
    "-"
]

# =========================================================
# HELPERS
# =========================================================

def random_timestamp(current_time):

    formats = [
        current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_time.strftime("%Y/%m/%d %H:%M:%S"),
        current_time.strftime("%d-%b-%Y %H:%M:%S"),
        str(int(current_time.timestamp()))
    ]

    return random.choice(formats)


def random_path():

    path = random.choice(PATHS)

    if "{id}" in path:

        replacement = random.choice([
            str(random.randint(1, 99999)),
            f"{random.randint(1000,9999)}-abcd-{random.randint(1000,9999)}"
        ])

        path = path.replace("{id}", replacement)

    return path


def random_response_time():

    values = [
        f"{random.randint(5, 500)}ms",
        f"{random.uniform(0.01, 0.9):.3f}s",
        str(random.randint(5, 1000)),
        "0s",
        "-12ms",
        f"{random.randint(5000, 45000)}ms"
    ]

    return random.choice(values)


# =========================================================
# LOG GENERATORS
# =========================================================

def generate_standard_log(current_time):

    return (
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')} "
        f"{random.choice(IPS)} "
        f"{random.choice(METHODS)} "
        f"{random_path()} "
        f"{random.choice(STATUS_CODES)} "
        f"{random_response_time()}"
    )


def generate_alt_timestamp_log(current_time):

    return (
        f"{random_timestamp(current_time)} "
        f"{random.choice(IPS)} "
        f"GET "
        f"{random_path()} "
        f"200 "
        f"{random_response_time()}"
    )


def generate_missing_status_log(current_time):

    return (
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')} "
        f"{random.choice(IPS)} "
        f"POST "
        f"/api/login "
        f"- "
        f"{random_response_time()}"
    )


def generate_extended_log(current_time):

    return (
        f"{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')} "
        f"{random.choice(IPS)} "
        f"GET "
        f"{random_path()} "
        f"200 "
        f"{random_response_time()} "
        f"\"{random.choice(USER_AGENTS)}\" "
        f"\"{random.choice(REFERRERS)}\""
    )


def generate_json_log(current_time):

    payload = {
        "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ip": random.choice(IPS),
        "method": random.choice(METHODS),
        "path": random_path(),
        "status": random.choice([200, 401, 404, 500]),
        "duration": random_response_time()
    }

    return json.dumps(payload)


def generate_broken_json():

    samples = [
        '{"timestamp": "2024-03-15',
        '{"status": 500, "path": ',
        '{"method":"GET"',
        '{INVALID_JSON}'
    ]

    return random.choice(samples)


def generate_partial_write():

    samples = [
        "2024-03-15T14:23",
        "GET /api",
        "500 Internal",
        "192.168.",
        "ERROR:"
    ]

    return random.choice(samples)


def generate_stack_trace():

    return [
        "Traceback (most recent call last):",
        '  File "/app/views.py", line 42, in process_payment',
        "    amount = total / items_count",
        "ZeroDivisionError: division by zero",
        ""
    ]


# =========================================================
# MAIN GENERATOR
# =========================================================

def generate_mock_logs(filename, num_lines):

    current_time = datetime.utcnow()

    if os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    print(
        f"\n🚀 Generating {num_lines} log lines "
        f"inside '{filename}'...\n"
    )

    lines_written = 0

    with open(
        filename,
        "w",
        encoding="utf-8",
        errors="replace"
    ) as f:

        while lines_written < num_lines:

            current_time += timedelta(
                seconds=random.randint(1, 5)
            )

            probability = random.random()

            # =====================================================
            # 88% STANDARD TRAFFIC
            # =====================================================

            if probability < 0.88:

                burst_count = random.choice([1, 1, 1, 5, 10])

                for _ in range(burst_count):

                    if lines_written >= num_lines:
                        break

                    line = generate_standard_log(current_time)

                    f.write(line + "\n")

                    lines_written += 1

            # =====================================================
            # 3% ALT TIMESTAMP FORMATS
            # =====================================================

            elif probability < 0.91:

                f.write(
                    generate_alt_timestamp_log(current_time) + "\n"
                )

                lines_written += 1

            # =====================================================
            # 2% MISSING STATUS
            # =====================================================

            elif probability < 0.93:

                f.write(
                    generate_missing_status_log(current_time) + "\n"
                )

                lines_written += 1

            # =====================================================
            # 2% QUOTED EXTRA FIELDS
            # =====================================================

            elif probability < 0.95:

                f.write(
                    generate_extended_log(current_time) + "\n"
                )

                lines_written += 1

            # =====================================================
            # 2% STACK TRACES
            # =====================================================

            elif probability < 0.97:

                main_error = (
                    f"{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')} "
                    f"{random.choice(IPS)} "
                    f"POST "
                    f"/api/checkout/{random.randint(1,999)}/pay "
                    f"500 "
                    f"{random_response_time()}"
                )

                f.write(main_error + "\n")
                lines_written += 1

                for trace in generate_stack_trace():

                    if lines_written >= num_lines:
                        break

                    f.write(trace + "\n")

                    lines_written += 1

            # =====================================================
            # 2% VALID JSON LOGS
            # =====================================================

            elif probability < 0.99:

                f.write(
                    generate_json_log(current_time) + "\n"
                )

                lines_written += 1

            # =====================================================
            # 1% CORRUPTED DATA
            # =====================================================

            else:

                corruption_type = random.choice([
                    "broken_json",
                    "partial_write",
                    "unicode_garbage"
                ])

                if corruption_type == "broken_json":

                    f.write(generate_broken_json() + "\n")

                elif corruption_type == "partial_write":

                    f.write(generate_partial_write() + "\n")

                elif corruption_type == "unicode_garbage":

                    # RAW INVALID UTF-8 BYTES
                    f.buffer.write(
                        b"\xff\xfe INVALID_PAYLOAD\n"
                    )

                lines_written += 1

    print("✅ Log generation completed successfully.\n")
    print(f"📄 Output File : {filename}")
    print(f"📦 Total Lines : {lines_written}\n")


# =========================================================
# ENTRYPOINT
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Production Grade Mock Log Generator"
    )

    parser.add_argument(
        "--output",
        default="test_server.log",
        help="Output log file"
    )

    parser.add_argument(
        "--lines",
        type=int,
        default=5000,
        help="Number of log lines to generate"
    )

    args = parser.parse_args()

    generate_mock_logs(
        filename=args.output,
        num_lines=args.lines
    )


if __name__ == "__main__":
    main()