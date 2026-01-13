from typing import Generic, TypeVar, Self

T = TypeVar('T', bound=object)

# Methods
# where
# limit
# offset
# order_by

# all
# first
# one
# exists
# count
# update
# delete

class Query(Generic[T]):
  __limit: int
  __offset: int
  __order_by: str
  __filters: dict[str, object]

  def where (self, **filters: object) -> Self:
    self.__filters = filters
    return self

  def limit (self, num: int) -> Self:
    self.__limit = num
    return self

  def offset (self, num) -> Self:
    self.__offset = num
    return self

  def order_by(self, attribute: str ) -> Self:
    self.__order_by = attribute
    return self

  def all(self) -> list[T]:

    return []
