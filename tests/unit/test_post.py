from unittest.mock import MagicMock

from protox_gatekeeper import GateKeeper


def test_post_calls_session(monkeypatch):
    gk = GateKeeper.__new__(GateKeeper)
    gk.exit_ip = '1.2.3.4'

    gk.request = MagicMock()

    payload = {'a': 1}

    gk.post(
        'https://example.com',
        json=payload,
        timeout=10
    )

    gk.request.assert_called_once_with(
        'POST',
        'https://example.com',
        data=None,
        json=payload,
        timeout=10
    )
