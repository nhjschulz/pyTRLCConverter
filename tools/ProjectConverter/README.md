# Project Converter Implementations <!-- omit in toc -->

- [Overview](#overview)
- [Project Converter Class Diagram](#project-converter-class-diagram)

## Overview

This folder adds project specifc converters for the pyTRCLConverter model files in
[doc/models](../../doc/models/). The coverters build hierarchies to add support
for the follwing files based on their include dependencies:

- [generic.rsl](../../doc/models/generic.rsl)
- [sw_req.rsl](../../doc/models/sw_req.rsl)
- [sw_req.rsl](../../doc/models/sw_req.rsl)

## Project Converter Class Diagram

The follwing diagrams shows the relations between the converter classes:

![context](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/NewTec-GmbH/pyTRLCConverter/refs/heads/main/tools/ProjectConverter/project_converter_class_diagram.puml)
