from typing import TypedDict, Literal
from enum import Enum
from uuid import UUID

class CarWhere(TypedDict, total=False):
    _CsvOrm__id: UUID
    marca: str
    velocidad: int
    puertas: int
    precio: int
    placa: str
    color: str

