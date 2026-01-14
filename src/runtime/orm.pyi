import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Type, TypeVar, overload

if TYPE_CHECKING:
    from src.runtime.query import Query

T = TypeVar("T", bound="CsvOrm")

class CsvOrm:
    id: uuid.UUID

    # Atributos de clase que pueden estar definidos en las subclases
    __uniques__: ClassVar[list[str]]

    @classmethod
    def get_attributes(cls) -> list[str]: ...

    @classmethod
    def get_csv(cls) -> str: ...

    @classmethod
    def csv_exists(cls) -> bool: ...

    @classmethod
    def check_uniques(cls: Type[T], new_row: dict[str, Any]) -> None: ...

    @classmethod
    def all(cls: Type[T]) -> list[T]: ...

    @classmethod
    def __create_csv(cls: Type[T]) -> bool: ...

    @classmethod
    def where(cls: Type[T], **filters: Any) -> "Query[T]": ...

    @overload
    @classmethod
    def create(cls: Type[T], obj: Optional[T] = None) -> None: ...

    @overload
    @classmethod
    def create(cls: Type[T], **fields_obj: Any) -> None: ...

    @classmethod
    def create(cls: Type[T], obj: Optional[T] = None, **fields_obj: Any) -> None: ...

    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...
