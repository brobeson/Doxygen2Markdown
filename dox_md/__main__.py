"""Convert Doxygen XML output to Markdown files."""

import logging
from dox_md import cli, xml_processor

# logging.basicConfig(level=logging.INFO, format="[ %(levelname)-8s ] %(message)s")
# logging.basicConfig(level=logging.INFO)  # , format="[ %(levelname)-8s ] %(message)s")
channel = logging.StreamHandler()
channel.setFormatter(cli.LogFormatter())
logger = logging.getLogger()
logger.addHandler(channel)
logger.setLevel(logging.DEBUG)

ARGUMENTS = cli.parse_command_line()
XML_FILES = xml_processor.find_xml_files(ARGUMENTS.input)
xml_processor.process_xml_files(XML_FILES)
