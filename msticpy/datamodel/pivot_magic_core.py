# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Txt2df core code."""
import argparse
import io

import pandas as pd
from pandas.errors import ParserError

from .._version import VERSION

__version__ = VERSION
__author__ = "Ian Hellen"


def _add_parser_args():
    parser = argparse.ArgumentParser(
        description="Cell magic to convert cell text to pandas DataFrame",
        prog="%%txt2df",
    )
    parser.add_argument(
        "--sep",
        "-s",
        default=",",
        required=False,
        help="Column separator/delimiter to use.",
    )
    parser.add_argument(
        "--name",
        "-n",
        default=None,
        required=False,
        help="If specified, the DataFrame will be assigned to the named variable.",
    )
    parser.add_argument(
        "--headers",
        "-e",
        action="store_true",
        default=False,
        help="If supplied, the first line is treated as the header row.",
    )
    parser.add_argument(
        "--keepna",
        "-k",
        action="store_true",
        default=False,
        help=(
            "Don't drop columns that are all NA (the default is to drop"
            + " them, which is useful for data with trailing delimiters.)"
        ),
    )
    return parser


def run_txt2df(line, cell, local_ns) -> pd.DataFrame:
    """Convert cell text to pandas DataFrame."""
    arg_parser = _add_parser_args()
    try:
        line_args = line.split(" ") if line else []
        args = arg_parser.parse_args(line_args)
    except argparse.ArgumentError as err:
        raise AttributeError(
            "Invalid argument supplied.", "Use --help to see valid arguments."
        ) from err

    cell_text = io.StringIO(cell)
    try:
        parsed_df = pd.read_csv(
            cell_text,
            header=0 if args.headers else None,
            prefix=None if args.headers else "column_",
            sep=args.sep,
            skipinitialspace=True,
            warn_bad_lines=True,
            skip_blank_lines=True,
        )
    except ParserError:
        # try again without headers
        cell_text = io.StringIO(cell)
        parsed_df = pd.read_csv(
            cell_text,
            sep=args.sep,
            skipinitialspace=True,
            warn_bad_lines=True,
            skip_blank_lines=True,
            error_bad_lines=False,
        )
        print(
            "One or more rows had more columns than specified in first row.",
            "Ignoring header row.",
        )
    if not args.keepna:
        parsed_df = parsed_df.dropna(axis=1, how="all")
    if local_ns is not None and args.name:
        local_ns[args.name] = parsed_df
    return parsed_df
