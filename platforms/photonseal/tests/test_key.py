"""An empty key and the test key k are refused."""
from platforms.photonseal.src.application.key import MissingKey, signing_key_from_env
from platforms.photonseal.src.application.meter import seal_interval, verify_interval


def test_env_key_seals_and_verifies():
    key = signing_key_from_env({"PHOTONSEAL_KEY": "cabinet-secret"})
    interval = seal_interval(
        meter_id="m-1",
        interval_start="2026-09-13T23:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        time_source="csac",
        signing_key=key,
    )
    assert verify_interval(interval, key) is True
    assert verify_interval(interval, "k") is False


def test_empty_and_literal_k_refused():
    try:
        signing_key_from_env({})
        assert False
    except MissingKey:
        pass
    try:
        signing_key_from_env({"PHOTONSEAL_KEY": "k"})
        assert False
    except MissingKey:
        pass
