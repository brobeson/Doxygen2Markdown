"""Convert Doxygen XML output to Markdown files."""

import logging
from dox_md import cli, markdown_writer, xml_processor

channel = logging.StreamHandler()
channel.setFormatter(cli.LogFormatter())
logger = logging.getLogger()
logger.addHandler(channel)
logger.setLevel(logging.INFO)

options = cli.parse_command_line()
logger.setLevel(options.log_level.upper())
xml_files = xml_processor.find_xml_files(options.input)
xml_processor.process_xml_files(xml_files, markdown_writer.Writer(options.output))
