# NetCheck

NetCheck is a Python-based automated network performance checker built around the Module 13 activity sheet. It automates the manual `ping` exercise and the `latency_test.py` example, then adds health checks, continuous monitoring, a local web dashboard, and JSON/CSV/HTML reports.

## Features

- Open a local Flask dashboard with ping, health-check, and monitor modes.
- Watch live latency, packet loss, jitter, status, and per-probe charts while a test runs.
- Ping one or many targets with configurable count, timeout, interval, and payload size.
- Measure packet loss, minimum/average/maximum RTT, jitter, standard deviation, and success rate.
- Run layered health checks: DNS resolution, default gateway, ICMP reachability, TCP 443, and Wi-Fi RSSI.
- Monitor continuously for a fixed duration and keep a running summary.
- Write timestamped JSON, CSV, and self-contained HTML reports.
- Use the Windows `ping` command by default; optionally use Scapy if it is installed and raw sockets are available.
- Keep the command-line interface for scripting and quick checks.

## Requirements

- Windows 10/11, Linux, or macOS
- Python 3.10 or newer (tested on Python 3.14)
- Flask 3.0 or newer for the web dashboard
- No administrator privileges required for the default engine
- Optional: Scapy + Npcap + an elevated terminal for raw ICMP

Install the dashboard dependency:

```powershell
python -m pip install -r requirements.txt
```

## Quick start

```powershell
cd C:\Users\Client\netcheck-system
python main.py
```

`python main.py` starts the local dashboard at `http://127.0.0.1:5000/` and opens it in your browser. If port 5000 is busy, NetCheck tries the next available port. The server binds to localhost only.

You can also launch the dashboard directly or without opening a browser:

```powershell
python main.py ui
python main.py ui --no-browser --port 5055
```

On Windows, double-click `NetCheck.pyw` for a console-free launch.

The CLI is still available:

```powershell
python main.py --help
python main.py ping google.com
python main.py ping google.com 1.1.1.1 --count 3 --interval 0.5
python main.py check
python main.py monitor --duration 30 --interval 2
python main.py menu
```

Reports are written to `results\<timestamp>\`:

- `summary.json` - complete structured result
- `targets.csv` - one row per target
- `probes.csv` - one row per ping probe
- `report.html` - printable report with charts and recommendations

## Dashboard

The dashboard has three modes:

- **Ping** - send a fixed number of probes to each target and chart each RTT.
- **Health Check** - run gateway, DNS, ICMP, TCP, and optional Wi-Fi checks.
- **Monitor** - sample every interval for a chosen duration and update the running summary.

The setup panel edits targets, probe settings, timeout, payload size, TCP port, Wi-Fi/TCP toggles, and the ping engine. Results update by polling the local API every 700 ms. One test runs at a time; the Stop button cancels ping and monitor jobs. Each completed test exposes an **Open report** link.

The dashboard is intentionally local-only and keeps recent runs in memory for the current server session. Reports remain on disk under `results/`.

### Local API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/status` | Host, Wi-Fi, gateway, active job, recent runs |
| `GET` | `/api/config` | Active configuration |
| `GET` | `/api/jobs` | Recent job summaries |
| `GET` | `/api/jobs/<id>` | Live job detail and results |
| `POST` | `/api/ping` | Start a ping job |
| `POST` | `/api/check` | Start a health-check job |
| `POST` | `/api/monitor` | Start a monitor job |
| `POST` | `/api/jobs/<id>/cancel` | Request cancellation |
| `GET` | `/api/jobs/<id>/report` | Open the generated HTML report |

Example:

```powershell
$body = @{ targets = @("google.com", "1.1.1.1"); count = 3; interval_s = 0.5 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/ping -ContentType application/json -Body $body
```

## Commands

### Ping

```powershell
python main.py ping [targets...] [--count N] [--timeout MS] [--interval S] [--size BYTES] [--engine auto|system|scapy] [--report-dir PATH] [--no-report] [--json]
```

Examples:

```powershell
python main.py ping 127.0.0.1 --count 3
python main.py ping google.com --count 10 --interval 0.5 --size 64
python main.py ping 8.8.8.8 --json --no-report
```

### Check

```powershell
python main.py check [targets...] [--no-wifi] [--no-tcp] [--port PORT] [--report-dir PATH] [--no-report] [--json]
```

`check` adds the default gateway to the ping set, resolves hostnames, runs TCP reachability checks, and reads Wi-Fi signal data from `netsh wlan show interfaces` on Windows.

### Monitor

