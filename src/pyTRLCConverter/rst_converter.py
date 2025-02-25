"""Converter to reStructuredText format.

    Author: Your Name (your.email@example.com)
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
import sys
from typing import List, Optional
from trlc import trlc
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object
from pyTRLCConverter.log_verbose import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

class RstConverter(BaseConverter):
    """
    RstConverter provides functionality for converting to a reStructuredText format.
    """

    OUTPUT_FILE_NAME_DEFAULT = "output.rst"
    TOP_LEVEL_DEFAULT = "Specification"

    def __init__(self, args: any) -> None:
        """
        Initializes the converter.

        Args:
            args (any): The parsed program arguments.
        """
        super().__init__(args)

        # The path to the given output folder.
        self._out_path = args.out

        # The file descriptor for the output file. Used in single and multiple document mode.
        self._fd = None

        # The base level for the headings. Its the minimum level for the headings which depends
        # on the single/multiple document mode.
        self._base_level = 1

        # For proper reStructuredText formatting, the first written part shall not have an empty line before.
        # But all following parts (heading, table, paragraph, image, etc.) shall have an empty line before.
        # And at the document bottom, there shall be just one empty line.
        self._empty_line_required = False

    @staticmethod
    def get_subcommand() -> str:
        """
        Return subcommand token for this converter.

        Returns:
            str: Parser subcommand token
        """
        return "rst"

    @staticmethod
    def get_description() -> str:
        """
        Return converter description.

        Returns:
            str: Converter description
        """
        return "Convert into reStructuredText format."

    @classmethod
    def register(cls, args_parser: any) -> None:
        """
        Register converter specific argument parser.

        Args:
            args_parser (any): Argument parser
        """
        super().register(args_parser)

        BaseConverter._parser.add_argument(
            "-e",
            "--empty",
            type=str,
            default=BaseConverter.EMPTY_ATTRIBUTE_DEFAULT,
            required=False,
            help="Every attribute value which is empty will output the string." \
                f"(default = {BaseConverter.EMPTY_ATTRIBUTE_DEFAULT})."
        )

        BaseConverter._parser.add_argument(
            "-n",
            "--name",
            type=str,
            default=RstConverter.OUTPUT_FILE_NAME_DEFAULT,
            required=False,
            help="Name of the generated output file inside the output folder " \
                f"(default = {RstConverter.OUTPUT_FILE_NAME_DEFAULT}) in " \
                "case a single document is generated."
        )

        BaseConverter._parser.add_argument(
            "-sd",
            "--single-document",
            action="store_true",
            required=False,
            default=False,
            help="Generate a single document instead of multiple files. The default is to generate multiple files."
        )

        BaseConverter._parser.add_argument(
            "-tl",
            "--top-level",
            type=str,
            default=RstConverter.TOP_LEVEL_DEFAULT,
            required=False,
            help="Name of the top level heading, required in single document mode. " \
                f"(default = {RstConverter.TOP_LEVEL_DEFAULT})"
        )

    def begin(self) -> Ret:
        """
        Begin the conversion process.

        Returns:
            Ret: Status
        """
        assert self._fd is None

        result = Ret.OK

        # Single document mode?
        if self._args.single_document is True:
            log_verbose("Single document mode.")
        else:
            log_verbose("Multiple document mode.")

        # Set the value for empty attributes.
        self._empty_attribute_value = self._args.empty

        log_verbose(f"Empty attribute value: {self._empty_attribute_value}")

        # Single document mode?
        if self._args.single_document is True:
            result = self._generate_out_file(self._args.name)

            if self._fd is not None:
                self._fd.write(RstConverter.rst_create_heading(self._args.top_level, 1, self._args.name))

                # All headings will be shifted by one level.
                self._base_level = self._base_level + 1

        return result

    def enter_file(self, file_name: str) -> Ret:
        """
        Enter a file.

        Args:
            file_name (str): File name
        
        Returns:
            Ret: Status
        """
        result = Ret.OK

        # Multiple document mode?
        if self._args.single_document is False:
            assert self._fd is None

            file_name_rst = self._file_name_trlc_to_rst(file_name)
            result = self._generate_out_file(file_name_rst)

            # The very first written reStructuredText part shall not have an empty line before.
            self._empty_line_required = False

        return result

    def leave_file(self, file_name: str) -> Ret:
        """
        Leave a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """

        # Multiple document mode?
        if self._args.single_document is False:
            assert self._fd is not None
            self._fd.close()
            self._fd = None

        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        """
        Process the given section item.
        It will create a reStructuredText heading with the given section name and level.

        Args:
            section (str): The section name
            level (int): The section indentation level
        
        Returns:
            Ret: Status
        """
        assert len(section) > 0
        assert self._fd is not None

        self._write_empty_line_on_demand()
        rst_heading = self.rst_create_heading(section,
                                            self._get_rst_heading_level(level),
                                            os.path.basename(self._fd.name))
        self._fd.write(rst_heading)

        return Ret.OK

    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        """
        Process the given record object.

        Args:
            record (Record_Object): The record object
            level (int): The record level
        
        Returns:
            Ret: Status
        """
        assert self._fd is not None

        self._write_empty_line_on_demand()
        return self._convert_record_object(record, level, None)

    def finish(self):
        """
        Finish the conversion process.
        """

        # Single document mode?
        if self._args.single_document is True:
            assert self._fd is not None
            self._fd.close()
            self._fd = None

        return Ret.OK

    def _write_empty_line_on_demand(self) -> None:
        """
        Write an empty line if necessary.
        """
        if self._empty_line_required is False:
            self._empty_line_required = True
        else:
            self._fd.write("\n")

    def _get_rst_heading_level(self, level: int) -> int:
        """
        Get the reStructuredText heading level from the TRLC object level.
        Its mandatory to use this method to calculate the reStructuredText heading level.
        Otherwise in single document mode the top level heading will be wrong.

        Args:
            level (int): The TRLC object level.
        
        Returns:
            int: reStructuredText heading level
        """
        return self._base_level + level

    def _file_name_trlc_to_rst(self, file_name_trlc: str) -> str:
        """
        Convert a TRLC file name to a reStructuredText file name.

        Args:
            file_name_trlc (str): TRLC file name
        
        Returns:
            str: reStructuredText file name
        """
        file_name = os.path.basename(file_name_trlc)
        file_name = os.path.splitext(file_name)[0] + ".rst"

        return file_name

    def _generate_out_file(self, file_name: str) -> Ret:
        """
        Generate the output file.

        Args:
            file_name (str): The output file name without path.
            item_list ([Element]): List of elements.

        Returns:
            Ret: Status
        """
        result = Ret.OK
        file_name_with_path = file_name

        # Add path to the output file name.
        if 0 < len(self._out_path):
            file_name_with_path = os.path.join(self._out_path, file_name)

        try:
            self._fd = open(file_name_with_path, "w", encoding="utf-8") #pylint: disable=consider-using-with
        except IOError as e:
            print(f"Failed to open file {file_name_with_path}: {e}", file=sys.stderr)
            result = Ret.ERROR

        return result

    def _on_implict_null(self, _) -> str:
        """
        Process the given implicit null value.
        
        Returns:
            str: The implicit null value
        """
        return self._empty_attribute_value

    def _on_array_aggregate(self, value: trlc.ast.Array_Aggregate) -> str:
        """
        Process the given array aggregate value.
        It will process the array elements recursively.
        Each element will be separated by a comma.

        Args:
            value (trlc.ast.Array_Aggregate): The array aggregate value.
        
        Returns:
            str: A comma separated list of array element names or reStructuredText links.
        """
        result = ""

        dispatcher_map = {
            trlc.ast.Implicit_Null: self._on_implict_null,
            trlc.ast.Array_Aggregate: self._on_array_aggregate,
            trlc.ast.Record_Reference: self._on_record_reference
        }

        if len(value.value) > 0:
            type_name = type(value.value[0])
            if type_name in dispatcher_map:
                for idx, item in enumerate(value.value):
                    if idx > 0:
                        result += ", "

                    result += dispatcher_map[type_name](item)
            else:
                result = self.rst_escape(value.to_python_object())

        return result

    def _on_record_reference(self, value: trlc.ast.Record_Reference) -> str:
        """
        Process the given record reference value and return a reStructuredText link.

        Args:
            value (trlc.ast.Record_Reference): The record reference value.
        
        Returns:
            str: reStructuredText link to the record reference.
        """
        return self._create_rst_link_from_record_object_reference(value)

    def _on_field(self, value: trlc.ast.Expression) -> str:
        """
        Process the given field value and return it as a string.
        The main purpose is to handle arrays and record references explicitly.
        A record reference will be converted into a reStructuredText link.

        Args:
            value (trlc.ast.Expression): The field value
        
        Returns:
            str: The field value
        """
        result = ""

        dispatcher_map = {
            trlc.ast.Implicit_Null: self._on_implict_null,
            trlc.ast.Array_Aggregate: self._on_array_aggregate,
            trlc.ast.Record_Reference: self._on_record_reference
        }

        type_name = type(value)
        if type_name in dispatcher_map:
            result = dispatcher_map[type_name](value)
        else:
            result = self.rst_escape(value.to_python_object())

        return result

    def _create_rst_link_from_record_object_reference(self, record_reference: trlc.ast.Record_Reference) -> str:
        """
        Create a reStructuredText cross-reference from a record reference.
        It considers the file name, the package name, and the record name.

        Args:
            record_reference (trlc.ast.Record_Reference): Record reference

        Returns:
            str: reStructuredText cross-reference
        """
        file_name = ""

        # Single document mode?
        if self._args.single_document is True:
            file_name = self._args.name

        # Multiple document mode
        else:
            file_name = self._file_name_trlc_to_rst(record_reference.target.location.file_name)

        record_name = record_reference.target.name

        # Create a target ID for the record
        target_id = f"{file_name}-{record_name.lower().replace(' ', '-')}"

        return RstConverter.rst_create_link(record_reference.to_python_object(), target_id)

    def _convert_record_object(self, record: Record_Object, level: int, attribute_translation: Optional[dict]) -> Ret:
        """
        Process the given record object.

        Args:
            record (Record_Object): The record object.
            level (int): The record level.
            attribute_translation (Optional[dict]): Attribute translation (attribute name -> user friendly name).
        
            Returns:
            Ret: Status
        """
        assert self._fd is not None

        self._write_empty_line_on_demand()
        file_name = os.path.basename(self._fd.name)
        rst_heading = self.rst_create_heading(record.name, self._get_rst_heading_level(level + 1), file_name, is_object_heading=True)
        self._fd.write(rst_heading)
        self._fd.write("\n")

        column_titles = ["Attribute Name", "Attribute Value"]

        # Calculate the maximum width of each column based on both headers and row values
        max_widths = [len(title) for title in column_titles]
        for name, value in record.field.items():
            attribute_name = name
            if attribute_translation is not None and name in attribute_translation:
                attribute_name = attribute_translation[name]
            attribute_name = self.rst_escape(attribute_name)
            attribute_value = self._on_field(value)
            max_widths = [max(max_widths[i], len(val)) for i, val in enumerate([attribute_name, attribute_value])]

        rst_table_head = self.rst_create_table_head(column_titles, max_widths)
        self._fd.write(rst_table_head)

        for name, value in record.field.items():
            attribute_name = name
            if attribute_translation is not None and name in attribute_translation:
                attribute_name = attribute_translation[name]
            attribute_name = self.rst_escape(attribute_name)
            attribute_value = self._on_field(value)
            rst_table_row = self.rst_append_table_row([attribute_name, attribute_value], max_widths, False)
            self._fd.write(rst_table_row)

        return Ret.OK

    @staticmethod
    def rst_escape(text: str) -> str:
        """
        Escapes the text to be used in a reStructuredText document.

        Args:
            text (str): Text to escape

        Returns:
            str: Escaped text
        """
        characters = ["\\", "`", "*", "_", "{", "}", "[", "]", "<", ">", "(", ")", "#", "+", "-", ".", "!", "|"]

        for character in characters:
            text = text.replace(character, "\\" + character)

        return text

    @staticmethod
    def rst_create_heading(text: str, level: int, file_name: str, escape: bool = True, is_object_heading: bool = False) -> str:
        """
        Create a reStructuredText heading with a label.
        The text will be automatically escaped for reStructuredText if necessary.

        Args:
            text (str): Heading text
            level (int): Heading level
            file_name (str): File name where the heading is found
            escape (bool): Escape the text (default: True).
            is_object_heading (bool): Indicates if this is an object heading (default: False).

        Returns:
            str: reStructuredText heading with a label
        """
        text_raw = text

        if escape is True:
            text_raw = RstConverter.rst_escape(text)

        label = f"{file_name}-{text_raw.lower().replace(' ', '-')}"
        underline_char = ["=", "#", "~", "^", "\"", "+", "'"][level - 1]
        underline = underline_char * len(text_raw)

        if is_object_heading:
            admonition_label = f".. admonition:: {text_raw}\n\n    "
            return f".. _{label}:\n\n{admonition_label}"
        
        return f".. _{label}:\n\n{text_raw}\n{underline}\n"

    @staticmethod
    def rst_create_table_head(column_titles: List[str], max_widths: List[int], escape: bool = True) -> str:
        """
        Create the table head for a reStructuredText table in grid format.
        The titles will be automatically escaped for reStructuredText if necessary.

        Args:
            column_titles ([str]): List of column titles.
            max_widths ([int]): List of maximum widths for each column.
            escape (bool): Escape the titles (default: True).

        Returns:
            str: Table head
        """
        if escape:
            column_titles = [RstConverter.rst_escape(title) for title in column_titles]

        # Create the top border of the table
        table_head = "    +" + "+".join(["-" * (width + 2) for width in max_widths]) + "+\n"

        # Create the title row
        table_head += "    |" + "|".join([f" {title.ljust(max_widths[i])} " for i, title in enumerate(column_titles)]) + "|\n"

        # Create the separator row
        table_head += "    +" + "+".join(["=" * (width + 2) for width in max_widths]) + "+\n"

        return table_head

    @staticmethod
    def rst_append_table_row(row_values: List[str], max_widths: List[int], escape: bool = True) -> str:
        """
        Append a row to a reStructuredText table in grid format.
        The values will be automatically escaped for reStructuredText if necessary.

        Args:
            row_values ([str]): List of row values.
            max_widths ([int]): List of maximum widths for each column.
            escape (bool): Escapes every row value (default: True).

        Returns:
            str: Table row
        """
        if escape:
            row_values = [RstConverter.rst_escape(value) for value in row_values]

        # Create the row
        table_row = "    |" + "|".join([f" {value.ljust(max_widths[i])} " for i, value in enumerate(row_values)]) + "|\n"

        # Create the separator row
        separator_row = "    +" + "+".join(["-" * (width + 2) for width in max_widths]) + "+\n"

        return table_row + separator_row

    @staticmethod
    def rst_create_link(text: str, target: str, escape: bool = True) -> str:
        """
        Create a reStructuredText cross-reference.
        The text will be automatically escaped for reStructuredText if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Link text
            target (str): Cross-reference target
            escape (bool): Escapes text (default: True).

        Returns:
            str: reStructuredText cross-reference
        """
        text_raw = text

        if escape is True:
            text_raw = RstConverter.rst_escape(text)

        return f":ref:`{text_raw} <{target}>`"

    @staticmethod
    def rst_create_diagram_link(diagram_file_name: str, diagram_caption: str, escape: bool = True) -> str:
        """
        Create a reStructuredText diagram link.
        The caption will be automatically escaped for reStructuredText if necessary.

        Args:
            diagram_file_name (str): Diagram file name
            diagram_caption (str): Diagram caption
            escape (bool): Escapes caption (default: True).

        Returns:
            str: reStructuredText diagram link
        """
        diagram_caption_raw = diagram_caption

        if escape is True:
            diagram_caption_raw = RstConverter.rst_escape(diagram_caption)

        return f".. image:: ./{diagram_file_name}\n   :alt: {diagram_caption_raw}\n"

# Functions ********************************************************************

# Main *************************************************************************