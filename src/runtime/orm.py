import csv
from dataclasses import field
import os
import subprocess
from typing import Generic, Optional, TypeVar, Type, List
import uuid

from src.runtime.query import Query

T = TypeVar('T', bound='CsvOrm')

class CsvOrm:
  __id: uuid.UUID

  # Obtiene los nombres de los atributos de la clase -> ["edad", "nombre"]
  @classmethod
  def get_attributes (cls) -> list[str]:
    return list(cls.__annotations__.keys())

  # Obtiene la ruta del csv de esa clase -> "data/students.csv"
  @classmethod
  def get_csv (cls) -> str:
    root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode('utf-8').strip()
    return f"{root}/data/{cls.__name__.lower()}.csv"

  # Verifica si la clase ya tiene un archivo csv creado -> ture/false
  @classmethod
  def csv_exists (cls):
    return os.path.exists(cls.get_csv())

  def check_uniques (self):
    uniques: list[str] = self["__uniques__"]
    objs = self.get_all()

    for obj in objs:
      for key in uniques:
        if obj[key] == self[key]: raise Exception(f"El campo {key} debe ser unico")

  # Guarda los datos que tiene la clase como un nuevo registro en el csv
  def save (self):
    file_exists = self.csv_exists()
    file_csv = self.get_csv()
    fields = self.get_attributes()

    with open(file_csv, mode="a", newline="", encoding="utf-8") as file:
      # Le pasa los header que debe tener el csv en base a los fields de la clase y con eso crea el writer
      writer = csv.DictWriter(file, fieldnames=["id", *fields])

      if not file_exists:
        # Si el csv no habia sido creado antes, se crean los headers del mismo
        writer.writeheader()

      self.check_uniques()

      self.__id = uuid.uuid4()
      obj = {field: getattr(self, field) for field in fields}
      obj["id"] = self.__id
      writer.writerow(obj)

  # Actualiza un registro del csv por medio de su id
  def update(self, filter_field: str, filter_value):
    objs = self.get_all()
    fields = self.get_attributes()
    file_csv = self.get_csv()
    rows: list[dict] = []

    for obj in objs:
      if obj[filter_field] == filter_value:
        # El campo field es dinamico, no se esta creando un objeto con un campo llamado "fiedl"
        rows.append({field: getattr(self, field) or getattr(obj, field) for field in fields})
      else: rows.append(vars(obj))

    with open(file_csv, mode="w", newline="", encoding="utf-8") as file:
      writer = csv.DictWriter(file, fieldnames=fields)
      writer.writeheader()
      writer.writerows(rows)

  def drop(self, filter_field: str, filter_value):
    objs = self.get_all()
    fields = self.get_attributes()
    file_csv = self.get_csv()
    rows: list[dict] = []

    for obj in objs:
      if obj[filter_field] == filter_value: continue
      else: rows.append(vars(obj))

    with open(file_csv, mode="w", newline="", encoding="utf-8") as file:
      writer = csv.DictWriter(file, fieldnames=fields)
      writer.writeheader()
      writer.writerows(rows)

  @classmethod
  def get_all (cls: Type[T]) -> List[T]:
    if not cls.csv_exists():
      return []

    file_csv = cls.get_csv()
    with open(file_csv, mode="r", encoding="utf-8") as file:
      reader = csv.DictReader(file)
      objs = []

      for row in reader:
        id = row.pop("id")
        obj = cls(**row)
        obj.__id = uuid.UUID(id)
        objs.append(obj)
        print("id:", obj.__id)

      return objs

  @classmethod
  def where (cls: Type[T], **filters: object) -> Query[T]:
    query: Query[T] = Query()
    return query.where(**filters)

  def find_by (self, **fields):
    results = []

    for obj in self.get_all():
      if all(str(getattr(obj, k)) == str(v) for k, v in fields.items()):
        results.append(obj)

    return results

  def __getitem__(self, key):
    return getattr(self, key)
