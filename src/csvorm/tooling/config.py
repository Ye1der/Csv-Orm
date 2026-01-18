from pathlib import Path
import tomllib

class CsvOrmConfig:
  def __init__(self, root: Path):
    self.root = root
    self.models: Path
    self.generated: Path
    self.pythonpath: list[Path]

  @classmethod
  def load(cls, root: Path) -> "CsvOrmConfig":
    config_path = root / ".csvorm.toml"

    if not config_path.exists():
      raise RuntimeError("Missing .csvorm.toml")

    data = tomllib.loads(config_path.read_text())

    cfg = cls(root)
    cfg.models = root / data["project"]["models"]
    cfg.generated = root / data["project"]["generated"]
    cfg.pythonpath = [
      root / p for p in data.get("python", {}).get("pythonpath", [])
    ]

    return cfg
