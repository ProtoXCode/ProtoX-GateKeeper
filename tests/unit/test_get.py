from unittest.mock import MagicMock

from protox_gatekeeper import GateKeeper


def test_get_delegates_to_request(monkeypatch):
    gk = GateKeeper.__new__(GateKeeper)
    gk.exit_ip = '1.2.3.4'

    gk.request = MagicMock()

    gk.get(url='https://example.com', timeout=5)

    gk.request.assert_called_once_with(
        'GET',
        'https://example.com',
        timeout=5
    )
