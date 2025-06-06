""" Additional utility functions """
import contextlib
import gzip
import re
import typing
from pathlib import Path

from spellchecker.info import __version__

KeyT = typing.Union[str, bytes]
PathOrStr = typing.Union[Path, str]


def ensure_unicode(value: KeyT, encoding: str = "utf-8") -> str:
    """Simplify checking if passed in data are bytes or a string and decode
    bytes into unicode.

    Args:
        value (str): The input string (possibly bytes)
        encoding (str): The encoding to use if input is bytes
    Returns:
        str: The encoded string
    """
    if isinstance(value, bytes):
        return value.decode(encoding)
    elif isinstance(value, list):
        raise TypeError(f"The provided value {value} is not of type str or bytes")
    return value


@contextlib.contextmanager
def __gzip_read(filename: PathOrStr, mode: str = "rb", encoding: str = "UTF-8") -> typing.Generator[KeyT, None, None]:
    """Context manager to correctly handle the decoding of the output of the gzip file

    Args:
        filename (str): The filename to open
        mode (str): The mode to read the data
        encoding (str): The file encoding to use
    Yields:
        str: The string data from the gzip file read
    """
    with gzip.open(filename, mode=mode, encoding=encoding) as fobj:
        yield fobj.read()


@contextlib.contextmanager
def load_file(filename: PathOrStr, encoding: str) -> typing.Generator[KeyT, None, None]:
    """Context manager to handle opening a gzip or text file correctly and
    reading all the data

    Args:
        filename (str): The filename to open
        encoding (str): The file encoding to use
    Yields:
        str: The string data from the file read
    """
    if isinstance(filename, Path):
        filename = str(filename)

    if filename[-3:].lower() == ".gz":
        with __gzip_read(filename, mode="rt", encoding=encoding) as data:
            yield data
    else:
        with open(filename, encoding=encoding) as fobj:
            yield fobj.read()


def write_file(filepath: PathOrStr, encoding: str, gzipped: bool, data: str) -> None:
    """Write the data to file either as a gzip file or text based on the
    gzipped parameter

    Args:
        filepath (str): The filename to open
        encoding (str): The file encoding to use
        gzipped (bool): Whether the file should be gzipped or not
        data (str): The data to be written out
    """
    if gzipped:
        with gzip.open(filepath, "wt") as fobj:
            fobj.write(data)
    else:
        with open(filepath, "w", encoding=encoding) as fobj:
            fobj.write(data)


def _parse_into_words(text: str) -> typing.Iterable[str]:
    """Parse the text into words; currently removes punctuation except for
    apostrophizes.

    Args:
        text (str): The text to split into words
    """
    # see: https://stackoverflow.com/a/12705513
    return re.findall(r"(\w[\w']*\w|\w)", text)
