from __future__ import annotations

import requests

from tor.session import make_tor_session
from tor.verify import get_public_ip, is_tor_exit, get_actual_public_ip
from utils.logger import logger

IP = get_actual_public_ip()


def get_verified_tor_session() -> requests.Session:
    """
    Returns a requests.Session that MUST be routed through Tor.
    Raises RuntimeError if Tor is not working.
    """
    session = make_tor_session()

    if not is_tor_exit(session):
        raise RuntimeError(
            "Tor check failed. Either Tor isn't running, "
            "the SOCKS port is wrong, or traffic isn't exiting via Tor.")

    return session


def main():
    logger.info('GateKeeper boot: Acquiring Tor-verified session...')

    try:
        session = get_verified_tor_session()
    except Exception as e:
        logger.error(f'GateKeeper blocked execution: {e}')
        return

    exit_ip = get_public_ip(session)

    if IP == exit_ip:
        raise RuntimeError(f'GateKeeper blocked execution. '
                           f'Original IP: {IP} <-> Exit IP{exit_ip}')

    logger.info(f'Tor verified - Original IP: {IP} -> Exit IP: {exit_ip}')

    r = session.get('https://httpbin.org/ip', timeout=10)
    logger.info(f'Test request OK: {r.text.strip()}')

    logger.info('Phase 1 complete: Working Tor session acquired.')


if __name__ == '__main__':
    main()
