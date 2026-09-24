"""A measurement row becomes an observation, then a factor."""
from platforms.cabinetfield.src.application.derate import issue_derate
from platforms.cabinetfield.src.application.ingest import MissingField, observation_from_row


def test_row_becomes_observation_then_derate():
    obs = observation_from_row(
        {
            "cabinet_id": "cab-7",
            "cluster_id": "cluster-a",
            "observed_at": "2026-09-13T23:00:00Z",
            "f_plus_mhz": 2872.0,
            "f_minus_mhz": 2868.0,
            "temp_c": 55.0,
            "fault_class": "oil_pump",
            "severity": "warning",
        }
    )
    derate = issue_derate(obs, None)
    assert derate.factor == 0.85
    assert obs.cabinet_id == "cab-7"


def test_missing_field_refused():
    try:
        observation_from_row({"cabinet_id": "cab-7"})
        assert False
    except MissingField:
        pass
