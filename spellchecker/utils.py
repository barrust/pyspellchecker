""" Additional utility functions """
import sys
import re
import gzip
import contextlib

if sys.version_info < (3, 0):
    import io  # python 2 text file encoding support
    READMODE = 'rb'
    WRITEMODE = 'wb'
    OPEN = io.open  # hijack this

    def ENSURE_UNICODE(s, encoding='utf-8'):
        if isinstance(s, str):
            return s.decode(encoding)
        return s

else:
    READMODE = 'rt'
    WRITEMODE = 'wt'
    OPEN = open

    def ENSURE_UNICODE(s, encoding='utf-8'):
        if isinstance(s, bytes):
            return s.decode(encoding)
        return s


@contextlib.contextmanager
def __gzip_read(filename, mode='rb', encoding='UTF-8'):
    """ Context manager to correctly handle the decoding of the output of \
        the gzip file

        Args:
            filename (str): The filename to open
            mode (str): The mode to read the data
            encoding (str): The file encoding to use
        Yields:
            str: The string data from the gzip file read
    """
    if sys.version_info < (3, 0):
        with gzip.open(filename, mode=mode) as fobj:
            yield fobj.read().decode(encoding)
    else:
        with gzip.open(filename, mode=mode, encoding=encoding) as fobj:
            yield fobj.read()


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
        with __gzip_read(filename, mode=READMODE, encoding=encoding) as data:
            yield data
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
        with gzip.open(filepath, WRITEMODE) as fobj:
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
