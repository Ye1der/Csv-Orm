# type: ignore

from typing import TypeVar, overload, Unpack, TYPE_CHECKING, Literal, Generic, Self
from csvorm.generated.filters import CarWhere, UserWhere

if TYPE_CHECKING:
    from models.car import Car
    from models.user import User


T = TypeVar('T', bound=object)

class Query(Generic[T]):

  __model: type[T]
  __path_csv: str
  __limit: int | None
  __offset: int | None
  __order_by: str | None
  __filters: dict[str, object] | None
    
  @overload
  def where(self, **filters: Unpack[CarWhere]) -> 'Query[Car]': ...

  @overload
  def where(self, **filters: Unpack[UserWhere]) -> 'Query[User]': ...

  @overload
  def update(self, **values: Unpack[CarWhere]) -> int: ...

  @overload
  def update(self, **values: Unpack[UserWhere]) -> int: ...

  @overload
  def order_by(self, attribute: Literal["id", "marca", "velocidad", "puertas", "precio", "placa", "color"]) -> 'Query[Car]': ...

  @overload
  def order_by(self, attribute: Literal["id", "cedula", "name", "age"]) -> 'Query[User]': ...


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
      