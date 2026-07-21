from src.autooss.content.blogger import (
    PORTFOLIO,
    build_pack,
    generate_nightly_posts,
    strip_em_dashes,
)


def test_strip_em_dashes():
    assert "\u2014" not in strip_em_dashes("hello \u2014 world")
    assert " - " in strip_em_dashes("hello \u2014 world")


def test_one_pack_per_project_no_emdash():
    assert len(PORTFOLIO) >= 1
    for p in PORTFOLIO:
        pack = build_pack(p)
        blob = pack.medium_body + pack.x_post + "".join(pack.x_thread)
        assert "\u2014" not in blob
        assert "\u2013" not in blob
        assert p.github in pack.medium_body
        assert p.github in pack.x_post


def test_generate_writes_files(tmp_path):
    out = generate_nightly_posts(out_dir=tmp_path / "day")
    assert (out / "INDEX.md").exists()
    assert (out / "COPY_PASTE_ALL.md").exists()
    # one folder per project
    dirs = [d for d in out.iterdir() if d.is_dir()]
    assert len(dirs) == len(PORTFOLIO)
    sample = dirs[0]
    assert (sample / "MEDIUM.md").exists()
    assert (sample / "X_POST.txt").exists()
