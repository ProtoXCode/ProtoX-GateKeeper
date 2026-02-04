from protox_gatekeeper import GateKeeper


def test_request_passthrought(monkeypatch):
    called = {}

    class DummySession:
        def request(self, method, url, **kwargs):
            called['method'] = method
            called['url'] = url
            called['kwargs'] = kwargs
            return 'ok'

    gk = GateKeeper.__new__(GateKeeper)
    gk._session = DummySession()
    gk.exit_ip = '1.2.3.4'

    result = gk.request('PUT', 'https://example.com', timeout=5)

    assert result == 'ok'
    assert called['method'] == 'PUT'
    assert called['url'] == 'https://example.com'
    assert called['kwargs']['timeout'] == 5
