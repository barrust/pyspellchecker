""" SpellChecker Module; simple, intuitive spell checker based on the post by
    Peter Norvig. See: https://norvig.com/spell-correct.html """
import gzip
import json
import pkgutil
import string
import typing
from collections import Counter
from collections.abc import Iterable

from .utils import KeyT, _parse_into_words, ensure_unicode, load_file, write_file


class SpellChecker:
    """The SpellChecker class encapsulates the basics needed to accomplish a
    simple spell checking algorithm. It is based on the work by
    Peter Norvig (https://norvig.com/spell-correct.html)

    Args:
        language (str): The language of the dictionary to load or None for no dictionary. Supported languages are \
            `en`, `es`, `de`, `fr`, `pt`, `ru`, `lv`, and `eu`. Defaults to `en`. A list of languages may be provided and all \
                languages will be loaded.
        local_dictionary (str): The path to a locally stored word frequency dictionary; if provided, no language \
            will be loaded
        distance (int): The edit distance to use. Defaults to 2.
        case_sensitive (bool): Flag to use a case sensitive dictionary or not, only available when not using a \
            language dictionary.
    Note:
        Using a case sensitive dictionary can be slow to correct words."""

    __slots__ = ["_distance", "_word_frequency", "_tokenizer", "_case_sensitive"]

    def __init__(
        self,
        language: typing.Union[str, typing.Iterable[str]] = "en",
        local_dictionary: typing.Optional[str] = None,
        distance: int = 2,
        tokenizer: typing.Optional[typing.Callable[[str], typing.Iterable[str]]] = None,
        case_sensitive: bool = False,
    ) -> None:
        self._distance = 2  # default
        self.distance = distance  # use the setter value check

        if tokenizer:
            self._tokenizer = tokenizer
        else:
            self._tokenizer = _parse_into_words

        self._case_sensitive = case_sensitive if not language else False
        self._word_frequency = WordFrequency(self._tokenizer, self._case_sensitive)

        if local_dictionary:
            self._word_frequency.load_dictionary(local_dictionary)
        elif language:
            if not isinstance(language, Iterable) or isinstance(language, (str, bytes)):
                language = [language]  # type: ignore
            for lang in language:
                filename = f"resources/{lang.lower()}.json.gz"
                try:
                    json_open = pkgutil.get_data("spellchecker", filename)
                except FileNotFoundError as exc:
                    msg = f"The provided dictionary language ({lang.lower()}) does not exist!"
                    raise ValueError(msg) from exc
                if json_open:
                    lang_dict = json.loads(gzip.decompress(json_open).decode("utf-8"))
                self._word_frequency.load_json(lang_dict)

    def __contains__(self, key: KeyT) -> bool:
        """setup easier known checks"""
        key = ensure_unicode(key)
        return key in self._word_frequency

    def __getitem__(self, key: KeyT) -> int:
        """setup easier frequency checks"""
        key = ensure_unicode(key)
        return self._word_frequency[key]

    def __iter__(self) -> typing.Generator[str, None, None]:
        """setup iter support"""
        yield from self._word_frequency.dictionary

    @classmethod
    def languages(cls) -> typing.Iterable[str]:
        """list: A list of all official languages supported by the library"""
        return ["de", "en", "es", "fr", "pt", "ru", "ar", "lv", "eu"]

    @property
    def word_frequency(self) -> "WordFrequency":
        """WordFrequency: An encapsulation of the word frequency `dictionary`

        Note:
            Not settable"""
        return self._word_frequency

    @property
    def distance(self) -> int:
        """int: The maximum edit distance to calculate

        Note:
            Valid values are 1 or 2; if an invalid value is passed, defaults to 2"""
        return self._distance

    @distance.setter
    def distance(self, val: int) -> None:
        """set the distance parameter"""
        tmp = 2
        try:
            if 0 < int(val) <= 2:
                tmp = val
        except (ValueError, TypeError):
            pass
        self._distance = tmp

    def split_words(self, text: KeyT) -> typing.Iterable[str]:
        """Split text into individual `words` using either a simple whitespace
        regex or the passed in tokenizer

        Args:
            text (str): The text to split into individual words
        Returns:
            list(str): A listing of all words in the provided text"""
        text = ensure_unicode(text)
        return self._tokenizer(text)

    def export(self, filepath: str, encoding: str = "utf-8", gzipped: bool = True) -> None:
        """Export the word frequency list for import in the future

        Args:
           filepath (str): The filepath to the exported dictionary
           encoding (str): The encoding of the resulting output
           gzipped (bool): Whether to gzip the dictionary or not"""
        data = json.dumps(self.word_frequency.dictionary, sort_keys=True)
        write_file(filepath, encoding, gzipped, data)

    def word_usage_frequency(self, word: KeyT, total_words: typing.Optional[int] = None) -> float:
        """Calculate the frequency to the `word` provided as seen across the
        entire dictionary

        Args:
            word (str): The word for which the word probability is calculated
            total_words (int): The total number of words to use in the calculation; \
                use the default for using the whole word frequency
        Returns:
            float: The probability that the word is the correct word"""
        if not total_words:
            total_words = self._word_frequency.total_words
        word = ensure_unicode(word)
        return self._word_frequency.dictionary[word] / total_words

    def correction(self, word: KeyT) -> typing.Optional[str]:
        """The most probable correct spelling for the word

        Args:
            word (str): The word to correct
        Returns:
            str: The most likely candidate or None if no correction is present"""
        word = ensure_unicode(word)
        candidates = self.candidates(word)
        if not candidates:
            return None
        return max(sorted(list(candidates)), key=self.__getitem__)

    def candidates(self, word: KeyT) -> typing.Optional[typing.Set[str]]:
        """Generate possible spelling corrections for the provided word up to
        an edit distance of two, if and only when needed

        Args:
            word (str): The word for which to calculate candidate spellings
        Returns:
            set: The set of words that are possible candidates or None if there are no candidates"""
        word = ensure_unicode(word)
        if self.known([word]):  # short-cut if word is correct already
            return {word}

        if not self._check_if_should_check(word):
            return {word}

        # get edit distance 1...
        res = list(self.edit_distance_1(word))
        tmp = self.known(res)
        if tmp:
            return tmp
        # if still not found, use the edit distance 1 to calc edit distance 2
        if self._distance == 2:
            tmp = self.known(list(self.__edit_distance_alt(res)))
            if tmp:
                return tmp
        return None

    def known(self, words: typing.Iterable[KeyT]) -> typing.Set[str]:
        """The subset of `words` that appear in the dictionary of words

        Args:
            words (list): List of words to determine which are in the corpus
        Returns:
            set: The set of those words from the input that are in the corpus"""
        tmp_words = [ensure_unicode(w) for w in words]
        tmp = [w if self._case_sensitive else w.lower() for w in tmp_words]
        return {w for w in tmp if w in self._word_frequency.dictionary and self._check_if_should_check(w)}

    def unknown(self, words: typing.Iterable[KeyT]) -> typing.Set[str]:
        """The subset of `words` that do not appear in the dictionary

        Args:
            words (list): List of words to determine which are not in the corpus
        Returns:
            set: The set of those words from the input that are not in the corpus"""
        tmp_words = [ensure_unicode(w) for w in words]
        tmp = [w if self._case_sensitive else w.lower() for w in tmp_words if self._check_if_should_check(w)]
        return {w for w in tmp if w not in self._word_frequency.dictionary}

    def edit_distance_1(self, word: KeyT) -> typing.Set[str]:
        """Compute all strings that are one edit away from `word` using only
        the letters in the corpus

        Args:
            word (str): The word for which to calculate the edit distance
        Returns:
            set: The set of strings that are edit distance one from the provided word"""
        tmp_word = ensure_unicode(word).lower() if not self._case_sensitive else ensure_unicode(word)
        if self._check_if_should_check(tmp_word) is False:
            return {tmp_word}
        letters = self._word_frequency.letters
        splits = [(tmp_word[:i], tmp_word[i:]) for i in range(len(tmp_word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(self, word: KeyT) -> typing.List[str]:
        """Compute all strings that are two edits away from `word` using only
        the letters in the corpus

        Args:
            word (str): The word for which to calculate the edit distance
        Returns:
            set: The set of strings that are edit distance two from the provided word"""
        word = ensure_unicode(word).lower() if not self._case_sensitive else ensure_unicode(word)
        return [e2 for e1 in self.edit_distance_1(word) for e2 in self.edit_distance_1(e1)]

    def __edit_distance_alt(self, words: typing.Iterable[KeyT]) -> typing.List[str]:
        """Compute all strings that are 1 edits away from all the words using
        only the letters in the corpus

        Args:
            words (list): The words for which to calculate the edit distance
        Returns:
            set: The set of strings that are edit distance two from the provided words"""
        tmp_words = [ensure_unicode(w) for w in words]
        tmp = [w if self._case_sensitive else w.lower() for w in tmp_words if self._check_if_should_check(w)]
        return [e2 for e1 in tmp for e2 in self.known(self.edit_distance_1(e1))]

    def _check_if_should_check(self, word: str) -> bool:
        if len(word) == 1 and word in string.punctuation:
            return False
        if len(word) > self._word_frequency.longest_word_length + 3:  # allow removal of up to 2 letters
            return False
        if word.lower() == "nan":  # nan passes the float(word) so this will bypass that issue (#125)
            return True
        try:  # check if it is a number (int, float, etc)
            float(word)
            return False
        except ValueError:
            pass

        return True


class WordFrequency:
    """Store the `dictionary` as a word frequency list while allowing for
    different methods to load the data and update over time"""

    __slots__ = [
        "_dictionary",
        "_total_words",
        "_unique_words",
        "_letters",
        "_tokenizer",
        "_case_sensitive",
        "_longest_word_length",
    ]

    def __init__(self, tokenizer=None, case_sensitive=False):
        self._dictionary = Counter()
        self._total_words = 0
        self._unique_words = 0
        self._letters = set()
        self._case_sensitive = case_sensitive
        self._longest_word_length = 0

        self._tokenizer = _parse_into_words
        if tokenizer is not None:
            self._tokenizer = tokenizer

    def __contains__(self, key: KeyT) -> bool:
        """turn on contains"""
        key = ensure_unicode(key)
        key = key if self._case_sensitive else key.lower()
        return key in self._dictionary

    def __getitem__(self, key: KeyT) -> int:
        """turn on getitem"""
        key = ensure_unicode(key)
        key = key if self._case_sensitive else key.lower()
        return self._dictionary[key]

    def __iter__(self) -> typing.Generator[str, None, None]:
        """turn on iter support"""
        yield from self._dictionary

    def pop(self, key: KeyT, default: typing.Optional[int] = None) -> int:
        """Remove the key and return the associated value or default if not
        found

        Args:
            key (str): The key to remove
            default (obj): The value to return if key is not present"""
        key = ensure_unicode(key)
        return self._dictionary.pop(key if self._case_sensitive else key.lower(), default)

    @property
    def dictionary(self) -> typing.Dict[str, int]:
        """Counter: A counting dictionary of all words in the corpus and the number
        of times each has been seen

        Note:
            Not settable"""
        return self._dictionary

    @property
    def total_words(self) -> int:
        """int: The sum of all word occurances in the word frequency dictionary

        Note:
            Not settable"""
        return self._total_words

    @property
    def unique_words(self) -> int:
        """int: The total number of unique words in the word frequency list

        Note:
            Not settable"""
        return self._unique_words

    @property
    def letters(self) -> typing.Set[str]:
        """set: The listing of all letters found within the corpus

        Note:
            Not settable"""
        return self._letters

    @property
    def longest_word_length(self) -> int:
        """int: The longest word length in the dictionary

        Note:
            Not settable"""
        return self._longest_word_length

    def tokenize(self, text: KeyT) -> typing.Generator[str, None, None]:
        """Tokenize the provided string object into individual words

        Args:
            text (str): The string object to tokenize
        Yields:
            str: The next `word` in the tokenized string
        Note:
            This is the same as the `spellchecker.split_words()` unless a tokenizer function was provided."""
        tmp_text = ensure_unicode(text)
        for word in self._tokenizer(tmp_text):
            yield word if self._case_sensitive else word.lower()

    def keys(self) -> typing.Generator[str, None, None]:
        """Iterator over the key of the dictionary

        Yields:
            str: The next key in the dictionary
        Note:
            This is the same as `spellchecker.words()`"""
        yield from self._dictionary.keys()

    def words(self) -> typing.Generator[str, None, None]:
        """Iterator over the words in the dictionary

        Yields:
            str: The next word in the dictionary
        Note:
            This is the same as `spellchecker.keys()`"""
        yield from self._dictionary.keys()

    def items(self) -> typing.Generator[typing.Tuple[str, int], None, None]:
        """Iterator over the words in the dictionary

        Yields:
            str: The next word in the dictionary
            int: The number of instances in the dictionary
        Note:
            This is the same as `dict.items()`"""
        yield from self._dictionary.items()

    def load_dictionary(self, filename: str, encoding: str = "utf-8") -> None:
        """Load in a pre-built word frequency list

        Args:
            filename (str): The filepath to the json (optionally gzipped) file to be loaded
            encoding (str): The encoding of the dictionary"""
        with load_file(filename, encoding) as data:
            data = data if self._case_sensitive else data.lower()
            self._dictionary.update(json.loads(data))
            self._update_dictionary()

    def load_json(self, data: typing.Dict[str, int]) -> None:
        """Load in a pre-built word frequency list

        Args:
            data (dict): The dictionary to be loaded"""
        self._dictionary.update(data)
        self._update_dictionary()

    def load_text_file(
        self,
        filename: str,
        encoding: str = "utf-8",
        tokenizer: typing.Optional[typing.Callable[[str], typing.Iterable[str]]] = None,
    ) -> None:
        """Load in a text file from which to generate a word frequency list

        Args:
            filename (str): The filepath to the text file to be loaded
            encoding (str): The encoding of the text file
            tokenizer (function): The function to use to tokenize a string
        """
        with load_file(filename, encoding=encoding) as data:
            self.load_text(data, tokenizer)

    def load_text(
        self,
        text: KeyT,
        tokenizer: typing.Optional[typing.Callable[[str], typing.Iterable[str]]] = None,
    ) -> None:
        """Load text from which to generate a word frequency list

        Args:
            text (str): The text to be loaded
            tokenizer (function): The function to use to tokenize a string
        """
        text = ensure_unicode(text)
        if tokenizer:
            words = [x if self._case_sensitive else x.lower() for x in tokenizer(text)]
        else:
            words = self.tokenize(text)  # type: ignore

        self._dictionary.update(words)
        self._update_dictionary()

    def load_words(self, words: typing.Iterable[KeyT]) -> None:
        """Load a list of words from which to generate a word frequency list

        Args:
            words (list): The list of words to be loaded"""
        words = [ensure_unicode(w) for w in words]
        self._dictionary.update([word if self._case_sensitive else word.lower() for word in words])
        self._update_dictionary()

    def add(self, word: KeyT, val: int = 1) -> None:
        """Add a word to the word frequency list

        Args:
            word (str): The word to add
            val (int): The number of times to insert the word"""
        word = ensure_unicode(word)
        self.load_json({word if self._case_sensitive else word.lower(): val})

    def remove_words(self, words: typing.Iterable[KeyT]) -> None:
        """Remove a list of words from the word frequency list

        Args:
            words (list): The list of words to remove"""
        words = [ensure_unicode(w) for w in words]
        for word in words:
            self.pop(word)
        self._update_dictionary()

    def remove(self, word: KeyT) -> None:
        """Remove a word from the word frequency list

        Args:
            word (str): The word to remove"""
        self.pop(word)
        self._update_dictionary()

    def remove_by_threshold(self, threshold: int = 5) -> None:
        """Remove all words at, or below, the provided threshold

        Args:
            threshold (int): The threshold at which a word is to be removed"""
        to_remove = [k for k, v in self._dictionary.items() if v <= threshold]
        self.remove_words(to_remove)

    def _update_dictionary(self) -> None:
        """Update the word frequency object"""
        self._longest_word_length = 0
        self._total_words = sum(self._dictionary.values())
        self._unique_words = len(self._dictionary.keys())
        self._letters = set()
        for key in self._dictionary:
            if len(key) > self._longest_word_length:
                self._longest_word_length = len(key)
            self._letters.update(key)
