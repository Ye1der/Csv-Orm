from dataclasses import dataclass
from src.runtime.orm import CsvOrm

@dataclass
class Car (CsvOrm):
  marca: str
  velocidad: int
  puertas: int
  precio: int
  placa: str
  color: str

  __uniques__ = ["placa"]
