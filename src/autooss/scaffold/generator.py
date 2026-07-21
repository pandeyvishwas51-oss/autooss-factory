"""Generate a minimal but runnable Python project from an Opportunity."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

from src.autooss.models import Opportunity


def _slug(name: str) -> str:
    s = name.lower().split(":")[0].strip()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def scaffold_opportunity(opp: Opportunity, parent_dir: Path) -> Path:
    slug = _slug(opp.name)
    root = parent_dir / slug
    root.mkdir(parents=True, exist_ok=True)

    pkg = slug.replace("-", "_")
    (root / "src" / pkg).mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "scripts").mkdir(parents=True, exist_ok=True)

    modules = opp.mvp_modules or ["core"]
    module_files = []
    for m in modules:
        safe = re.sub(r"[^a-z0-9_]+", "_", m.lower())
        module_files.append(safe)
        (root / "src" / pkg / f"{safe}.py").write_text(
            f'''"""{opp.name} — {safe} module."""

from __future__ import annotations


def run_{safe}(*args, **kwargs):
    """MVP placeholder for {safe}. Expand in iteration 2."""
    return {{"module": "{safe}", "status": "ok", "project": "{slug}"}}
''',
            encoding="utf-8",
        )

    (root / "src" / pkg / "__init__.py").write_text(
        f'"""{opp.name}: {opp.one_liner}"""\n\n__version__ = "0.1.0"\n',
        encoding="utf-8",
    )

    (root / "src" / pkg / "cli.py").write_text(
        f'''"""CLI entry for {slug}."""

from __future__ import annotations

import json


def main():
    print(json.dumps({{
        "project": "{slug}",
        "name": {json.dumps(opp.name)},
        "one_liner": {json.dumps(opp.one_liner)},
        "modules": {json.dumps(module_files)},
    }}, indent=2))


if __name__ == "__main__":
    main()
''',
        encoding="utf-8",
    )

    (root / "tests" / "test_smoke.py").write_text(
        f'''from src.{pkg} import __version__
from src.{pkg}.cli import main


def test_version():
    assert __version__


def test_cli(capsys):
    main()
    out = capsys.readouterr().out
    assert "{slug}" in out
''',
        encoding="utf-8",
    )

    readme = f"""# {opp.name}

{opp.one_liner}

## Problem

{opp.problem}

## Solution

{opp.solution}

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
python -m src.{pkg}.cli
```

## Modules

{chr(10).join(f"- `{m}`" for m in module_files)}

## Stack

{', '.join(opp.tech_stack) or 'Python'}

## License

MIT
"""
    (root / "README.md").write_text(readme, encoding="utf-8")

    (root / "pyproject.toml").write_text(
        f'''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{slug}"
version = "0.1.0"
description = {json.dumps(opp.one_liner)}
readme = "README.md"
requires-python = ">=3.11"
license = {{ text = "MIT" }}
dependencies = ["pydantic>=2.6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
''',
        encoding="utf-8",
    )

    (root / "LICENSE").write_text(
        "MIT License\n\nCopyright (c) 2026 pandeyvishwas51-oss\n",
        encoding="utf-8",
    )
    (root / ".gitignore").write_text(
        ".venv/\n__pycache__/\n.env\n.pytest_cache/\n*.egg-info/\n",
        encoding="utf-8",
    )
    (root / "docs" / "OPPORTUNITY.json").write_text(
        opp.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (root / "scripts" / "verify.py").write_text(
        f'''#!/usr/bin/env python3
import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"])
sys.exit(r.returncode)
''',
        encoding="utf-8",
    )

    return root
