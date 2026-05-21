# 🚀 Production-Grade Log Analyzer

> Built for operational resilience against malformed production telemetry.

A memory-safe, Dockerized log ingestion and analytics pipeline designed to process highly volatile, malformed, and mixed-format server logs without crashing.

Built to simulate real-world production debugging workflows where:
- logging formats drift over time
- stack traces interrupt request streams
- malformed lines appear unexpectedly
- telemetry becomes inconsistent under load

The analyzer is intentionally defensive and optimized for operational resilience rather than perfect input assumptions.

---

# ✨ Core Capabilities

✅ Stream-based memory-safe ingestion  
✅ Mixed timestamp format support  
✅ Smart route normalization  
✅ Stack trace aggregation  
✅ Hybrid JSON + plaintext parsing  
✅ Graceful malformed log handling  
✅ Interactive CLI metrics dashboard  
✅ Percentile latency analysis (P95/P99)  
✅ JSON metrics export support  
✅ Dockerized execution environment  

---

# 🏗️ Architecture Overview

The system is designed as a lightweight streaming ingestion pipeline focused on resilience and operational visibility.

### Pipeline Flow

```text
Raw Log File
      ↓
Streaming Line Reader
      ↓
Format Detection Engine
      ↓
Normalization Layer
      ↓
Aggregation Engine
      ↓
CLI Metrics Dashboard + JSON Export
```

### Internal Processing Stages

| Stage | Responsibility |
|---|---|
| Stream Reader | Reads logs safely line-by-line |
| Format Detector | Detects JSON vs plaintext logs |
| Parser Layer | Extracts timestamps, methods, paths, statuses |
| Normalization Engine | Normalizes routes and durations |
| Aggregation Engine | Builds operational metrics |
| Reporting Layer | Displays dashboards and exports JSON |

The analyzer intentionally prioritizes survivability over strict parsing assumptions.

---

# 📂 Project Structure

```text
log-analyzer-project/
│
├── scripts/
│   └── log-generater.py
│
├── .gitignore
├── log-analyzer.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── ANSWERS.md
```

---

# ⚡ Key Features

---

## 🧠 Memory-Safe Stream Processing

Processes logs line-by-line without loading entire files into memory.

Ideal for:
- massive production logs
- low-memory systems
- continuous ingestion workloads

```python
with open(file_path, "r") as f:
    for line in f:
        process(line)
```

---

## 🕒 Multi-Format Timestamp Support

The parser automatically handles inconsistent timestamp formats.

### Supported Formats

```text
2024-03-15T14:23:01Z
2024/03/15 14:23:01
15-Mar-2024 14:23:01
1710512581
```

---

## ⚙️ Response Time Normalization

Automatically converts inconsistent latency units into milliseconds.

### Supported Inputs

```text
142ms
0.142s
142
-12ms
0s
```

### Normalized Output

```text
142ms
142ms
142ms
12ms
0ms
```

---

## 🛣️ Smart Route Normalization

Prevents endpoint cardinality explosion caused by dynamic IDs.

### Example

```text
/api/users/12
/api/users/99
/api/users/8888
```

Automatically becomes:

```text
/api/users/{id}
```

This dramatically improves:
- aggregation accuracy
- endpoint analytics
- operational visibility

---

## 🔥 Stack Trace Aggregation

Multi-line exceptions are intelligently grouped into single operational incidents.

Supports:
- Python tracebacks
- Java-style exceptions
- interrupted multiline dumps
- partial crash writes

Instead of treating every trace line as malformed noise, the analyzer clusters them into meaningful incidents.

---

## 🧩 Hybrid JSON + Plaintext Parsing

Supports environments where teams accidentally mix:
- structured JSON logs
- legacy plaintext logs
- malformed payloads

### Example JSON Payload

```json
{
  "timestamp": "2024-03-15T14:23:01Z",
  "path": "/api/login",
  "status": 401,
  "duration": "89ms"
}
```

---

## 🛡️ Graceful Failure Handling

The analyzer is intentionally defensive.

It never crashes on:

- malformed lines
- broken JSON
- partial writes
- missing status codes
- invalid UTF-8 characters
- empty lines
- corrupted telemetry

All anomalies are safely counted and surfaced in operational metrics.

---

## Real-World Edge Cases Handled

