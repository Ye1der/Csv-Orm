import csv
import os
from pathlib import Path
import subprocess
from typing import Optional, TypeVar, Type, List
import uuid

from src.runtime.query import Query

T = TypeVar('T', bound='CsvOrm')

class CsvOrm:
  id: uuid.UUID

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

  @classmethod
  def check_uniques(cls: Type[T], new_row: dict):
    uniques: list[str] = getattr(cls, "__uniques__")
    objs = cls.all()
    for obj in objs:
      for key in uniques:
        if obj[key] == new_row[key]:
          raise Exception(f"El campo {key} debe ser unico")

  @classmethod
  def all (cls: Type[T]) -> List[T]:
    if not cls.csv_exists():
      return []

    return Query(cls, cls.get_csv()).all()

  @classmethod
  def __create_csv (cls: Type[T]) -> bool:
    if not cls.csv_exists():
      file_csv = cls.get_csv()
      fields = cls.get_attributes()

      # Creamos todas las carpetas de la ruta por si no existen
      Path(file_csv).parent.mkdir(parents=True, exist_ok=True)

      with open(file_csv, mode="a", newline="", encoding="utf-8") as file:
        # Le pasa los header que debe tener el csv en base a los fields de la clase y con eso crea el writer
        csv.DictWriter(file, fieldnames=["id", *fields]).writeheader()

      return True
    return False

  @classmethod
  def where (cls: Type[T], **filters: object) -> Query[T]:
    cls.__create_csv()
    query: Query[T] = Query(cls, cls.get_csv())
    return query.where(**filters)

  @classmethod
  def create(cls: Type[T], obj: Optional[T] = None, **fields_obj: object):
    file_exists = cls.csv_exists()
    file_csv = cls.get_csv()
    fields = cls.get_attributes()

    # Creamos todas las carpetas de la ruta por si no existen
    Path(file_csv).parent.mkdir(parents=True, exist_ok=True)

    # Abrimos o creamos el archivo csv
    with open(file_csv, mode="a", newline="", encoding="utf-8") as file:
      # Le pasa los header que debe tener el csv en base a los fields de la clase y con eso crea el writer
      writer = csv.DictWriter(file, fieldnames=["id", *fields])

      if not file_exists:
        writer.writeheader()

      row: dict[str, object]

      if obj: row = vars(obj)
      else: row = {field: fields_obj[field] or None for field in fields}

      row["id"] = uuid.uuid4()
      cls.check_uniques(row)
      writer.writerow(row)


  def __getitem__(self, key):
    return getattr(self, key)

  def __setitem__(self, key, value):
    setattr(self, key, value)
