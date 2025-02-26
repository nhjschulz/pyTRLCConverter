"""Project specific Markdown converter functions.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
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

from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class CustomMarkDownConverter(MarkdownConverter):
    """Custom Project specific Markdown Converter.
    """

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project extended markdown format."

    def convert_section(self, section: str, level: int) -> Ret:
        """Converts a section to Markdown format.

        Args:
            section (str): Section to convert
            level (int): Current level of the section

        Returns:
            Ret: Status
        """
        assert len(section) > 0
        assert self._fd is not None

        self._write_empty_line_on_demand()
        markdown_heading = self.markdown_create_heading(section, self._get_markdown_heading_level(level))
        self._fd.write(markdown_heading)

        return Ret.OK

    # pylint: disable=unused-argument
    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        """Converts a record object to Markdown format.

        Args:
            record (Record_Object): Record object to convert
            level (int): Current level of the record object

        Returns:
            Ret: Status
        """
        assert self._fd is not None

        self._write_empty_line_on_demand()

        if record.n_typ.name == "Diagram":
            self._print_diagram(record, level)

        if record.n_typ.name == "Info":
            self._print_info(record, level)

        elif record.n_typ.name == "SwReq":
            self._print_sw_req(record, level)

        elif record.n_typ.name == "SwReqNonFunc":
            self._print_sw_req(record, level)

        elif record.n_typ.name == "SwConstraint":
            self. _print_sw_constraint(record, level)

        else:
            # Skipped.
            pass

        return Ret.OK

    # pylint: disable=unused-argument
    def _print_diagram(self, diagram: Record_Object, level: int) -> None:
        """Prints the diagram.

        Args:
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

            full_file_path = self._locate_file(full_file_path)
            # Diagram not found?
            if full_file_path is None:
                raise FileNotFoundError(f"{file_path} not found.")

        if plantuml_generator.is_plantuml_file(file_path):

            plantuml_generator.generate(
                image_format, full_file_path, self._args.out)

            file_dst_path = os.path.basename(full_file_path)
            file_dst_path = os.path.splitext(file_dst_path)[0]
            file_dst_path += "." + image_format

            # PlantUML uses as output filename the diagram name if available.
            # The diagram name may differ from the filename.
            # To aovid that a invalid reference will be in the Markdown document,
            # ensure that the generated filename is as expected.
            expected_dst_path = os.path.join(self._args.out, file_dst_path)
            if os.path.isfile(expected_dst_path) is False:
                raise FileNotFoundError(
                    f"{file_path} diagram name ('@startuml <name>') may differ from file name,"
                    f" expected {expected_dst_path}."
                )

        else:
            # Copy diagram image file to output folder.
            shutil.copy(full_file_path, self._args.out)
            file_dst_path = os.path.basename(full_file_path)

        markdown_image = self.markdown_create_diagram_link(
            file_dst_path, caption)
        self._fd.write(markdown_image)

    def _print_info(self, info: Record_Object, level: int) -> None:
        """Prints the information.

        Args:
            info (Record_Object): Information to print
            level (int): Current level of the record object
        """
        description = self._get_attribute(info, "description")

        markdown_info = self.markdown_escape(description)
        self._fd.write(markdown_info)
        self._fd.write("\n")

    def _print_sw_req(self, sw_req: Record_Object, level: int) -> None:
        """Prints the software requirement.

        Args:
            sw_req (Record_Object): Software requirement to print
            level (int): Current level of the record object
        """
        attribute_translation = {
            "description": "Description",
            "note": "Note",
            "verification_criteria": "Verification Criteria",
            "derived": "Derived"
        }

        self._convert_record_object(sw_req, level, attribute_translation)

    def _print_sw_constraint(self, sw_constraint: Record_Object, level: int) -> None:
        """Prints the software constraint.

        Args:
            sw_constraint (Record_Object): Software constraint to print
            level (int): Current level of the record object
        """
        attribute_translation = {
            "description": "Description",
            "note": "Note",
            "derived": "Derived"
        }

        self._convert_record_object(sw_constraint, level, attribute_translation)

# Functions ********************************************************************

# Main *************************************************************************
