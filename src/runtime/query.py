import csv
from typing import TYPE_CHECKING, Generic, Type, TypeVar, Self
import uuid

T = TypeVar('T', bound=object)

if TYPE_CHECKING:
  from src.runtime.orm import CsvOrm
  T = TypeVar('T', bound=CsvOrm)

class Query(Generic[T]):
  __limit: int
  __offset: int
  __order_by: str
  __filters: dict[str, object]
  __path_csv: str

  def __init__(self, model: Type[T], path_csv: str):
    self.__model = model
    self.__path_csv = path_csv

  def __method_order_by (self):
    pass

  def __method_filter_where (self):
    pass

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

  def get_all(self) -> list[T]:
    with open(self.__path_csv, mode="r", encoding="utf-8") as file:
      reader = csv.DictReader(file)
      objs = []

      for row in reader:
        id = row.pop("id")
        obj = self.__model(**row)
        obj.id = uuid.UUID(id)
        objs.append(obj)

      return objs

  def set_filters(self) -> list[T]:
    rows = self.get_all()
    filtered_rows = []

    if hasattr(self, "_Query__filters") and len(self.__filters) > 0:
      attributes_filter = self.__filters.keys()
      for row in rows:
        for attr in attributes_filter:
          if row[attr] == self.__filters[attr]:
            filtered_rows.append(row)
    else: filtered_rows = rows

    if hasattr(self, "_Query__offset"): filtered_rows = filtered_rows[self.__offset:]
    if hasattr(self, "_Query__limit"): filtered_rows = filtered_rows[:self.__limit]

    # Aplicar ordenamiento si existe
    if hasattr(self, '_Query__order_by') and self.__order_by:
      # Verificar si el atributo existe en la clase
      model_attributes = self.__model.get_attributes() if hasattr(self.__model, 'get_attributes') else []

      if self.__order_by in model_attributes:
        try:
          # Ordenar por el atributo especificado
          filtered_rows = sorted(filtered_rows, key=lambda x: getattr(x, self.__order_by))
        except (TypeError, AttributeError):
          # Si hay error al ordenar (tipos incompatibles), no ordenar
          pass

    return filtered_rows

  def all(self) -> list[T]:
    return self.set_filters()

  def first(self) -> T | None:
    rows = self.set_filters()
    if len(rows) > 0: return rows[0]
    else: return None

  def exists(self) -> bool:
    rows = self.set_filters()
    if len(rows) > 0: return True
    else: return False

  def count(self) -> int:
    return len(self.set_filters())

  def delete(self) -> int:
    rows = self.get_all()
    rows_filtered = self.set_filters()

    ids_to_detele = [row["id"] for row in rows_filtered]
    rows = list(filter(lambda x: x["id"] not in ids_to_detele ,rows))
    rows = [vars(row) for row in rows]

    fields = ["id", *self.__model.get_attributes()]
    with open(self.__path_csv, mode="w", newline="", encoding="utf-8") as file:
      writer = csv.DictWriter(file, fieldnames=fields)
      writer.writeheader()
      writer.writerows(rows)

    return len(rows_filtered)

  def update(self, **updates: object) -> int:
    if not updates:
      raise ValueError("No se proporcionaron campos para actualizar")

    rows = self.get_all()
    rows_filtered = self.set_filters()
    rows_afected = len(rows_filtered)

    if rows_afected == 0: return 0

    # ids_to_update = [row["id"] for row in rows_filtered]
    rows_updated = []

    for row in rows_filtered:
      for key, value in updates.items():
        row[key] = value
      rows_updated.append(row)

    dict_rows_updated: dict[str, object] = {row["id"]:row for row in rows_updated}
    rows = [dict_rows_updated.get(row["id"], row) for row in rows]

    fields = ["id", *self.__model.get_attributes()]
    with open(self.__path_csv, mode="w", newline="", encoding="utf-8") as file:
      writer = csv.DictWriter(file, fieldnames=fields)
      writer.writeheader()
      writer.writerows([vars(row) for row in rows])

    return rows_afected
