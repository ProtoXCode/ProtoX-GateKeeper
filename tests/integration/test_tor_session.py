import pytest

from protox_gatekeeper import GateKeeper


@pytest.mark.integration
def test_tor_exit_differs_from_clearnet():
    gk = GateKeeper()
    assert gk.clearnet_ip != gk.tor_exit
