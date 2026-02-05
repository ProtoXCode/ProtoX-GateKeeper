from protox_gatekeeper.utils import get_version_from_toml


def test_get_version_from_toml():
    version = get_version_from_toml()

    assert isinstance(version, str)
