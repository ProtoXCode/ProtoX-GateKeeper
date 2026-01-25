from protox_gatekeeper import GateKeeper


class DummySession:
    def post(self, url, data=None, json=None, **kwargs):
        self.called = True
        self.url = url
        self.data = data
        self.json = json
        self.kwargs = kwargs
        return 'ok'


def test_post_calls_session(monkeypatch):
    gk = GateKeeper.__new__(GateKeeper)
    gk.exit_ip = '1.2.3.4'
    gk._session = DummySession()

    resp = gk.post(
        'http://example.com/api',
        json={'a': 1},
        timeout=5,
        headers={'X-Test': 'yes'},
    )

    assert resp == 'ok'
    assert gk._session.called
    assert gk._session.url == 'http://example.com/api'
    assert gk._session.json == {'a': 1}
    assert gk._session.kwargs['timeout'] == 5
    assert gk._session.kwargs['headers']['X-Test'] == 'yes'
