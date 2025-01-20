"""The main module with the program entry point.
    The main task is to convert requirements, diagrams and etc. which are defined
    by TRLC into markdown format.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
# Copyright (c) 2024 - 2025 NewTec GmbH
#
# This file is part of pyTRLCConverter program.
#
# The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# The pyTRLCConverter program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyTRLCConverter.
# If not, see <https://www.gnu.org/licenses/>.

# Imports **********************************************************************
import sys
import argparse
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.version import __license__, __repository__, __version__
from pyTRLCConverter.trlc_helper import get_trlc_symbols
from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.log_verbose import enable_verbose, log_verbose, is_verbose_enabled

# Variables ********************************************************************

PROG_NAME = "pyTrlcConverter"
PROG_DESC = "A CLI tool to convert TRLC into different formats."
PROG_COPYRIGHT = "Copyright (c) 2024 - 2025 NewTec GmbH - " + __license__
PROG_GITHUB = "Find the project on GitHub: " + __repository__
PROG_EPILOG = PROG_COPYRIGHT + " - " + PROG_GITHUB

CONVERTER_TABLE = {
    "Markdown": MarkdownConverter()
}

# Classes **********************************************************************

# Functions ********************************************************************

def _create_args_parser() -> argparse.ArgumentParser:
    """ Creater parser for command line arguments.

    Returns:
        argparse.ArgumentParser:  The parser object for command line arguments.
    """
    parser = argparse.ArgumentParser(prog=PROG_NAME,
                                     description=PROG_DESC,
                                     epilog=PROG_EPILOG)

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print full command details before executing the command." \
                "Enables logs of type INFO and WARNING."
    )

    parser.add_argument(
        "-i",
        "--include",
        type=str,
        default=None,
        required=False,
        action="append",
        help="Add additional directory which to include on demand. Can be specified several times."
    )

    parser.add_argument(
        "-s",
        "--source",
        type=str,
        required=True,
        action="append",
        help="The path to the TRLC files folder or a single TRLC file."
    )

    parser.add_argument(
        "-ex",
        "--exclude",
        type=str,
        default=None,
        required=False,
        action="append",
        help="Add source directory which shall not be considered for conversion. Can be specified several times."
    )

    return parser

def main():
    """Main program entry point.

    Returns:
        int: Program status
    """
    ret_status = Ret.OK

    # Handle program arguments.
    args_parser = _create_args_parser()
    args_sub_parser = args_parser.add_subparsers(required='True')

    for _, converter in CONVERTER_TABLE.items():
        converter.register(args_sub_parser)

    args = args_parser.parse_args()

    if args is None:
        ret_status = Ret.ERROR

    else:
        enable_verbose(args.verbose)

        # In verbose mode print all program arguments.
        if is_verbose_enabled() is True:
            log_verbose("Program arguments: ")

            for arg in vars(args):
                log_verbose(f"* {arg} = {vars(args)[arg]}")
            log_verbose("\n")

        symbols = get_trlc_symbols(args.source, args.include)

        if symbols is None:
            print(f"No items found at {args.source}.")
            ret_status = Ret.ERROR
        else:
            try:
                ret_status = args.func(args, symbols)
            except FileNotFoundError as exc:
                print(exc)
                ret_status = Ret.ERROR

    return ret_status

# Main *************************************************************************

if __name__ == "__main__":
    sys.exit(main())
