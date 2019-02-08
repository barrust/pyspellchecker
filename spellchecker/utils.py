""" Additional utility functions """
import sys
import re
import gzip
import contextlib

if sys.version_info < (3, 0):
    import io  # python 2 text file encoding support

    OPEN = io.open  # hijack this
else:
    OPEN = open


@contextlib.contextmanager
def load_file(filename, encoding):
    """ Context manager to handle opening a gzip or text file correctly and
        reading all the data

        Args:
            filename (str): The filename to open
            encoding (str): The file encoding to use
        Yields:
            str: The string data from the file read
    """
    try:
        with gzip.open(filename, mode="rt") as fobj:
            yield fobj.read()
    except (OSError, IOError):
        with OPEN(filename, mode="r", encoding=encoding) as fobj:
            yield fobj.read()


def write_file(filepath, encoding, gzipped, data):
    """ Write the data to file either as a gzip file or text based on the
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
        with OPEN(filepath, "w", encoding=encoding) as fobj:
            if sys.version_info < (3, 0):
                data = data.decode(encoding)
            fobj.write(data)


def _parse_into_words(text):
    """ Parse the text into words; currently removes punctuation

        Args:
            text (str): The text to split into words
    """
    return re.findall(r"\w+", text.lower())
