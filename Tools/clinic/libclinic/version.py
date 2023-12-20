import itertools

from typing import Literal


class ParseVersionError(BaseException):
    pass


def _version_splitter(s: str) -> tuple[int, ...]:
    """Splits a version string into a tuple of integers.

    The following ASCII characters are allowed, and employ
    the following conversions:
        a -> -3
        b -> -2
        c -> -1
    (This permits Python-style version strings such as "1.4b3".)
    """
    version: list[int] = []
    accumulator: list[str] = []
    def flush() -> None:
        if not accumulator:
            raise ParseVersionError(f'Unsupported version string: {s!r}')
        version.append(int(''.join(accumulator)))
        accumulator.clear()

    for c in s:
        if c.isdigit():
            accumulator.append(c)
        elif c == '.':
            flush()
        elif c in 'abc':
            flush()
            version.append('abc'.index(c) - 3)
        else:
            raise ParseVersionError(
                f'Illegal character {c!r} in version string {s!r}'
            )
    flush()
    return tuple(version)


def version_comparator(version1: str, version2: str) -> Literal[-1, 0, 1]:
    iterator = itertools.zip_longest(
        _version_splitter(version1), _version_splitter(version2), fillvalue=0
    )
    for a, b in iterator:
        if a < b:
            return -1
        if a > b:
            return 1
    return 0
