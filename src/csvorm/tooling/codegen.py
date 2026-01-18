import inspect
import os
import pkgutil
import importlib
from pathlib import Path
from typing import get_type_hints, get_origin, get_args
from enum import Enum

from csvorm.runtime.orm import CsvOrm
from csvorm.tooling.config import CsvOrmConfig
from csvorm.tooling.model_loader import load_models

MODELS_PACKAGE = "models"

GENERATED_DIR = Path("src/csvorm/generated")
FILTERS_FILE = GENERATED_DIR / "filters.py"

ORM_STUB = Path("src/csvorm/runtime/orm.pyi")
QUERY_STUB = Path("src/csvorm/runtime/query.pyi")


def iter_models():
  package = importlib.import_module(MODELS_PACKAGE)

  for _, module_name, _ in pkgutil.iter_modules(package.__path__):
    module = importlib.import_module(f"{MODELS_PACKAGE}.{module_name}")

    for _, obj in inspect.getmembers(module, inspect.isclass):
      if issubclass(obj, CsvOrm) and obj is not CsvOrm:
        yield obj

def resolve_type(tp) -> str:
  origin = get_origin(tp)
  args = get_args(tp)

  if origin is None:
    if inspect.isclass(tp) and issubclass(tp, Enum):
      return tp.__name__
    return tp.__name__

  if origin is list:
    return f"list[{resolve_type(args[0])}]"

  if origin is dict:
    return f"dict[{resolve_type(args[0])}, {resolve_type(args[1])}]"

  if origin is tuple:
    return f"tuple[{', '.join(resolve_type(a) for a in args)}]"

  if origin is type(None):
    return "None"

  # Optional / Union
  if origin is getattr(__import__('typing'), 'Union'):
    return " | ".join(resolve_type(a) for a in args)

  # Literal
  if origin is getattr(__import__('typing'), 'Literal'):
    return f"Literal[{', '.join(repr(a) for a in args)}]"

  return "Any"

def generate_filters(models, out_dir: Path):
  file = out_dir / "filters.py"

  lines = [
    "from typing import TypedDict, Literal\n",
    "from enum import Enum\n",
    "from uuid import UUID\n",
    "\n",
  ]

  for model in models:
    name = model.__name__
    hints = get_type_hints(model)

    lines.append(f"class {name}Where(TypedDict, total=False):\n")
    for field, tp in hints.items():
      lines.append(f"    {field}: {resolve_type(tp)}\n")
    lines.append("\n")

  file.write_text("".join(lines))


def generate_orm_stub(models, out_dir: Path):
  file = out_dir / "orm.pyi"

  import_lines = []
  type_checking_lines = []

  for model in models:
    name = model.__name__
    mod = model.__module__
    import_lines.append(f"{name}Where")
    type_checking_lines.append(f"    from {mod} import {name}\n")

  import_lines_str = ", ".join(import_lines)

  lines = [
    "# type: ignore\n\n",
    "from typing import Type, TypeVar, overload, Unpack, TYPE_CHECKING, Optional\n",
    "import uuid\n"
    f"from csvorm.generated.filters import  {import_lines_str}\n",
    "from csvorm import Query\n",
    "from typing import TYPE_CHECKING\n",
    "\n",
    "if TYPE_CHECKING:\n",
  ]

  lines.extend(type_checking_lines)
  lines.extend([
    "\n",
    "\n",
    "T = TypeVar(\"T\")\n",
    "\n",
    "class CsvOrm:\n",
    "  id: uuid.UUID\n\n"
  ])

  for model in models:
    name = model.__name__
    lines.extend([
      f"  @classmethod\n",
      f"  @overload\n",
      f"  def where(cls: Type[\"{name}\"], **filters: Unpack[{name}Where]) -> Query[\"{name}\"]: ...\n",
      "\n",
    ])

  for model in models:
    name = model.__name__
    lines.extend([
      f"  @classmethod\n",
      f"  @overload\n",
      f"  def create(cls: Type[\"{name}\"], obj: Optional[\"{name}\"] = None) -> None: ...\n",
      "\n",
      f"  @classmethod\n",
      f"  @overload\n",
      f"  def create(cls: Type[\"{name}\"], **fields_obj: Unpack[{name}Where]) -> None: ...\n",
    ])

  lines.extend ([
"""
  @classmethod
  def get_attributes(cls) -> list[str]: ...

  @classmethod
  def get_csv(cls) -> str: ...

  @classmethod
  def csv_exists(cls) -> bool: ...

  @classmethod
  def check_uniques(cls: Type[T], new_row: dict[str, object]) -> None: ...

  @classmethod
  def all(cls: Type[T]) -> list[T]: ...

  @classmethod
  def __create_csv(cls: Type[T]) -> bool: ...

  def __getitem__(self, key: str) -> object: ...

  def __setitem__(self, key: str, value: object) -> None: ...
"""
    ])

  file.write_text("".join(lines))


