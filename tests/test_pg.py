import os

from desk import pg
from desk.drain import DrainRow
from desk.pg import DatabaseUrlMissing, connect, database_url, drain_live

SEVEN = (
    "work_order",
    "enrollment",
    "derate",
    "time_pin",
    "wrap",
    "commitment_run",
    "signed_meter",
)


class _Cursor:
    def __init__(self, conn: "_Conn") -> None:
        self._conn = conn
        self.rowcount = 0

    def execute(self, sql: str, params=None) -> None:
        text = sql.upper()
        if "DROP " in text or "TRUNCATE" in text:
            raise AssertionError("forbidden sql reached the wire")
        if "CREATE_HYPERTABLE" in text or "ADD_COMPRESSION_POLICY" in text or "ADD_RETENTION_POLICY" in text:
            raise RuntimeError("timescale missing")
        if "INSERT" in text:
            key = (params[0], params[1])
            if key in self._conn.seen:
                self.rowcount = 0
            else:
                self._conn.seen.add(key)
                self._conn.rows.append(params)
                self.rowcount = 1
            return
        self.rowcount = 0


class _Conn:
    def __init__(self) -> None:
        self.seen: set[tuple] = set()
        self.rows: list = []
        self.rollbacks = 0

    def cursor(self) -> _Cursor:
        return _Cursor(self)

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        pass


def _seven() -> list[DrainRow]:
    tenant = "11111111-1111-4111-8111-111111111111"
    return [
        DrainRow(
            tenant_id=tenant,
            event_id=f"evt-{kind}",
            kind=kind,  # type: ignore[arg-type]
            observed_at="2026-09-15T19:00:00Z",
            payload={"kind": kind},
        )
        for kind in SEVEN
    ]


def test_unset_url_writes_zero():
    os.environ.pop("DATABASE_URL", None)
    assert database_url() is None
    assert drain_live([]) == 0
    try:
        connect()
        assert False
    except DatabaseUrlMissing:
        pass


def test_dsn_path_writes_seven_then_zero():
    conn = _Conn()
    original = pg.connect
    os.environ["DATABASE_URL"] = "postgres://desk-test"
    try:
        pg.connect = lambda url=None: conn  # type: ignore[assignment]
        rows = _seven()
        assert drain_live(rows) == 7
        assert drain_live(rows) == 0
        assert len(conn.rows) == 7
        assert conn.rollbacks >= 2
    finally:
        pg.connect = original
        os.environ.pop("DATABASE_URL", None)
