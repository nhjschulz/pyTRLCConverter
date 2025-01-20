"""Project specific Markdown converter functions.

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
from pyTRLCConverter.ret import Ret

# Variables ********************************************************************
_source_items = []
_out_path = ""
_is_table_active = False

# Classes **********************************************************************

# Functions ********************************************************************

def _set_table_active(value):
    """Sets the table active flag to the given value.

    Args:
        value (bool): If the table is active, set to True, otherwise False.
    """
    global _is_table_active # pylint: disable=global-statement
    _is_table_active = value

def _print_req_table_head(fd):
    """Prints the table head for requirements.

    Args:
        fd (file): File descriptor
    """
    result = "\n"
    column_headings = ["ID", "Description"]

    for idx, heading in enumerate(column_headings):
        if 0 < idx:
            result += " "

        result += f"| {heading}"

    result += " |\n"

    for idx, heading in enumerate(column_headings):
        if 0 < idx:
            result += " "

        result += "| "

        for _ in range(len(heading)):
            result += "-"

    result += " |\n"

    fd.write(result)

def _print_req(fd, req):
    """Prints the requirement.

    Args:
        fd (file): File descriptor
        req (Record_Object): Requirement to print
    """
    req_id = req.name
    sys_req_attributes = req.to_python_dict()
    description = sys_req_attributes["description"]

    fd.write(f"| {req_id} ")
    fd.write(f"| {description} |\n")

def init(sources, out_path):
    """Initializes the Markdown converter.

    Args:
        sources (list): List of source paths
        out_path (str): Output path
    """
    global _source_items, _out_path # pylint: disable=global-statement
    _source_items = sources
    _out_path = out_path

    _set_table_active(False)

def convert_section(fd, section, level):
    """Converts a section to Markdown format.

    Args:
        fd (file): File descriptor
        section (dict): Section to convert
        level (int): Current level of the section
    """
    if _is_table_active is True:
        fd.write("\n")
        _set_table_active(False)

    fd.write(f"{'#' * (level + 1)} {section}\n")

    return Ret.OK

# pylint: disable=unused-argument
def convert_record_object(fd, record_object, level):
    """Converts a record object to Markdown format.

    Args:
        fd (file): File descriptor
        record_object (Record_Object): Record object to convert
        level (int): Current level of the record object
    """

    if record_object.n_typ.name == "Requirement":
        # System requirements are printed in a table.
        if _is_table_active is False:
            _print_req_table_head(fd)
            _set_table_active(True)

        _print_req(fd, record_object)

    else:
        # Skipped.
        pass

    return Ret.OK

# Main *************************************************************************
