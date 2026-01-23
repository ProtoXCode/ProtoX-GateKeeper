from __future__ import annotations

import requests

PORT = 9150
DEFAULT_TOR_SOCKS = f'socks5h://127.0.0.1:{PORT}'


def make_tor_session(socks_url: str = DEFAULT_TOR_SOCKS) -> requests.Session:
    s = requests.Session()
    s.proxies = {
        'http': socks_url,
        'https': socks_url,
    }
    return s
