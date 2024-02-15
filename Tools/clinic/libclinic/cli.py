"""Parse arguments passed to the code generator for parsing arguments passed."""

import argparse
import inspect
import os
import re
import sys
from typing import NoReturn
from collections.abc import Callable

import libclinic
from libclinic import clinic, ClinicError
from libclinic.clinic import (
    BlockParser,
    Clinic,
    CLanguage,
    Language,
    PythonLanguage,
)

__all__ = ["main", "parse_file"]


# match '#define Py_LIMITED_API'
LIMITED_CAPI_REGEX = re.compile(r'#define +Py_LIMITED_API')


# "extensions" maps the file extension ("c", "py") to Language classes.
LangDict = dict[str, Callable[[str], Language]]
extensions: LangDict = { name: CLanguage for name in "c cc cpp cxx h hh hpp hxx".split() }
extensions['py'] = PythonLanguage


def create_cli() -> argparse.ArgumentParser:
    cmdline = argparse.ArgumentParser(
        description="""Preprocessor for CPython C files.

The purpose of the Argument Clinic is automating all the boilerplate involved
with writing argument parsing code for builtins and providing introspection
signatures ("docstrings") for CPython builtins.

For more information see https://devguide.python.org/development-tools/clinic/""",
    )
    cmdline.add_argument(
        "-f", "--force", action="store_true", help="force output regeneration"
    )
    cmdline.add_argument(
        "-o", "--output", type=str, help="redirect file output to OUTPUT"
    )
    cmdline.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose mode"
    )
    cmdline.add_argument(
        "--converters",
        action="store_true",
        help=("print a list of all supported converters " "and return converters"),
    )
    cmdline.add_argument(
        "--make",
        action="store_true",
        help="walk --srcdir to run over all relevant files",
    )
    cmdline.add_argument(
        "--srcdir",
        type=str,
        default=os.curdir,
        help="the directory tree to walk in --make mode",
    )
    cmdline.add_argument(
        "--exclude",
        type=str,
        action="append",
        help=("a file to exclude in --make mode; " "can be given multiple times"),
    )
    cmdline.add_argument(
        "--limited",
        dest="limited_capi",
        action="store_true",
        help="use the Limited C API",
    )
    cmdline.add_argument(
        "filename",
        metavar="FILE",
        type=str,
        nargs="*",
        help="the list of files to process",
    )
    return cmdline


def parse_file(
        filename: str,
        *,
        limited_capi: bool,
        output: str | None = None,
        verify: bool = True,
) -> None:
    if not output:
        output = filename

    extension = os.path.splitext(filename)[1][1:]
    if not extension:
        raise ClinicError(f"Can't extract file type for file {filename!r}")

    try:
        language = extensions[extension](filename)
    except KeyError:
        raise ClinicError(f"Can't identify file type for file {filename!r}")

    with open(filename, encoding="utf-8") as f:
        raw = f.read()

    # exit quickly if there are no clinic markers in the file
    find_start_re = BlockParser("", language).find_start_re
    if not find_start_re.search(raw):
        return

    if LIMITED_CAPI_REGEX.search(raw):
        limited_capi = True

    assert isinstance(language, CLanguage)
    clinic = Clinic(language,
                    verify=verify,
                    filename=filename,
                    limited_capi=limited_capi)
    cooked = clinic.parse(raw)

    libclinic.write_file(output, cooked)


def run_clinic(parser: argparse.ArgumentParser, ns: argparse.Namespace) -> None:
    if ns.converters:
        if ns.filename:
            parser.error("can't specify --converters and a filename at the same time")
        converters: list[tuple[str, str]] = []
        return_converters: list[tuple[str, str]] = []
        ignored = set(
            """
            add_c_converter
            add_c_return_converter
            add_default_legacy_c_converter
            add_legacy_c_converter
            """.strip().split()
        )

        module = vars(clinic)
        for name in module:
            for suffix, ids in (
                ("_return_converter", return_converters),
                ("_converter", converters),
            ):
                if name in ignored:
                    continue
                if name.endswith(suffix):
                    ids.append((name, name.removesuffix(suffix)))
                    break
        print()

        print("Legacy converters:")
        legacy = sorted(clinic.legacy_converters)
        print("    " + " ".join(c for c in legacy if c[0].isupper()))
        print("    " + " ".join(c for c in legacy if c[0].islower()))
        print()

        for title, attribute, ids in (
            ("Converters", "converter_init", converters),
            ("Return converters", "return_converter_init", return_converters),
        ):
            print(title + ":")
            longest = -1
            for name, short_name in ids:
                longest = max(longest, len(short_name))
            for name, short_name in sorted(ids, key=lambda x: x[1].lower()):
                cls = module[name]
                callable = getattr(cls, attribute, None)
                if not callable:
                    continue
                signature = inspect.signature(callable)
                parameters = []
                for parameter_name, parameter in signature.parameters.items():
                    if parameter.kind == inspect.Parameter.KEYWORD_ONLY:
                        if parameter.default != inspect.Parameter.empty:
                            s = f"{parameter_name}={parameter.default!r}"
                        else:
                            s = parameter_name
                        parameters.append(s)
                print("    {}({})".format(short_name, ", ".join(parameters)))
            print()
        print(
            "All converters also accept (c_default=None, py_default=None, annotation=None)."
        )
        print("All return converters also accept (py_default=None).")
        return

    if ns.make:
        if ns.output or ns.filename:
            parser.error("can't use -o or filenames with --make")
        if not ns.srcdir:
            parser.error("--srcdir must not be empty with --make")
        if ns.exclude:
            excludes = [os.path.join(ns.srcdir, f) for f in ns.exclude]
            excludes = [os.path.normpath(f) for f in excludes]
        else:
            excludes = []
        for root, dirs, files in os.walk(ns.srcdir):
            for rcs_dir in (".svn", ".git", ".hg", "build", "externals"):
                if rcs_dir in dirs:
                    dirs.remove(rcs_dir)
            for filename in files:
                # handle .c, .cpp and .h files
                if not filename.endswith((".c", ".cpp", ".h")):
                    continue
                path = os.path.join(root, filename)
                path = os.path.normpath(path)
                if path in excludes:
                    continue
                if ns.verbose:
                    print(path)
                parse_file(path, verify=not ns.force, limited_capi=ns.limited_capi)
        return

    if not ns.filename:
        parser.error("no input files")

    if ns.output and len(ns.filename) > 1:
        parser.error("can't use -o with multiple filenames")

    for filename in ns.filename:
        if ns.verbose:
            print(filename)
        parse_file(
            filename,
            output=ns.output,
            verify=not ns.force,
            limited_capi=ns.limited_capi,
        )


def main(argv: list[str] | None = None) -> NoReturn:
    parser = create_cli()
    args = parser.parse_args(argv)
    try:
        run_clinic(parser, args)
    except ClinicError as exc:
        sys.stderr.write(exc.report())
        sys.exit(1)
    else:
        sys.exit(0)
