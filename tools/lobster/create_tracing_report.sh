#!/bin/bash

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

LOBSTER_TRLC=lobster-trlc
LOBSTER_PYTHON=lobster-python
LOBSTER_REPORT=lobster-report
LOBSTER_RENDERER=lobster-html-report
OUT_DIR=out
SOURCES=../../../doc/sw-requirements
MODELS=../../../doc/models
PYTHON_SOURCES=../../../src/pyTRLCConverter

if [ ! -d "$OUT_DIR" ]; then
    mkdir "$OUT_DIR"
fi

cd "$OUT_DIR"

$LOBSTER_TRLC --config-file ../lobster-trlc.conf --out trlc.lobster $SOURCES $MODELS
if [ $? -ne 0 ]; then
    echo "Error in $LOBSTER_TRLC"
    exit 1
fi

$LOBSTER_PYTHON --out python.lobster $PYTHON_SOURCES
if [ $? -ne 0 ]; then
    echo "Error in $LOBSTER_PYTHON"
    exit 1
fi

$LOBSTER_REPORT --lobster-config ../lobster.conf --out lobster-report.lobster
if [ $? -ne 0 ]; then
    echo "Error in $LOBSTER_REPORT"
    exit 1
fi

$LOBSTER_RENDERER --out tracing_report.html lobster-report.lobster
if [ $? -ne 0 ]; then
    echo "Error in $LOBSTER_RENDERER"
    exit 1
fi

echo "Tracing report generated successfully"
cd ..
