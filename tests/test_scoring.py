from src.autooss.discovery.collect import SEED_OPPORTUNITIES, collect_all_signals
from src.autooss.scoring.opportunities import signals_to_opportunities
from src.autooss.scaffold.generator import scaffold_opportunity
from src.autooss.models import Opportunity
from pathlib import Path


def test_seeds_produce_opportunities():
    opps = signals_to_opportunities(SEED_OPPORTUNITIES, max_n=10)
    assert len(opps) >= 3
    assert opps[0].total_score >= opps[-1].total_score


def test_scaffold(tmp_path):
    opp = Opportunity(
        id="x",
        name="TestProj",
        one_liner="test",
        problem="p",
        solution="s",
        mvp_modules=["core", "cli"],
        tech_stack=["python"],
        total_score=0.9,
    )
    root = scaffold_opportunity(opp, tmp_path)
    assert (root / "README.md").exists()
    assert (root / "tests" / "test_smoke.py").exists()


def test_collect_offline_seeds():
    # collect always includes seeds even if network fails
    sigs = collect_all_signals()
    assert any(s.source == "seed" for s in sigs)
