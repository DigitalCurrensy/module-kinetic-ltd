"""The cabinet factor shrinks the group before the power check."""
from platforms.unitcommit.src.application.from_clusters import clusters_from_flex
from platforms.loadclear.src.application.cluster import FlexibleCluster


class _D:
    def __init__(self, cluster_id, factor):
        self.cluster_id = cluster_id
        self.factor = factor


def test_flex_becomes_shrunk_cluster():
    flex = FlexibleCluster(
        "site-s1", pmin_mw=0.0, pmax_mw=0.04, c_nl=10.0, c_su=5.0, mut_steps=1, initial_on=1
    )
    clusters = clusters_from_flex([flex], [_D("site-s1", 0.70)])
    assert len(clusters) == 1
    assert abs(clusters[0].pmax_mw - 0.028) < 1e-9
    assert clusters[0].initial_on == 1


def test_zero_factor_forces_initial_off():
    flex = FlexibleCluster(
        "site-s1", pmin_mw=0.0, pmax_mw=0.04, c_nl=10.0, c_su=5.0, mut_steps=1, initial_on=1
    )
    clusters = clusters_from_flex([flex], [_D("site-s1", 0.0)])
    assert clusters[0].pmax_mw == 0.0
    assert clusters[0].initial_on == 0