| Edge Case | Behavior |
|---|---|
| Broken JSON payloads | safely skipped and counted |
| Partial log writes | marked malformed without crash |
| Blank lines | ignored safely |
| Missing status codes | normalized as `MISSING` |
| Invalid UTF-8 | replaced safely during ingestion |
| Stack traces | aggregated into single incidents |
| Mixed timestamp formats | automatically normalized |
| Unknown response units | converted gracefully |
| Extremely large files | streamed without memory explosion |

The parser is intentionally defensive because production telemetry is rarely clean or consistent.

---

## 📊 Interactive CLI Dashboard

The analyzer generates live terminal dashboards containing:

- HTTP status distributions
- average latency
- P95 latency
- P99 latency
- slowest endpoints
- error pattern aggregation
- stack trace incidents

### Example Output

```text
══════════════════════════════════════════════════════════════
        🚀 PRODUCTION LOG ANALYTICS REPORT 🚀
══════════════════════════════════════════════════════════════

📂 Source File            : test_server.log
📦 Total Lines            : 5000
✅ Parsed Entries         : 4721
⚠️  Malformed Entries     : 132
📭 Empty Lines            : 17
⚙️  JSON Log Entries      : 91
🔥 Stack Trace Incidents  : 24

📊 HTTP STATUS DISTRIBUTION

[200     ] 1420   ████████████████████
[404     ] 210    ███
[500     ] 73     ██

⚡ LATENCY METRICS

Average Latency : 184.22ms
P95 Latency     : 812ms
P99 Latency     : 4200ms
Max Latency     : 44111ms
```

---

# 🧪 Built-In Log Generator

The project includes a realistic noisy log generator for stress testing parser resilience.

### Generated Anomalies

✅ Alternate timestamps  
✅ Broken JSON payloads  
✅ Partial writes  
✅ Invalid UTF-8 characters  
✅ Stack traces  
✅ Missing status codes  
✅ Random latency spikes  
✅ Quoted user agents  
✅ Traffic bursts  
✅ Hybrid structured logs  

---

# 🐳 Dockerized Runtime

No local Python installation required.

Everything runs through Docker.

---

## Why Docker?

Docker ensures:
- identical runtime environments
- zero local dependency conflicts
- reproducible execution
- simplified evaluator setup
- platform portability across Linux/macOS/Windows

The entire project can be tested using only:

```bash
docker compose build
docker compose run --rm generator
docker compose run --rm analyzer
```

---

# 📦 Requirements

- Docker
- Docker Compose

---

# 🚀 Quick Start

---

## 1️⃣ Build Containers

```bash
docker compose build
```

---

## 2️⃣ Generate Realistic Test Logs

```bash
docker compose run --rm generator
```

Default output:

```text
test_server.log
```

---

## 3️⃣ Analyze Logs

```bash
docker compose run --rm analyzer
```

---

# 📂 Analyze Custom Log File

```bash
docker compose run --rm analyzer \
--file custom.log
```

---

# 📤 Export Metrics as JSON

```bash
docker compose run --rm analyzer \
--file test_server.log \
--json-output metrics.json
```

---

# ⚡ Example Stress Test

Generate 100,000 noisy log lines:

```bash
docker compose run --rm generator \
--output stress.log \
--lines 100000
```

Analyze them:

```bash
docker compose run --rm analyzer \
--file stress.log
```

---

# 🏗️ Technical Highlights

| Capability | Description |
|---|---|
| Stream Processing | Memory-safe line-by-line ingestion |
| Route Grouping | Prevents endpoint explosion |
| Percentile Metrics | P95 / P99 latency analysis |
| Stack Trace Clustering | Groups multiline incidents |
| Hybrid Parsing | JSON + plaintext support |
| Fault Tolerance | Never crashes on malformed input |
| Dockerized Runtime | Portable execution environment |

---

# 🎯 Design Philosophy

This project prioritizes:

- operational resilience
- graceful degradation
- observability
- parser survivability
- production realism
- memory efficiency

The analyzer intentionally assumes:

> logs in production are messy.

---

# 🔮 Future Improvements

Potential future upgrades:

- live web dashboard
- Prometheus metrics export
- anomaly detection engine
- concurrent parsing workers
- gzip log ingestion
- distributed ingestion pipeline
- Elasticsearch integration
- real-time streaming mode

---

# 📜 License

MIT License

---

# 👨‍💻 Author

**Yash Pokhriyal**

Production-grade log ingestion and analytics assessment project.


