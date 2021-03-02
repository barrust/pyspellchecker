""" Additional utility functions """
import contextlib
import gzip
import re

def fail_after(version):
    import functools
    from .info import __version__

    def decorator_wrapper(func):
        @functools.wraps(func)
        def test_inner(*args, **kwargs):
            if [int(x) for x in version.split('.')] <= [int(x) for x in __version__.split('.')]:
                raise AssertionError("The function {} must be fully removed as it is depricated and must be removed by version {}".format(func.__name__, version))
            return func(*args, **kwargs)
        return test_inner
    return decorator_wrapper

def deprecated(message=""):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used first time and filter is set for show DeprecationWarning.
    """
    import warnings
    import functools

    def decorator_wrapper(func):
        @functools.wraps(func)
        def function_wrapper(*args, **kwargs):
            func_name = func.__name__
            if func_name not in function_wrapper.deprecated_items:
                warnings.warn("Function {} is now deprecated! {}".format(func.__name__, message),
                              category=DeprecationWarning, stacklevel=2)
                function_wrapper.deprecated_items.add(func_name)

            return func(*args, **kwargs)
        # set this up the first time the decorator is called
        function_wrapper.deprecated_items = set()

        return function_wrapper
    return decorator_wrapper

def ensure_unicode(s, encoding='utf-8'):
    """ Simplify checking if passed in data are bytes or a string and decode
        bytes into unicode.

        Args:
            s (str): The input string (possibly bytes)
            encoding (str): The encoding to use if input is bytes
        Returns:
            str: The encoded string
    """
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
    if filename[-3:].lower() == ".gz":
        with __gzip_read(filename, mode='rt', encoding=encoding) as data:
            yield data
    else:
        with open(filename, mode="r", encoding=encoding) as fobj:
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
        with gzip.open(filepath, 'wt') as fobj:
            fobj.write(data)
    else:
        with open(filepath, "w", encoding=encoding) as fobj:
            fobj.write(data)


def _parse_into_words(text):
    """ Parse the text into words; currently removes punctuation except for
        apostrophies.

        Args:
            text (str): The text to split into words
    """
    # see: https://stackoverflow.com/a/12705513
    return re.findall(r"(\w[\w']*\w|\w)", text.lower())
