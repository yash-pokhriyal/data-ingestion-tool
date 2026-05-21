# Technical Assessment — ANSWERS.md

---

# 1. How to Run

## Question

> Give the exact command(s) or steps to run your project on a fresh machine. If anything needs installing, list it.

---

## Answer

### Requirements

The project only requires:

- Docker
- Docker Compose

No local Python installation or additional dependencies are required because the entire runtime environment is containerized.

---

### Setup Instructions

#### Step 1 — Build Docker Containers

```bash
docker compose build
```

---

#### Step 2 — Generate Test Logs

This generates a realistic noisy log file containing malformed entries, mixed timestamp formats, stack traces, JSON payloads, and telemetry anomalies.

```bash
docker compose run --rm generator
```

This creates:

```text
test_server.log
```

---

#### Step 3 — Analyze Logs

Run the analyzer against the generated log file:

```bash
docker compose run --rm analyzer
```

---

### Analyze Custom Log File

```bash
docker compose run --rm analyzer --file custom.log
```

---

### Export Metrics as JSON

```bash
docker compose run --rm analyzer \
--file test_server.log \
--json-output metrics.json
```

---

# 2. Stack Choice

## Question

> Why did you pick this stack/language/framework for this task?  
> What would have been a worse choice and why?

---

## Answer

I chose Python because it is lightweight, expressive, and extremely well-suited for text processing and stream-based file ingestion tasks. The standard library already provides strong support for regular expressions, JSON handling, file streaming, and defensive parsing, which allowed me to focus more on resilience and operational behavior instead of framework overhead.

I intentionally kept the implementation dependency-light to reduce setup complexity and improve portability.

I chose Docker to make the project completely environment-independent. The evaluator can run the exact same runtime configuration on macOS, Linux, or Windows without worrying about Python versions, package conflicts, or local system differences. Since this assessment focuses heavily on reliability against unknown input, I wanted the runtime environment itself to also be predictable and reproducible.

The CLI-based approach was intentional as well. For operational debugging workflows, terminal-based tooling is often faster and more practical than building a full web interface. The assignment emphasized resilience, ingestion quality, and handling malformed telemetry, so I prioritized parser robustness and operational metrics instead of frontend complexity.

A worse choice for this task would have been using a lower-level language such as C for rapid development because it would significantly increase implementation complexity for parsing, memory safety, and string handling. Similarly, using a heavy enterprise stack such as Java with large frameworks would have introduced unnecessary boilerplate and slower iteration speed for a relatively focused ingestion tool.

Another poor design choice would have been loading entire log files into memory instead of streaming line-by-line. Since the assignment explicitly mentions potentially very large log files, stream processing is a much safer and more scalable approach.

---

# 3. One Real Edge Case

## Question

> Describe one specific edge case your code handles correctly.  
> Point to the file and line number.  
> Explain what would happen without that handling.

---

## Answer

One important edge case the analyzer handles correctly is multi-line stack trace aggregation.

### File

```text
log-analyzer.py
```

### Relevant Section

```python
if not timestamp_prefix.match(raw_line) and not raw_line.startswith("{"):
    stack_trace_lines += 1
    if not in_stack_trace:
        stack_trace_incident_count += 1
        in_stack_trace = True
    continue
```

This logic detects lines that no longer follow a normal log structure and treats them as part of a continuous stack trace incident instead of separate malformed log entries.

This matters because real production logs often contain exceptions such as Python tracebacks or Java stack traces that span multiple lines. Without this handling, every trace line would be counted as an isolated malformed entry, which would heavily distort operational metrics and hide the fact that they belong to the same crash event.

With this handling in place, the analyzer groups related trace lines into a single operational incident while still tracking the total number of traceback lines separately. This makes the final output significantly more useful for debugging and incident analysis.

---

# 4. AI Usage

## Question

> List every place you used AI (which tool, what you asked, what it gave you).  
> For at least one of these, describe something you changed about the AI output and why.

---

## Answer

I used a combination of ChatGPT and Google Gemini during development, mainly for brainstorming implementation ideas, improving resilience handling, and refining documentation structure.

---

## Where I Used AI

| Tool | Purpose |
|---|---|
| Google Gemini | Initial implementation ideas for the log analyzer and generator |
| ChatGPT | Improving parser resilience, edge-case handling, and project structure |
| ChatGPT | README formatting and technical documentation improvements |
| ChatGPT | Suggestions for operational metrics and analytics presentation |

---

Initially, I asked Gemini to generate a  of a log analyzer and log generator. I then expanded the command for  implementation manually by adding more defensive parsing behavior, operational metrics, stack trace aggregation, and route normalization logic.

I also used ChatGPT for improving the overall structure and making the solution more production-oriented instead of just a basic parser. After implementing changes manually, I repeatedly re-checked and refined parts of the code with AI tools to improve optimization, resilience, and edge-case handling.

I created the Dockerfile and docker-compose setup myself and later used AI tools to review and improve the configuration. One example where I intentionally changed the AI-generated output was the Python runtime version. The initial suggestion used a newer Python 3.11 slim image, but I manually reduced it to Python 3.9 slim because the project does not require newer language features. This keeps the runtime lighter, more stable, and better optimized for the scope of the assignment.

One example where I intentionally changed the AI-generated output was improving the parser’s resilience handling. The initial generated version handled only simple log patterns, but I manually improved support for:
- inconsistent response time units
- missing status codes
- malformed log lines
- stack trace grouping
- hybrid JSON logs

This made the analyzer significantly more resilient against unpredictable production-style telemetry.

---

# 5. Honest Gap

## Question

> What's one thing in your submission that isn't good enough, and what would you do to fix it with another day?

---

## Answer

One area that is not fully production-ready yet is real-time streaming ingestion. Currently, the analyzer processes static log files after they are written instead of continuously consuming logs in real time.

With another day of work, I would improve the system by adding:
- live log tailing support
- streaming ingestion mode
- concurrent parsing workers
- Prometheus metrics export
- optional web dashboard visualization
- gzip-compressed log support

I would also improve percentile calculation efficiency for extremely large datasets by implementing streaming percentile estimation instead of storing all durations in memory for aggregation.