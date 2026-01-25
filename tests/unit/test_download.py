import requests

from protox_gatekeeper.ops import download_file


class DummyResponse:
    status_code = 200

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size=8192):
        yield b'hello '
        yield b'world'


def test_download_write_file(tmp_path, monkeypatch):
    session = requests.Session()

    def fake_get(url, stream=True, timeout=None):
        return DummyResponse()

    monkeypatch.setattr(session, 'get', fake_get)

    target = tmp_path / 'out.bin'

    download_file(
        session=session,
        url='http://example.com/file',
        target_path=str(target),
        timeout=10,
        chunk_size=4
    )

    assert target.exists()
    assert target.read_bytes() == b'hello world'
