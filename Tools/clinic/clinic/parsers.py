from __future__ import annotations
import contextlib
import io
from collections.abc import Callable
from typing import TYPE_CHECKING

from clinic.block_parser import Block
from clinic.parser import Parser, create_parser_namespace
from clinic.dslparser import DSLParser
if TYPE_CHECKING:
    from clinic.clinic_class import Clinic



class PythonParser:
    def __init__(self, clinic: Clinic) -> None:
        self.namespace = create_parser_namespace()

    def parse(self, block: Block) -> None:
        ns = dict(self.namespace)
        with contextlib.redirect_stdout(io.StringIO()) as s:
            exec(block.input, ns)
            block.output = s.getvalue()


# maps strings to callables.
# the callable should return an object
# that implements the clinic parser
# interface (__init__ and parse).
#
# example parsers:
#   "clinic", handles the Clinic DSL
#   "python", handles running Python code
#
parsers: dict[str, Callable[[Clinic], Parser]] = {
    'clinic': DSLParser,
    'python': PythonParser,
}
