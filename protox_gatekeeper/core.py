import logging

import requests
from requests.exceptions import RequestException

from protox_gatekeeper.session import make_tor_session
from protox_gatekeeper.verify import is_tor_exit, get_public_ip
from protox_gatekeeper.ops import download_file as _download
from protox_gatekeeper.geo import geo_lookup

logger = logging.getLogger(__name__)


class GateKeeper:
    def __init__(self, socks_port: int = 9150, geo=False, timeout: int = 10):
        """
        GateKeeper constructor.

        Args:
            socks_port (int, optional): The socks port to use. Defaults to 9150.
            geo (bool, optional): Whether to use geo. Defaults to False.
            timeout (int, optional): The timeout to wait for a response. Defaults to 10.
        """

        self._geo = geo
        self._port = socks_port
        self._timeout = timeout

        self._session: requests.Session
        self.exit_ip: str
        self.clearnet_ip: str

        # 1) Measure clearnet IP (no proxies)
        clearnet = requests.Session()
        self.clearnet_ip = get_public_ip(session=clearnet, timeout=timeout)

        # 2) Create Tor session
        self._session = make_tor_session(port=socks_port)

        # 3) Verify Tor routing
        try:
            if not is_tor_exit(session=self._session, timeout=timeout):
                raise RuntimeError(
                    'Tor verification failed. Execution aborted.')
        except RequestException as e:
            logger.debug('Underlying Tor connection error', exc_info=e)
            raise RuntimeError(
                f'Tor SOCKS proxy is not reachable on 127.0.0.1:{socks_port}. '
                'Start Tor or Tor Browser and try again.'
            ) from None

        # 4) Measure Tor exit IP
        self.exit_ip = get_public_ip(session=self._session, timeout=timeout)

        # 5) Log the transition
        logger.info(f'Tor verified: {self.clearnet_ip} -> {self.exit_ip}')

        # 6) Location data
        if geo:
            location = geo_lookup(self.exit_ip)
            if location:
                logger.info(f'Tor exit location: {location}')
            else:
                logger.info('Tor exit location: Unavailable')

    def __repr__(self) -> str:
        return f'<GateKeeper: {self.clearnet_ip} -> tor_exit: {self.exit_ip}>'

    def __enter__(self) -> "GateKeeper":
        return self

    def __exit__(self, exc_type, exc, tb):
        self._session.close()

    @property
    def session(self) -> requests.Session:
        """ Exposes the verified session if needed. """
        return self._session

    @property
    def tor_exit(self) -> str:
        """ Returns the Tor exit IP address. """
        return self.exit_ip

    # --- Core function ----------------------------------------------------- #

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP request throught the Tor-verified session.

        This is a thin passthrough to ``requests.Session.request`` with enforced
        Tor routing and logging.

        Args:
            method (str): HTTP method (e.g. "GET", "POST", "PUT", "DELETE").
            url (str): The url to request.
            **kwargs: Additional arguments passed directly to
            ``requests.Session.request``.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RuntimeError: If the Tor session is not available or verified.
        """
        logger.info(f'[Tor {self.tor_exit}] {method.upper()} {url}')
        return self._session.request(method=method, url=url, **kwargs)

    # --- Circuit rotation -------------------------------------------------- #

    def rotate(self) -> str:
        """
        Attempt to rotate the Tor exit by renewing the session and re-verifying
    routing.

    This method closes the current Tor session, creates a new one, and
    performs full Tor verification again.

    Important:
        Tor may reuse existing circuits for performance and stability.
        Therefore, calling ``rotate()`` does not guarantee a different
        exit IP address. If the exit remains unchanged, this does not
        indicate failure — it reflects Tor's circuit reuse policy.

    Returns:
        str: The current Tor exit IP address after rotation attempt.

    Raises:
        RuntimeError: If Tor verification fails after session renewal.
        """
        old_exit = self.exit_ip

        logger.info(f'[Tor {old_exit}] rotating session...')

        self._session.close()
        self._session = make_tor_session(port=self._port)

        try:
            if not is_tor_exit(session=self._session, timeout=self._timeout):
                raise RuntimeError(
                    'Tor verification failed after rotation.'
                )
        except RequestException:
            raise RuntimeError(
                f'Tor SOCKS proxy is not reachable on '
                f'127.0.0.1:{self._port}. '
                'Start Tor or Tor Browser and try again.'
            ) from None

        # Measure new exit IP
        self.exit_ip = get_public_ip(
            session=self._session,
            timeout=self._timeout
        )

        if old_exit != self.exit_ip:
            logger.info(f'Tor exit rotated: {old_exit} -> {self.exit_ip}')

            if self._geo:
                location = geo_lookup(self.exit_ip)
                if location:
                    logger.info(f'Tor exit location: {location}')
                else:
                    logger.info('Tor exit location: Unavailable')
        else:
            logger.warning(
                f'Tor exit unchanged after rotation attempt: {self.exit_ip}')

        return self.exit_ip

    # --- Helper functions -------------------------------------------------- #

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Passes a GET request to the Tor Gatekeeper.

        Args:
            url (str): The url to request.
            **kwargs: Additional parameters to pass to the GET request.
        """
        return self.request('GET', url, **kwargs)

    def post(self, url: str, data=None, json=None,
             **kwargs) -> requests.Response:
        """
        Passes a POST request to the Tor Gatekeeper.

        Args:
            url (str): The url to post to.
            data (dict, optional): The data to post.
            json (dict, optional): The json data to post.
            **kwargs: Additional parameters to pass to the POST request.
        """
        return self.request('POST', url, data=data, json=json, **kwargs)

    def put(self, url: str, data=None, json=None,
            **kwargs) -> requests.Response:
        """
        Passes a PUT request to the Tor Gatekeeper.

        Args:
             url (str): The url to put to.
             data (dict, optional): The data to put.
             json (dict, optional): The json data to put.
             **kwargs: Additional parameters to pass to the PUT request.
        """
        return self.request(
            method='PUT', url=url, data=data, json=json, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Passes a DELETE request to the Tor Gatekeeper.

        Args:
            url (str): The url to delete.
            **kwargs: Additional parameters to pass to the DELETE request.
        """
        return self.request(method='DELETE', url=url, **kwargs)

    # --- Custom functions -------------------------------------------------- #

    def download(self, url: str, target_path: str, timeout: int = 30,
                 chunk_size: int = 8192, **kwargs):
        """
        Attempts to download the given url to the target path.

        Args:
            url (str): The url to download.
            target_path (str): The target path.
            timeout (int, optional): The timeout to wait for a response.
            chunk_size (int, optional): The chunk size to use for download.
            **kwargs: Additional parameters to pass to the download request.
        """
        logger.info(
            f'[Tor {self.tor_exit}] downloading {url} -> {target_path}')

        return _download(
            session=self._session,
            url=url,
            target_path=target_path,
            timeout=timeout,
            chunk_size=chunk_size,
            **kwargs
        )
