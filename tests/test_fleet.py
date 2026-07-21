from src.autooss.fleet.catalog import default_catalog
from src.autooss.fleet.operator import load_test_url


def test_catalog_has_core_repos():
    names = {r.name for r in default_catalog()}
    assert "schemaweaver" in names
    assert "sentinelscrape" in names or "autooss-factory" in names


def test_load_test_skips_dead_service():
    # nothing on high port → skip style result, should not raise
    r = load_test_url("http://127.0.0.1:59999/health", requests_n=5, concurrency=2)
    assert r.requests == 5
    assert r.note in ("service_down_skipped", "no_success", "ok")
