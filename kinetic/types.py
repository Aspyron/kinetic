"""Kinetic type representations."""

from dataclasses import dataclass
from enum import Enum, auto


class KType(Enum):
    INT = auto()
    STRING = auto()
    BOOL = auto()
    INT_ARRAY = auto()
    VOID = auto()
    UNKNOWN = auto()


@dataclass
class FunctionType:
    parameters: list[KType]
    result: KType
