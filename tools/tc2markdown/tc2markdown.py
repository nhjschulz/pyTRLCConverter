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
        return "Convert test case definitions into project extended markdown format."

    def convert_section(self, section: str, level: int) -> Ret:
        """Converts a section to Markdown format.

        Args:
            section (str): Section to convert
            level (int): Current level of the section

        Returns:
            Ret: Status
        """
        markdown_text = self.markdown_create_heading(section, self._get_markdown_heading_level(level))
        self._fd.write(markdown_text)

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

        if record.n_typ.name == "Diagram":
            self._print_diagram(record, level)

        if record.n_typ.name == "Info":
            self._print_info(record, level)

        elif record.n_typ.name == "SwTestCase":
            self._print_sw_test_case(record, level)

        else:
            # Skipped.
            pass

        return Ret.OK

    def _print_table_head(self) -> None:
        """Prints the table head for software requirements and constraints.
        """
        column_titles = ["Attribute", "Value"]
        markdown_table_head = self.markdown_create_table_head(column_titles)

        self._fd.write(markdown_table_head)

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
        self._fd.write("\n\n")

    def _print_sw_test_case(self, sw_test_case: Record_Object, level: int) -> None:
        """Prints the software test case.

        Args:
            sw_test_case (Record_Object): Software test case to print
            level (int): Current level of the record object
        """
        attribute_translation = {
            "description": "Description",
            "derived": "Derived"
        }

        self._convert_record_object(sw_test_case, level, attribute_translation)

# Functions ********************************************************************

# Main *************************************************************************
