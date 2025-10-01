"""Command line interface to convert Doxygen XML to Markdown."""

import argparse
import logging
import sys

if __name__ == "__main__":
    sys.exit(f"{__file__} is not a script.")


class LogFormatter(logging.Formatter):
    """Custom console log formatting."""

    def format(self, record):
        reset = "\x1b[0m"
        colors = {
            "DEBUG": "\x1b[38m",  # grey
            "WARNING": "\x1b[33m",  # yellow
            "ERROR": "\x1b[31m",  # red
            "INFO": "\x1b[34m",  # blue
            "CRITICAL": "\x1b[41m",  # red background
        }
        return (
            # cspell:ignore levelname
            f"{colors[record.levelname]}{record.levelname.lower():8}{reset} "
            f"{record.getMessage()}"
        )


def parse_command_line() -> argparse.Namespace:
    """
    Parse the command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert Doxygen XML output to Markdown files."
    )
    parser.add_argument(
        "input", help="The path to the directory containing Doxygen XML."
    )
    parser.add_argument("output", help="Path to the directory to write Markdown files.")
    arguments = parser.parse_args()
    return arguments
