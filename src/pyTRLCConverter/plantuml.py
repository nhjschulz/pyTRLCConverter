"""PlantUML to image file converter.

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
import subprocess

# Variables ********************************************************************

# Classes **********************************************************************

class PlantUML():
    """PlantUML image generator.
    """
    def __init__(self) -> None:
        self._plantuml_jar = None
        self._working_directory = os.path.abspath(os.getcwd())

        if "PLANTUML" in os.environ:
            self._plantuml_jar = os.environ["PLANTUML"]

    def _get_absolute_path(self, path):
        """Get absolute path to the diagram.
            This is required by PlantUML java program for the output path.

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        absolute_path = path

        if os.path.isabs(path) is False:
            absolute_path = os.path.join(self._working_directory, path)

        return absolute_path

    def is_plantuml_file(self, diagram_path):
        """Is the diagram a PlantUML file?
            Only the file extension will be checked.

        Args:
            diagram_path (str): Diagram path.

        Returns:
            bool: If file is a PlantUML file, it will return True otherwise False.
        """
        is_valid = False

        if diagram_path.endswith(".plantuml") or \
            diagram_path.endswith(".puml") or \
            diagram_path.endswith(".wsd"):
            is_valid = True

        return is_valid

    def generate(self, diagram_type, diagram_path, dst_path):
        """Generate image.

        Args:
            diagram_type (str): Diagram type, e.g. svg. See PlantUML -t options.
            diagram_path (str): Path to the PlantUML diagram.
            dst_path (str): Path to the destination of the generated image.

        Raises:
            FileNotFoundError: PlantUML java jar file not found.
        """
        if self._plantuml_jar is not None:

            if 0 < len(dst_path):
                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)

            plantuml_cmd = [
                "java", \
                "-jar", f"{self._plantuml_jar}", \
                f"{diagram_path}", \
                f"-t{diagram_type}", \
                "-o", self._get_absolute_path(dst_path)
            ]

            try:
                output = subprocess.run(plantuml_cmd, capture_output=True, text=True, check=False)
                print(output.stdout)
            except FileNotFoundError as exc:
                raise FileNotFoundError(f"{self._plantuml_jar} not found.") from exc

# Functions ********************************************************************

# Main *************************************************************************
