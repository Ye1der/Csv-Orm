# type: ignore

from typing import Type, TypeVar, overload, Unpack, TYPE_CHECKING, Optional
import uuid
from csvorm.generated.filters import  CarWhere, UserWhere
from csvorm import Query
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.car import Car
    from models.user import User


T = TypeVar("T")

class CsvOrm:
  id: uuid.UUID

  @classmethod
  @overload
  def where(cls: Type["Car"], **filters: Unpack[CarWhere]) -> Query["Car"]: ...

  @classmethod
  @overload
  def where(cls: Type["User"], **filters: Unpack[UserWhere]) -> Query["User"]: ...

  @classmethod
  @overload
  def create(cls: Type["Car"], obj: Optional["Car"] = None) -> None: ...

  @classmethod
  @overload
  def create(cls: Type["Car"], **fields_obj: Unpack[CarWhere]) -> None: ...
  @classmethod
  @overload
  def create(cls: Type["User"], obj: Optional["User"] = None) -> None: ...

  @classmethod
  @overload
  def create(cls: Type["User"], **fields_obj: Unpack[UserWhere]) -> None: ...

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
