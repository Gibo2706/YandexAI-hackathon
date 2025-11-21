from pathlib import Path
from pydantic import BaseModel, Field


class DataPaths(BaseModel):
    dataset_dir: Path = Field(default=Path("dataset"), description="Root folder with raw Reddit data")
    processed_dir: Path = Field(default=Path("dataset/processed"), description="Folder for filtered/processed files")


class FilterConfig(BaseModel):
    min_chars: int = 40
    min_score: int = 1
    scam_keywords: list[str] = Field(
        default_factory=lambda: [
            "scam",
            "fraud",
            "is this a scam",
            "legit",
            "suspicious",
            "ponzi",
            "mlm",
            "lost my money",
            "phishing",
        ]
    )


class EmbeddingConfig(BaseModel):
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 128


class AppConfig(BaseModel):
    paths: DataPaths = DataPaths()
    filters: FilterConfig = FilterConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()


def get_default_config() -> AppConfig:
    """Return default config; later you can extend this to load from YAML."""

    return AppConfig()
