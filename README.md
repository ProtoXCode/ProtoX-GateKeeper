# ProtoX GateKeeper

ProtoX GateKeeper is a small, focused Python project that enforces **fail-closed Tor routing** for HTTP(S) traffic.

The goal is intentionally narrow and strict:

> Obtain a `requests.Session` that is **provably routed through the Tor network**,
> or abort execution immediately.

There is no silent fallback and no best-effort behavior. Either Tor is active and verified, or nothing runs.

---

## Phase 1 – Status

**Phase 1 is complete.**

At this stage, GateKeeper can:

- Create a `requests.Session` routed through a local Tor SOCKS proxy
- Verify that traffic exits via the Tor network
- Compare and log clearnet IP vs Tor exit IP
- Fail hard if Tor is unavailable or misconfigured

Phase 1 deliberately avoids:

- Tor circuit inspection
- ControlPort interaction
- Identity rotation (NEWNYM)
- Geo‑location or visualization

Those features are intentionally deferred to later phases.

---

## Requirements

- Python 3.10 or newer
- Tor running locally
  - Tor Browser (default SOCKS port: `9150`)
  - or Tor service (commonly `9050`)

Python dependencies:

```
requests
pysocks
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Project

Ensure Tor is fully started and connected before running the script.

```bash
python main.py
```

Example output:

```
GateKeeper boot: Acquiring Tor-verified session...
Tor verified - Original IP: 89.xxx.xxx.xxx -> Exit IP: 185.xxx.xxx.xxx
Test request OK: { "origin": "185.xxx.xxx.xxx" }
Phase 1 complete: Working Tor session acquired.
```

If Tor is not reachable or verification fails, execution stops immediately.

---

## Design Principles

- **Fail‑closed by default** – no Tor, no execution
- **No silent fallback** – clearnet traffic is never allowed accidentally
- **Explicit verification** – Tor exit is confirmed via Tor Project infrastructure
- **Observable behavior** – IP transition is logged and visible
- **Minimal scope** – Phase 1 does exactly one thing, correctly

---

## Intended Use

ProtoX GateKeeper is designed as a foundational **enforcement primitive**:

- Educational exploration of proxy enforcement and verification
- A reusable guard layer for privacy‑aware tooling
- A building block for more advanced Tor‑aware systems

It is not designed to bypass laws, policies, or service terms.

---

## License

This project is licensed under the MIT License.
See the `LICENSE` file for details.

