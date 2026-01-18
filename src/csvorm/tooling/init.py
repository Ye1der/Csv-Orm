from pathlib import Path

def init_config (root: Path):
  models_dir = root / "models"
  models_dir.mkdir(parents=True, exist_ok=True)

  csvorm_config = root / ".csvorm.toml"

  csvorm_config.write_text(
"""[project]
models = "models"
generated = ".csvorm/generated"

[python]
pythonpath = ["."]""", encoding="utf-8")
