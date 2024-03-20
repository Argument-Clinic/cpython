from typing import Final

from .errors import (
    ClinicError,
    warn,
    fail,
)
from .formatting import (
    SIG_END_MARKER,
    c_repr,
    docstring_for_c_string,
    format_escape,
    indent_all_lines,
    linear_format,
    normalize_snippet,
    pprint_words,
    suffix_all_lines,
    wrap_declarations,
    wrapped_c_string_literal,
)
from .identifiers import (
    ensure_legal_c_identifier,
    is_legal_c_identifier,
    is_legal_py_identifier,
)
from .utils import (
    FormatCounterFormatter,
    compute_checksum,
    create_regex,
    write_file,
    VersionTuple,
    Sentinels,
    unspecified,
    unknown,
    Null,
    NULL,
)


CLINIC_PREFIX: Final = "__clinic_"
CLINIC_PREFIXED_ARGS: Final = frozenset(
    {
        "_keywords",
        "_parser",
        "args",
        "argsbuf",
        "fastargs",
        "kwargs",
        "kwnames",
        "nargs",
        "noptargs",
        "return_value",
    }
)


from .option_groups import (
    permute_optional_groups, permute_left_option_groups,
    permute_right_option_groups)
from .clanguage import CLanguage
from .return_converters import int_return_converter
from .block_parser import Block, BlockParser
from .block_printer import BlockPrinter
from .function import Module, Function

from .dslparser import DSLParser
from .clinic_class import Clinic
from .cli import parse_file, main


__all__ = [
    # Error handling
    "ClinicError",
    "warn",
    "fail",

    # Formatting helpers
    "SIG_END_MARKER",
    "c_repr",
    "docstring_for_c_string",
    "format_escape",
    "indent_all_lines",
    "linear_format",
    "normalize_snippet",
    "pprint_words",
    "suffix_all_lines",
    "wrap_declarations",
    "wrapped_c_string_literal",

    # Identifier helpers
    "ensure_legal_c_identifier",
    "is_legal_c_identifier",
    "is_legal_py_identifier",

    # Utility functions
    "FormatCounterFormatter",
    "compute_checksum",
    "create_regex",
    "write_file",
    "VersionTuple",
    "Sentinels",
    "unspecified",
    "unknown",
    "Null",
    "NULL",

    # Others
    "permute_optional_groups",
    "permute_left_option_groups",
    "permute_right_option_groups",
    "CLanguage",
    "int_return_converter",
    "Block",
    "BlockParser",
    "BlockPrinter",
    "Module",
    "Function",
    "DSLParser",
    "Clinic",
    "parse_file",
    "main",
]
