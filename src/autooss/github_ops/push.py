"""Create GitHub repo and push local project (requires gh + token)."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional

from src.autooss.config import settings

logger = logging.getLogger(__name__)


def _run(cmd: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )


def init_and_push(
    project_dir: Path,
    repo_name: str,
    description: str,
    *,
    public: bool = True,
    owner: Optional[str] = None,
) -> str:
    """
    git init + commit + gh repo create --push.
    Returns repo URL or empty string on failure.
    """
    owner = owner or settings.GITHUB_OWNER
    project_dir = project_dir.resolve()

    if not (project_dir / ".git").exists():
        _run(["git", "init", "-b", "main"], cwd=project_dir)

    _run(["git", "add", "-A"], cwd=project_dir)
    status = _run(["git", "status", "--porcelain"], cwd=project_dir)
    if status.stdout.strip():
        commit = _run(
            [
                "git",
                "-c",
                "user.name=pandeyvishwas51-oss",
                "-c",
                "user.email=pandeyvishwas51@users.noreply.github.com",
                "commit",
                "-m",
                f"Initial release: {repo_name}",
            ],
            cwd=project_dir,
        )
        if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr):
            logger.error("commit failed: %s", commit.stderr)
            return ""

    # already has remote?
    remote = _run(["git", "remote", "get-url", "origin"], cwd=project_dir)
    if remote.returncode == 0:
        push = _run(["git", "push", "-u", "origin", "main"], cwd=project_dir)
        if push.returncode == 0:
            return f"https://github.com/{owner}/{repo_name}"
        logger.error("push failed: %s", push.stderr)
        return ""

    visibility = "--public" if public else "--private"
    create = _run(
        [
            "gh",
            "repo",
            "create",
            f"{owner}/{repo_name}",
            visibility,
            "--description",
            description[:350],
            "--source=.",
            "--remote=origin",
            "--push",
        ],
        cwd=project_dir,
    )
    if create.returncode != 0:
        # maybe exists
        logger.warning("gh create: %s %s", create.stdout, create.stderr)
        _run(
            [
                "git",
                "remote",
                "add",
                "origin",
                f"https://github.com/{owner}/{repo_name}.git",
            ],
            cwd=project_dir,
        )
        push = _run(["git", "push", "-u", "origin", "main"], cwd=project_dir)
        if push.returncode != 0:
            logger.error("push existing failed: %s", push.stderr)
            return ""
    return f"https://github.com/{owner}/{repo_name}"
