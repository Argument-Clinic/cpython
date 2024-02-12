import logging
from typing import Final

from .errors import (
    ClinicError,
)
from .formatting import (
    SIG_END_MARKER,
    c_repr,
    docstring_for_c_string,
    format_escape,
    indent_all_lines,
    normalize_snippet,
    pprint_words,
    suffix_all_lines,
    wrap_declarations,
    wrapped_c_string_literal,
)
from .utils import (
    FormatCounterFormatter,
    compute_checksum,
    create_regex,
    write_file,
)


def get_logger(level: int = logging.WARNING) -> logging.Logger:
    fmt = logging.Formatter("%(levelname)s: %(message)s")

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)

    logger = logging.getLogger("clinic")
    logger.addHandler(console)
    return logger


__all__ = [
    # Error handling
    "ClinicError",

    # Formatting helpers
    "SIG_END_MARKER",
    "c_repr",
    "docstring_for_c_string",
    "format_escape",
    "indent_all_lines",
    "normalize_snippet",
    "pprint_words",
    "suffix_all_lines",
    "wrap_declarations",
    "wrapped_c_string_literal",

    # Misc
    "get_logger",

    # Utility functions
    "FormatCounterFormatter",
    "compute_checksum",
    "create_regex",
    "write_file",
]


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
