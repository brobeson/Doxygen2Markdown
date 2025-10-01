"""Write Doxygen data to Markdown files."""

import logging
import os.path
from typing import IO, Optional


class Writer:
    """
    Write information to a Markdown file.

    To use this as a context manager, first instantiate a Writer, then use ``new_file()`` to
    invoke context management.

    .. code-block:: py

        writer = Writer("docs/")
        with new_file(writer, "vector.md") as _:
            writer.write_heading(1, "`std::vector`")

    Attributes:
        output_root(str): The root directory in which to write any Markdown files.
        output_file(str): The path, relative to ``output_root``, for the current file.
        file: The file stream for ``output_file``.
    """

    def __init__(self, output_root: str):
        if not os.path.exists(output_root):
            os.makedirs(output_root)
        if not os.path.isdir(output_root):
            raise FileExistsError(f"{output_root} exists and is not a directory")
        self.output_root = output_root
        self.output_file: Optional[str] = None
        self.file: Optional[IO[str]] = None

    def __enter__(self):
        logging.debug("Starting writer")
        if self.file is not None:
            raise RuntimeError(
                "already writing a file, cannot write another at the same time"
            )
        self.file = open(self.output_file, encoding="utf-8", mode="w")

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        self.file = None
        logging.debug("Stopping writer")

    def write_heading(self, level: int, heading: str) -> None:
        """
        Write a Markdown heading to the current file.

        Args:
            level (int): The heading level. This must be in the range [1, 6].
            heading (str): The heading text.
        """
        if self.file is not None:
            self.file.write(f"{'#' * level} {heading}\n")


def new_file(writer: Writer, file_path: str) -> Writer:
    """
    Initiate context management for writing Markdown files.

    Args:
        writer (Writer): The Writer to use for writing Markdown files.
        file_path (str): The path to the new file to write. This should be relative to
        ``writer.output_root``.

    Returns:
        Writer: This function returns ``writer``. It's safe to ignore the return value.
    """
    file_path, _ = os.path.splitext(file_path)
    file_path += ".md"
    writer.output_file = os.path.join(writer.output_root, file_path)
    return writer
