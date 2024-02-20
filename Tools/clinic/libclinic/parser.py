import re
from typing import NamedTuple
try:
    from .errors import ParseError
except ImportError:
    class ParseError(Exception):
        pass


class Token(NamedTuple):
    kind: str
    value: str


def tokenize(line: str):
    token_specification = [
        ("ARROW",      r"->"),           # Arrow operator
        ("CLONE",      r"="),            # Clone clause
        ("ARGS",       r"\(.*\)"),       # Converter args
        ("WORD",       r"[\w.]+"),       # Possibly dotted word
        ("SPACE",      r"[ ]+"),         # Space
        ("MISMATCH",   r"."),            # Any other character
    ]
    regex = "|".join(
        [f"(?P<{kind}>{spec})" for kind, spec in token_specification]
    )
    for mo in re.finditer(regex, line):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "SPACE":
            continue
        elif kind == "MISMATCH":
            raise ParseError(f"{value!r} stray character in input")
        yield Token(kind, value)


def print_tokens(line):
    for token in tokenize(line):
        print(token)


def parse_file(path):
    with open(path) as f:
        for line in f.readlines():
            print_tokens(line)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        for line in sys.stdin.readlines():
            print_tokens(line)
    else:
        for path in sys.argv[1:]:
            parse_file(path)
