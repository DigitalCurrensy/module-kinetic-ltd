import os

from desk.pg import DatabaseUrlMissing, connect, database_url, drain_live


def test_unset_url_writes_zero():
    os.environ.pop("DATABASE_URL", None)
    assert database_url() is None
    assert drain_live([]) == 0
    try:
        connect()
        assert False
    except DatabaseUrlMissing:
        pass
