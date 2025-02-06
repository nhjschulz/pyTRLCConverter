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
    markdown_append_table_row, markdown_create_diagram_link, markdown_create_link, markdown_escape

# Variables ********************************************************************
_source_items = []
_OUT_PATH = ""

# Classes **********************************************************************

# Functions ********************************************************************

def _print_table_head(fd):
    """Prints the table head for software requirements and constraints.

    Args:
        fd (file): File descriptor
    """
    column_titles = ["Attribute", "Value"]
    markdown_table_head = markdown_create_table_head(column_titles)

    fd.write(markdown_table_head)

# pylint: disable=unused-argument
def _print_diagram(fd, diagram, level):
    """Prints the diagram.

    Args:
        fd (file): File descriptor
        diagram (Record_Object): Diagram to print
        level (int): Current level of the record object
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

        plantuml_generator.generate(image_format, full_file_path, _OUT_PATH)

        file_dst_path = os.path.basename(full_file_path)
        file_dst_path = os.path.splitext(file_dst_path)[0]
        file_dst_path += "." + image_format

        # PlantUML uses as output filename the diagram name if available.
        # The diagram name may differ from the filename.
        # To aovid that a invalid reference will be in the Markdown document,
        # ensure that the generated filename is as expected.
        expected_dst_path = os.path.join(_OUT_PATH, file_dst_path)
        if os.path.isfile(expected_dst_path) is False:
            raise FileNotFoundError(
                f"{file_path} diagram name ('@startuml <name>') may differ from file name,"
                 " expected {expected_dst_path}."
            )

    else:
        # Copy diagram image file to output folder.
        shutil.copy(full_file_path, _OUT_PATH)
        file_dst_path = os.path.basename(full_file_path)

    markdown_image = markdown_create_diagram_link(file_dst_path, caption)
    fd.write(markdown_image)

def _print_sw_req(fd, sw_req, level):
    """Prints the software requirement.

    Args:
        fd (file): File descriptor
        sw_req (Record_Object): Software requirement to print
        level (int): Current level of the record object
    """
    sw_req_id = sw_req.name
    sw_req_attributes = sw_req.to_python_dict()
    description = sw_req_attributes["description"]
    verification_proposal = sw_req_attributes["verification_proposal"]
    info = sw_req_attributes["info"]
    derived = sw_req_attributes["derived"]
    derived_info = "N/A"

    if info is None:
        info = "N/A"

    if derived is not None:
        derived_info = ""
        for idx, derived_req in enumerate(derived):
            if 0 < idx:
                derived_info += ", "

            anchor_tag = "#" + derived_req.replace("SwRequirements.", "").lower()
            anchor_tag = anchor_tag.replace(" ", "-")

            derived_info += markdown_create_link(derived_req, anchor_tag)

    markdown_text = markdown_create_heading(sw_req_id, level + 1)
    fd.write(markdown_text)

    _print_table_head(fd)

    table = [
        ["Description", markdown_escape(description)],
        ["Verification Proposal", markdown_escape(verification_proposal)],
        ["Info", markdown_escape(info)],
        ["Derived", derived_info]
    ]

    for row in table:
        markdown_table_row = markdown_append_table_row(row, False)
        fd.write(markdown_table_row)

    fd.write("\n")

def _print_sw_constraint(fd, sw_req, level):
    """Prints the software constraint.

    Args:
        fd (file): File descriptor
        sw_req (Record_Object): Software constraint to print
        level (int): Current level of the record object
    """
    sw_constraint_id = sw_req.name
    sw_constraint_attributes = sw_req.to_python_dict()
    description = sw_constraint_attributes["description"]
    info = sw_constraint_attributes["info"]

    if info is None:
        info = "N/A"

    markdown_text = markdown_create_heading(sw_constraint_id, level + 1)
    fd.write(markdown_text)

    _print_table_head(fd)

    table = [
        ["Description", description],
        ["Info", info]
    ]

    for row in table:
        markdown_table_row = markdown_append_table_row(row)
        fd.write(markdown_table_row)

    fd.write("\n")

def init(sources, out_path):
    """Initializes the Markdown converter.

    Args:
        sources (list): List of source paths
        out_path (str): Output path
    """
    global _source_items, _OUT_PATH # pylint: disable=global-statement
    _source_items = sources
    _OUT_PATH = out_path

def convert_section(fd, section, level):
    """Converts a section to Markdown format.

    Args:
        fd (file): File descriptor
        section (dict): Section to convert
        level (int): Current level of the section
    """
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

    if record_object.n_typ.name == "SwReqDiagram":
        _print_diagram(fd, record_object, level)

    elif record_object.n_typ.name == "SwReq":
        _print_sw_req(fd, record_object, level)

    elif record_object.n_typ.name == "SwConstraint":
        _print_sw_constraint(fd, record_object, level)

    else:
        # Skipped.
        pass

    return Ret.OK

# Main *************************************************************************
