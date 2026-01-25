from protox_gatekeeper import GateKeeper


class DummySession:
    def get(self, url, **kwargs):
        self.called = True
        self.url = url
        self.kwargs = kwargs
        return 'ok'


def test_get_calls_session(monkeypatch):
    gk = GateKeeper.__new__(GateKeeper)
    gk.exit_ip = '1.2.3.4'
    gk._session = DummySession()

    resp = gk.get(url='http://example.com', timeout=5)

    assert resp == 'ok'
    assert gk._session.called
    assert gk._session.url == 'http://example.com'
    assert gk._session.kwargs['timeout'] == 5