```powershell
python main.py monitor [targets...] [--duration S] [--interval S] [--timeout MS] [--size BYTES] [--engine ENGINE] [--no-report] [--json]
```

Press `Ctrl+C` to stop early. The final report covers every probe collected during the run.

### Interactive menu

```powershell
python main.py menu
```

The menu offers ping, health checks, continuous monitoring, and opening the results folder.

### Dashboard options

```powershell
python main.py ui [--config PATH] [--host localhost|127.0.0.1] [--port PORT] [--no-browser]
```

## Configuration

Edit `config.json` to change defaults:

```json
{
  "targets": ["google.com", "1.1.1.1", "8.8.8.8"],
  "count": 5,
  "timeout_ms": 1000,
  "interval_s": 1.0,
  "payload_bytes": 32,
  "engine": "auto",
  "thresholds": {
    "latency_ms": 150.0,
    "loss_pct": 5.0,
    "jitter_ms": 30.0
  },
  "tcp_check": {
    "enabled": true,
    "port": 443,
    "timeout_s": 3.0
  },
  "wifi": {
    "enabled": true,
    "rssi_warn_dbm": -75
  },
  "monitor": {
    "duration_s": 30,
    "interval_s": 2.0
  },
  "report_dir": "results",
  "ui": {
    "host": "127.0.0.1",
    "port": 5000,
    "open_browser": true
  }
}
```

CLI flags override the configuration file. Use `python main.py --config other.json ping ...` or `python main.py ui --config other.json` to load a different file.

## Metrics and thresholds

- **Latency** - round-trip time in milliseconds; average above `latency_ms` produces a warning.
- **Packet loss** - `(sent - received) / sent * 100`; above `loss_pct` produces a failure.
- **Jitter** - mean absolute difference between consecutive RTT samples; above `jitter_ms` produces a warning.
- **Standard deviation** - RTT variability for the run.
- **Success rate** - percentage of probes that received a reply.

Exit codes: `0` pass/skip, `1` warning, `2` failure, `3` usage or configuration error.

## How this maps to the Module 13 SAS

| SAS activity | NetCheck feature |
| --- | --- |
| Manual `ping google.com` | `python main.py ping google.com` or dashboard Ping mode |
| Observe performance information | RTT, loss, jitter, min/avg/max, success rate |
| `latency_test.py` loop of five probes | `--count 5`, dashboard probe count, per-probe chart |
| Run longer | `--count`, dashboard Monitor mode, `monitor --duration` |
| Test a different target | Target field, positional targets, or `config.json` |
| Collect more performance data | JSON/CSV/HTML reports with every probe |
| Standard automated testing workflow | config, traffic generation, execution, probe capture, analysis, report |
| Wireless signal strength automation | `check` and dashboard Health Check read SSID, signal %, RSSI, rates |
| Cloud/endpoint checks | ping and TCP checks against configurable public endpoints |

## Scapy engine

Phase 1 works without Scapy. To try raw ICMP:

```powershell
python -m pip install scapy
```

On Windows, Scapy also needs Npcap and an elevated terminal. If Scapy is missing, cannot import, or cannot open a raw socket, NetCheck falls back to the operating system ping command and records the reason in the report.

## Limitations

- The dashboard binds to localhost only and has no authentication because it is a local tool.
- Job history is held in memory and resets when the dashboard server stops; report files remain on disk.
- Only one dashboard test runs at a time. Starting a second test returns HTTP 409.
- ICMP may be blocked by a campus network, firewall, or target host. The TCP 443 check provides a fallback signal, but it is not a substitute for ICMP.
- The default engine parses `ping` output. NetCheck handles common English and localized numeric formats, but unusual output can produce a missing RTT.
- Wi-Fi metrics are read from Windows `netsh`; Linux and macOS return a skipped Wi-Fi check.
- True cloud multi-region, SDN flow-rule, and VM-to-VM tests need lab infrastructure and are planned as Phase 2 modules.
- This tool performs reachability and performance checks only. It does not scan ports or test vulnerabilities.

## Tests

```powershell
python -m unittest discover -s tests -v
```

The test suite covers metric calculations, ping-output parsing, Wi-Fi parsing, HTML report rendering, job execution/cancellation, and dashboard API routes without requiring network access.

## Project layout

```text
netcheck-system/
  main.py
  NetCheck.pyw
  config.json
  requirements.txt
  README.md
  netcheck/
    __init__.py
    cli.py
    config.py
    ping.py
    metrics.py
    checks.py
    wireless.py
    report.py
    jobs.py
    webui.py
    templates/
      index.html
    static/
      app.css
      app.js
  tests/
  results/
```
