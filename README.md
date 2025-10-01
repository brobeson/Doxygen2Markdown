# Doxygen 2 Markdown

![Maturity: Alpha Software](https://img.shields.io/badge/Maturity-Alpha_Software-red)
[![Build Status](https://github.com/brobeson/doxygen2markdown/actions/workflows/build.yaml/badge.svg)](https://github.com/brobeson/doxygen2markdown/actions/workflows/build.yaml)

Doxygen 2 Markdown converts Doxygen XML output to Markdown files.

## Quick Start

1. Configure Doxygen to output XML.
   In your Doxyfile, set `GENERATE_XML = YES`
1. Run Doxygen in your project.
1. Run `dox_md`:
   ```bash
   python3 dox_md INPUT OUTPUT
   ```
   `INPUT` must be the path to the directory that contains the Doxygen XML files.
   `OUTPUT` must be the path to the directory your want `dox_md` to write the Markdown files.

See the [command reference](docs/command_reference.md) for details.
