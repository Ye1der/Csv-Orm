import inspect
import pkgutil
import importlib
from pathlib import Path
from typing import get_type_hints, get_origin, get_args
from enum import Enum

from src.runtime.orm import CsvOrm


MODELS_PACKAGE = "models"

GENERATED_DIR = Path("src/generated")
FILTERS_FILE = GENERATED_DIR / "filters.py"

ORM_STUB = Path("src/runtime/orm.pyi")
QUERY_STUB = Path("src/runtime/query.pyi")


# ---------------------------------------------------------
# Model discovery
# ---------------------------------------------------------

def iter_models():
    package = importlib.import_module(MODELS_PACKAGE)

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{MODELS_PACKAGE}.{module_name}")

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, CsvOrm) and obj is not CsvOrm:
                yield obj


# ---------------------------------------------------------
# Type resolution
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# filters.py
# ---------------------------------------------------------

def generate_filters(models):
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

    GENERATED_DIR.mkdir(exist_ok=True)
    FILTERS_FILE.write_text("".join(lines))


# ---------------------------------------------------------
# orm.pyi
# ---------------------------------------------------------

def generate_orm_stub(models):
    lines = [
        "from typing import Type, TypeVar, overload, Unpack, TYPE_CHECKING\n",
        "from generated.filters import *\n",
        "from database.query import Query\n",
        "\n",
        "if TYPE_CHECKING:\n",
    ]

    for model in models:
        mod = model.__module__
        name = model.__name__
        lines.append(f"    from {mod} import {name}\n")

    lines.append("\nT = TypeVar('T')\n\n")
    lines.append("class CsvOrm:\n")

    for model in models:
        name = model.__name__
        lines.append(
            f"    @classmethod\n"
            f"    @overload\n"
            f"    def where(cls: Type['{name}'], **filters: Unpack[{name}Where]) -> Query['{name}']: ...\n\n"
        )

    ORM_STUB.write_text("".join(lines))


# ---------------------------------------------------------
# query.pyi
# ---------------------------------------------------------

def generate_query_stub(models):
    lines = [
        "from typing import TypeVar, overload, Unpack, TYPE_CHECKING\n",
        "from generated.filters import *\n",
        "\n",
        "if TYPE_CHECKING:\n",
    ]

    for model in models:
        mod = model.__module__
        name = model.__name__
        lines.append(f"    from {mod} import {name}\n")

    lines.append("\nT = TypeVar('T')\n\n")
    lines.append("class Query:\n")

    for model in models:
        name = model.__name__
        lines.append(
            f"    @overload\n"
            f"    def where(self, **filters: Unpack[{name}Where]) -> 'Query[{name}]': ...\n\n"
            f"    @overload\n"
            f"    def update(self, **values: Unpack[{name}Where]) -> int: ...\n\n"
        )

    QUERY_STUB.write_text("".join(lines))


# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------

def generate():
    models = list(iter_models())
    generate_filters(models)
    generate_orm_stub(models)
    generate_query_stub(models)


if __name__ == "__main__":
    generate()
