from __future__ import annotations

import requests


def get_public_ip(session: requests.Session, timeout: int = 10) -> str:
    r = session.get('https://api.ipify.org/', timeout=timeout)
    r.raise_for_status()
    return r.text.strip()


def get_actual_public_ip(session: requests.Session | None = None) -> str:
    s = session or requests.Session()
    return s.get('https://api.ipify.org', timeout=10).text


def is_tor_exit(session: requests.Session, timeout: int = 10) -> bool:
    r = session.get('https://check.torproject.org/api/ip', timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return bool(data.get('IsTor', False))
