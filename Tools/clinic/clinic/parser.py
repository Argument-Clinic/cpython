from __future__ import annotations
from types import NoneType
from typing import Protocol, Any, TYPE_CHECKING

from clinic import unspecified
from clinic.converter import CConverter, converters
from clinic.converters import buffer, robuffer, rwbuffer
from clinic.return_converters import CReturnConverter, return_converters
from clinic.block_parser import Block
if TYPE_CHECKING:
    from clinic.clinic_class import Clinic


class Parser(Protocol):
    def __init__(self, clinic: Clinic) -> None: ...
    def parse(self, block: Block) -> None: ...


def _create_parser_namespace() -> dict[str, Any]:
    ns = dict(
        CConverter=CConverter,
        CReturnConverter=CReturnConverter,
        buffer=buffer,
        robuffer=robuffer,
        rwbuffer=rwbuffer,
        unspecified=unspecified,
        NoneType=NoneType,
    )
    for name, converter in converters.items():
        ns[f'{name}_converter'] = converter
    for name, return_converter in return_converters.items():
        ns[f'{name}_return_converter'] = return_converter
    return ns
_BASE_NAMESPACE = _create_parser_namespace()


def create_parser_namespace() -> dict[str, Any]:
    return _BASE_NAMESPACE.copy()
