from dataclasses import dataclass
from csvorm import CsvOrm

@dataclass
class User (CsvOrm):
  cedula: int
  name: str
  age: int

  __uniques__ = ["cedula"]
