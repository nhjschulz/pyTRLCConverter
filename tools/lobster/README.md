# lobster

## Overview

![tracing_toolchain](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/NewTec-GmbH/pyTRLCConverter/refs/heads/main/tools/lobster/tracing_toolchain.puml)

The shown tool call chain is hidden in two scripts:
* ```create_tracing_report.[bat|sh]```
* ```create_tracing_online_report.[bat|sh]```

## How to generate a local tracing report?

The following tracing report will consider the local checked out files!

1. Call create_tracing_report.[bat|sh] depended on your OS.
2. It will create the tracability report in the ```./out``` folder.
3. Open ```tracing_report.html``` in your browser.

## How to generate a online tracing report?

The following tracing report will consider the files on git SHA base for unique identification.

1. Call create_tracing_online_report.[bat|sh] depended on your OS and provide the git SHA as parameter like e.g.
    ```bash
    ./create_tracing_online_report <GIT-SHA>
    ```
2. It will create the tracability report in the ```./out``` folder.
3. Open ```tracing_online_report.html``` in your browser.
