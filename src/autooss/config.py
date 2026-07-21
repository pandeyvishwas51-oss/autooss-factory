from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = "pandeyvishwas51-oss"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    HN_TOP_N: int = 30
    GITHUB_SEARCH_QUERIES: str = (
        "web scraping,RAG pipeline,LLM extraction,anti-bot,browser fingerprint,"
        "vector search,structured extraction"
    )
    MAX_OPPORTUNITIES: int = 10
    SCAFFOLD_TOP_N: int = 1
    AUTO_PUSH: bool = False
    WORKSPACE_ROOT: str = ""

    @property
    def workspace(self) -> Path:
        if self.WORKSPACE_ROOT:
            return Path(self.WORKSPACE_ROOT)
        return Path.home() / "autooss-workspace"

    @property
    def factory_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def data_dir(self) -> Path:
        d = self.factory_root / "data"
        d.mkdir(parents=True, exist_ok=True)
        return d


settings = Settings()
