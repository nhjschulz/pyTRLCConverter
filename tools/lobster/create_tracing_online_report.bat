@echo off

rem pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
rem Copyright (c) 2024 - 2025 NewTec GmbH
rem
rem This file is part of pyTRLCConverter program.
rem
rem The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
rem the terms of the GNU General Public License as published by the Free Software Foundation,
rem either version 3 of the License, or (at your option) any later version.
rem
rem The pyTRLCConverter program is distributed in the hope that it will be useful, but
rem WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
rem FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License along with pyTRLCConverter.
rem If not, see <https://www.gnu.org/licenses/>.

set LOBSTER_TRLC=lobster-trlc
set LOBSTER_PYTHON=lobster-python
set LOBSTER_REPORT=lobster-report
set LOBSTER_ONLINE_REPORT=lobster-online-report
set LOBSTER_RENDERER=lobster-html-report
set OUT_DIR=out
set SOURCES=..\..\..\doc\sw-requirements
set MODELS=..\..\..\doc\models
set PYTHON_SOURCES=..\..\..\src\pyTRLCConverter
set LOCAL_REPOSITORY_ROOT=..\..\..
set COMMIT=%~1

if "%1" == "" (
    echo Branch/Commit hash is missing.
    goto error
)

if not exist "%OUT_DIR%" (
    md %OUT_DIR%
)

cd %OUT_DIR%

%LOBSTER_TRLC% --config-file ..\lobster-trlc.conf --out trlc.lobster %SOURCES% %MODELS%

if errorlevel 1 (
    goto error
)

%LOBSTER_PYTHON% --out python.lobster %PYTHON_SOURCES%

if errorlevel 1 (
    goto error
)

%LOBSTER_REPORT% --lobster-config ..\lobster.conf --out lobster-report.lobster

if errorlevel 1 (
    goto error
)

%LOBSTER_ONLINE_REPORT% --out online-report.lobster lobster-report.lobster --repo-root %LOCAL_REPOSITORY_ROOT% --commit %COMMIT%

if errorlevel 1 (
    goto error
)

%LOBSTER_RENDERER% --out tracing_online_report.html online-report.lobster

if errorlevel 1 (
    goto error
)

goto finished

:error

:finished
cd ..