def generate_query_stub(models, out_dir: Path):
  file = out_dir / "query.pyi"

  # Generar importaciones dinámicas
  import_lines = []
  type_checking_lines = []

  for model in models:
    name = model.__name__
    mod = model.__module__
    import_lines.append(f"{name}Where")
    type_checking_lines.append(f"    from {mod} import {name}\n")

  import_lines_str = ", ".join(import_lines)

  lines = [
    "# type: ignore\n\n",
    "from typing import TypeVar, overload, Unpack, TYPE_CHECKING, Literal, Generic, Self\n",
    f"from csvorm.generated.filters import {import_lines_str}\n",
    "\n",
    "if TYPE_CHECKING:\n",
  ]

  lines.extend(type_checking_lines)
  lines.extend([
    "\n",
    "\n",
    "T = TypeVar('T', bound=object)\n",
    "\n",
    "class Query(Generic[T]):\n",
    """
  __model: type[T]
  __path_csv: str
  __limit: int | None
  __offset: int | None
  __order_by: str | None
  __filters: dict[str, object] | None
    """,
    "\n"
  ])

  for model in models:
    name = model.__name__
    lines.extend([
      f"  @overload\n",
      f"  def where(self, **filters: Unpack[{name}Where]) -> 'Query[{name}]': ...\n",
      "\n",
    ])

  for model in models:
    name = model.__name__
    lines.extend([
      f"  @overload\n",
      f"  def update(self, **values: Unpack[{name}Where]) -> int: ...\n",
      "\n",
    ])

  for model in models:
    name = model.__name__
    hints = get_type_hints(model)
    attributes = list(hints.keys())

    if attributes:
      literal_values = ", ".join([f"\"{attr}\"" for attr in attributes])
      lines.extend([
        f"  @overload\n",
        f"  def order_by(self, attribute: Literal[{literal_values}]) -> 'Query[{name}]': ...\n",
        "\n",
      ])

  lines.extend([
      """
  def __init__(self, model: type[T], path_csv: str) -> None: ...

  def limit(self, num: int) -> Self: ...

  def offset(self, num: int) -> Self: ...

  def get_all(self) -> list[T]: ...

  def set_filters(self) -> list[T]: ...

  def all(self) -> list[T]: ...

  def first(self) -> T | None: ...

  def exists(self) -> bool: ...

  def count(self) -> int: ...

  def delete(self) -> int: ...
      """
    ])

  file.write_text("".join(lines))

def generate(project_root: Path):
  print("Generating types...")

  config = CsvOrmConfig.load(project_root)

  models = list(
    load_models(
      models_path=config.models,
      pythonpath=config.pythonpath
    )
  )

  path = os.path.abspath(__file__)
  father = os.path.dirname(path)
  grandfather = os.path.dirname(father)

  dir_pyis = Path(grandfather) / "runtime"
  dir_generated = Path(grandfather) / "generated"

  generate_filters(models, dir_generated)
  generate_orm_stub(models, dir_pyis)
  generate_query_stub(models, dir_pyis)

  print("Type generated.")

if __name__ == "__main__":
    generate(Path.cwd())
