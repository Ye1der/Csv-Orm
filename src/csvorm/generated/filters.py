from typing import TypedDict, Literal
from enum import Enum
from uuid import UUID

class CarWhere(TypedDict, total=False):
    id: UUID
    marca: str
    velocidad: int
    puertas: int
    precio: int
    placa: str
    color: str

class UserWhere(TypedDict, total=False):
    id: UUID
    cedula: int
    name: str
    age: int

