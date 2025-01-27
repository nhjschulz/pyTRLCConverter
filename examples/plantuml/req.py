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
import os
import shutil
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.plantuml import PlantUML
from pyTRLCConverter.markdown_converter import markdown_create_heading, markdown_create_table_head, \
    markdown_append_table_row, markdown_create_diagram_link

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
    column_titles = ["ID", "Description"]
    markdown_table_head = markdown_create_table_head(column_titles)

    fd.write(markdown_table_head)

def _print_req(fd, req):
    """Prints the requirement.

    Args:
        fd (file): File descriptor
        req (Record_Object): Requirement to print
    """
    req_id = req.name
    req_attributes = req.to_python_dict()
    description = req_attributes["description"]

    row_values = [req_id, description, description]
    markdown_table_row = markdown_append_table_row(row_values)
    fd.write(markdown_table_row)

def _print_diagram(fd, diagram):
    """Prints the diagram.

    Args:
        fd (file): File descriptor
        out_path (str): Output path
        diagram (Record_Object): Diagram to print
    """
    plantuml_generator = PlantUML()
    image_format = "png"
    diagram_dict = diagram.to_python_dict()
    file_path = diagram_dict["file_path"]
    caption = diagram_dict["caption"]
    full_file_path = file_path
    file_dst_path = None

    # Is the path to the diagram invalid?
    if os.path.isfile(full_file_path) is False:

        # Maybe the path is relative to one of the source paths.
        for src_item in _source_items:
            if os.path.isdir(src_item):
                full_file_path = os.path.join(src_item, file_path)

                if os.path.isfile(full_file_path) is False:
                    full_file_path = None
                else:
                    break

        # Diagram not found?
        if full_file_path is None:
            raise FileNotFoundError(f"{file_path} not found.")

    if plantuml_generator.is_plantuml_file(file_path):
        plantuml_generator.generate(image_format, full_file_path, _out_path)

        file_dst_path = os.path.basename(full_file_path)
        file_dst_path = os.path.splitext(file_dst_path)[0]
        file_dst_path += "." + image_format

        # PlantUML uses as output filename the diagram name if available.
        # The diagram name may differ from the filename.
        # To aovid that a invalid reference will be in the Markdown document,
        # ensure that the generated filename is as expected.
        expected_dst_path = os.path.join(_out_path, file_dst_path)
        if os.path.isfile(expected_dst_path) is False:
            raise FileNotFoundError(
                f"{file_path} diagram name ('@startuml <name>') may differ from file name,"
                 " expected {expected_dst_path}."
            )

    else:
        # Copy diagram image file to output folder.
        shutil.copy(full_file_path, _out_path)
        file_dst_path = os.path.basename(full_file_path)

    markdown_image = markdown_create_diagram_link(file_dst_path, caption)
    fd.write(markdown_image)

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

    if record_object.n_typ.name == "Requirement":
        # System requirements are printed in a table.
        if _is_table_active is False:
            _print_req_table_head(fd)
            _set_table_active(True)

        _print_req(fd, record_object)

    elif record_object.n_typ.name == "Diagram":
        # If a table is active, close it.
        if _is_table_active is True:
            fd.write("\n")
            _set_table_active(False)

        _print_diagram(fd, record_object)

    else:
        # Skipped.
        pass

    return Ret.OK

# Main *************************************************************************
