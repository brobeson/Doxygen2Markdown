"""Convert Doxygen XML output to Markdown files."""

import logging
from dox_md import cli, xml_processor, documentation

channel = logging.StreamHandler()
channel.setFormatter(cli.LogFormatter())
logger = logging.getLogger()
logger.addHandler(channel)
logger.setLevel(logging.INFO)

options = cli.parse_command_line()
logger.setLevel(options.log_level.upper())
xml_files = xml_processor.find_xml_files(options.input)
docs = documentation.Documentation(options.output, options.clang_format)
for xml_file in xml_files:
    parsed_xml = xml_processor.read_xml_file(xml_file)
    if parsed_xml is not None:
        docs.write_class(parsed_xml)
