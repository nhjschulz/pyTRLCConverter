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
from pyTRLCConverter.ret import Ret

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
        assert self._fd is not None

        self._write_empty_line_on_demand()

        if record.n_typ.name == "Requirement":
            self._print_req(record, level)

        else:
            # Skipped.
            pass

        return Ret.OK

    def _print_req(self, req: Record_Object, level: int) -> None:
        """Prints the requirement.

        Args:
            req (Record_Object): Requirement to print
            level (int): Current level of the record object
        """
        attribute_translation = {
            "description": "Description"
        }

        self._convert_record_object(req, level, attribute_translation)

# Functions ********************************************************************

# Main *************************************************************************
