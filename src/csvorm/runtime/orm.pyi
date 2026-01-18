from typing import Type, TypeVar, overload, Unpack, TYPE_CHECKING, Optional
import uuid
from csvorm import Query

T = TypeVar("T")

class CsvOrm:
  id: uuid.UUID

  @classmethod
  def where(cls: Type[T], **filters: object) -> Query[T]: ...

  @classmethod
  def create(cls: Type[T], **fields_obj: object) -> None: ...

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
