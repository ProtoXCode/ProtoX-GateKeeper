import logging

import requests

from protox_gatekeeper.utils import get_version_from_toml

logger = logging.getLogger(__name__)

VERSION = get_version_from_toml()

def geo_lookup(ip: str) -> str | None:
    """ Tries to lookup geolocation for a given IP address of the Tor exit """
    try:
        r = requests.get(
            url=f'https://ipapi.co/{ip}/json',
            timeout=10,
            headers={'User-Agent': f'GateKeeper/{VERSION}'},
        )
        if r.status_code != 200:
            return None

        data = r.json()
        city = data.get('city')
        country = data.get('country')
        if city and country:
            return f'{city}, {country}'

    except Exception as e:
        logger.info(f'Unable to get geolocation for {ip}: {e}')
        return None
