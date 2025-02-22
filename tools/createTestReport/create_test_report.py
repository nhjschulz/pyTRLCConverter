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

from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class CustomMarkDownConverter(MarkdownConverter):
    """Custom Project specific Markdown Converter responsible for converting the
        SW test case results into Markdown format.
    """

    def __init__(self, args: any) -> None:
        """Initializes the converter.
        """
        super().__init__(args)

        self._is_table_head_req = True

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert SW test case results to Markdown format."

    def convert_section(self, section: str, level: int) -> Ret:
        """Converts a section to Markdown format.

        Args:
            section (str): Section to convert
            level (int): Current level of the section

        Returns:
            Ret: Status
        """
        markdown_text = self.markdown_create_heading(section, level + 1)
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

        if record.n_typ.name == "SwTestCaseResult":
            self._print_test_case_result(record, level)

        else:
            # Skipped.
            pass

        return Ret.OK

    def _print_table_head(self) -> None:
        """Prints the table head for software test case results.
        """
        column_titles = ["Test Case", "Test Function", "Test Result"]
        markdown_table_head = self.markdown_create_table_head(column_titles)

        self._fd.write(markdown_table_head)

    def _print_test_case_result(self, test_case_result: Record_Object, level: int) -> None:
        """Prints the software test case result.

        Args:
            test_case_result (Record_Object): Software test case result to print
            level (int): Current level of the record object
        """
        if self._is_table_head_req is True:
            self._print_table_head()
            self._is_table_head_req = False

        test_case_result_attributes = test_case_result.to_python_dict()

        test_function_name = self._get_attribute(test_case_result, "name")
        test_result = self._get_attribute(test_case_result, "result")

        test_case = test_case_result_attributes["relates"]
        if test_case is None:
            test_case = self.markdown_escape("N/A")
        else:
            anchor_tag = "#" + test_case.replace("SwTests.", "").lower()
            anchor_tag = anchor_tag.replace(" ", "-")

            test_case = self.markdown_create_link(test_case, anchor_tag)

        test_function_name = self.markdown_escape(test_function_name)

        if test_result == "PASSED":
            test_result = self.markdown_text_color(test_result, "color:lightgreen")
        elif test_result == "FAILED":
            test_result = self.markdown_text_color(test_result, "color:red")

        row = [test_case, test_function_name, test_result]

        markdown_table_row = self.markdown_append_table_row(row, False)
        self._fd.write(markdown_table_row)

# Functions ********************************************************************

# Main *************************************************************************
