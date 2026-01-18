import sys
import importlib
import pkgutil
import inspect
from pathlib import Path
from typing import Iterable, Type

from csvorm.runtime.orm import CsvOrm

def load_models(models_path: Path, pythonpath: list[Path]) -> Iterable[type[CsvOrm]]:
  for p in pythonpath:
    sys.path.insert(0, str(p))

  if not models_path.exists():
    raise RuntimeError(f"Models path not found: {models_path}")

  package_name = models_path.name

  package = importlib.import_module(package_name)

  for _, module_name, _ in pkgutil.iter_modules(package.__path__):
    module = importlib.import_module(f"{package_name}.{module_name}")

    for _, obj in inspect.getmembers(module, inspect.isclass):
      if issubclass(obj, CsvOrm) and obj is not CsvOrm:
        yield obj
