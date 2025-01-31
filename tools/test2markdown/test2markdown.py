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
from pyTRLCConverter.markdown_converter import markdown_create_heading, markdown_create_table_head, \
    markdown_append_table_row

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

def _print_sw_test_case_table_head(fd):
    """Prints the table head for software test cases.

    Args:
        fd (file): File descriptor
    """
    column_titles = ["ID", "Description", "Derived"]
    markdown_table_head = markdown_create_table_head(column_titles)

    fd.write(markdown_table_head)

def _print_sw_test_case(fd, sw_test_case):
    """Prints the software test case.

    Args:
        fd (file): File descriptor
        sw_test_case (Record_Object): Software test case to print
    """
    sw_test_case_id = sw_test_case.name
    sw_test_case_attributes = sw_test_case.to_python_dict()
    description = sw_test_case_attributes["description"]
    derived = sw_test_case_attributes["derived"]
    derived_info = "N/A"

    if derived is not None:
        derived_info = ""
        for idx, derived_req in enumerate(derived):
            if 0 < idx:
                derived_info += ", "

            derived_info += derived_req

    row_values = [sw_test_case_id, description, derived_info]
    markdown_table_row = markdown_append_table_row(row_values)
    fd.write(markdown_table_row)

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

    markdown_text = markdown_create_heading(section, level + 1)
    fd.write(markdown_text)

    return Ret.OK

# pylint: disable=unused-argument
def convert_record_object(fd, record_object, level):
    """Converts a record object to Markdown format.

    Args:
        fd (file): File descriptor
        record_object (Record_Object): Record object to convert
        level (int): Current level of the record object
    """

    if record_object.n_typ.name == "SwTestCase":
        # Sofware requirements are printed in a table.
        if _is_table_active is False:
            _print_sw_test_case_table_head(fd)
            _set_table_active(True)

        _print_sw_test_case(fd, record_object)

    else:
        # Skipped.
        pass

    return Ret.OK

# Main *************************************************************************
