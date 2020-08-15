""" SpellChecker Module; simple, intuitive spell checker based on the post by
    Peter Norvig. See: https://norvig.com/spell-correct.html """
from __future__ import absolute_import, division, unicode_literals

import os
import json
import string
from collections import Counter

from .utils import load_file, write_file, _parse_into_words, ENSURE_UNICODE


class SpellChecker(object):
    """ The SpellChecker class encapsulates the basics needed to accomplish a
        simple spell checking algorithm. It is based on the work by
        Peter Norvig (https://norvig.com/spell-correct.html)

        Args:
            language (str): The language of the dictionary to load or None \
            for no dictionary. Supported languages are `en`, `es`, `de`, `fr` \
            and `pt`. Defaults to `en`
            local_dictionary (str): The path to a locally stored word \
            frequency dictionary; if provided, no language will be loaded
            distance (int): The edit distance to use. Defaults to 2.
            case_sensitive (bool): Flag to use a case sensitive dictionary or \
            not, only available when not using a language dictionary.
        Note:
            Using a case sensitive dictionary can be slow to correct words."""

    __slots__ = ["_distance", "_word_frequency", "_tokenizer", "_case_sensitive"]

    def __init__(
        self,
        language="en",
        local_dictionary=None,
        distance=2,
        tokenizer=None,
        case_sensitive=False,
    ):
        self._distance = None
        self.distance = distance  # use the setter value check

        self._tokenizer = _parse_into_words
        if tokenizer is not None:
            self._tokenizer = tokenizer

        self._case_sensitive = case_sensitive if not language else False
        self._word_frequency = WordFrequency(self._tokenizer, self._case_sensitive)

        if local_dictionary:
            self._word_frequency.load_dictionary(local_dictionary)
        elif language:
            filename = "{}.json.gz".format(language.lower())
            here = os.path.dirname(__file__)
            full_filename = os.path.join(here, "resources", filename)
            if not os.path.exists(full_filename):
                msg = (
                    "The provided dictionary language ({}) does not " "exist!"
                ).format(language.lower())
                raise ValueError(msg)
            self._word_frequency.load_dictionary(full_filename)

    def __contains__(self, key):
        """ setup easier known checks """
        key = ENSURE_UNICODE(key)
        return key in self._word_frequency

    def __getitem__(self, key):
        """ setup easier frequency checks """
        key = ENSURE_UNICODE(key)
        return self._word_frequency[key]

    @property
    def word_frequency(self):
        """ WordFrequency: An encapsulation of the word frequency `dictionary`

            Note:
                Not settable """
        return self._word_frequency

    @property
    def distance(self):
        """ int: The maximum edit distance to calculate

            Note:
                Valid values are 1 or 2; if an invalid value is passed, \
                defaults to 2 """
        return self._distance

    @distance.setter
    def distance(self, val):
        """ set the distance parameter """
        tmp = 2
        try:
            int(val)
            if val > 0 and val <= 2:
                tmp = val
        except (ValueError, TypeError):
            pass
        self._distance = tmp

    def split_words(self, text):
        """ Split text into individual `words` using either a simple whitespace
            regex or the passed in tokenizer

            Args:
                text (str): The text to split into individual words
            Returns:
                list(str): A listing of all words in the provided text """
        text = ENSURE_UNICODE(text)
        return self._tokenizer(text)

    def export(self, filepath, encoding="utf-8", gzipped=True):
        """ Export the word frequency list for import in the future

             Args:
                filepath (str): The filepath to the exported dictionary
                encoding (str): The encoding of the resulting output
                gzipped (bool): Whether to gzip the dictionary or not """
        data = json.dumps(self.word_frequency.dictionary, sort_keys=True)
        write_file(filepath, encoding, gzipped, data)

    def word_probability(self, word, total_words=None):
        """ Calculate the probability of the `word` being the desired, correct
            word

            Args:
                word (str): The word for which the word probability is \
                calculated
                total_words (int): The total number of words to use in the \
                calculation; use the default for using the whole word \
                frequency
            Returns:
                float: The probability that the word is the correct word """
        if total_words is None:
            total_words = self._word_frequency.total_words
        word = ENSURE_UNICODE(word)
        return self._word_frequency.dictionary[word] / total_words

    def correction(self, word):
        """ The most probable correct spelling for the word

            Args:
                word (str): The word to correct
            Returns:
                str: The most likely candidate """
        word = ENSURE_UNICODE(word)
        candidates = list(self.candidates(word))
        return max(sorted(candidates), key=self.word_probability)

    def candidates(self, word):
        """ Generate possible spelling corrections for the provided word up to
            an edit distance of two, if and only when needed

            Args:
                word (str): The word for which to calculate candidate spellings
            Returns:
                set: The set of words that are possible candidates """
        word = ENSURE_UNICODE(word)
        if self.known([word]):  # short-cut if word is correct already
            return {word}

        if not self._check_if_should_check(word):
            return {word}

        # get edit distance 1...
        res = [x for x in self.edit_distance_1(word)]
        tmp = self.known(res)
        if tmp:
            return tmp
        # if still not found, use the edit distance 1 to calc edit distance 2
        if self._distance == 2:
            tmp = self.known([x for x in self.__edit_distance_alt(res)])
            if tmp:
                return tmp
        return {word}

    def known(self, words):
        """ The subset of `words` that appear in the dictionary of words

            Args:
                words (list): List of words to determine which are in the \
                corpus
            Returns:
                set: The set of those words from the input that are in the \
                corpus """
        words = [ENSURE_UNICODE(w) for w in words]
        tmp = [w if self._case_sensitive else w.lower() for w in words]
        return set(
            w
            for w in tmp
            if w in self._word_frequency.dictionary
            and self._check_if_should_check(w)
        )

    def unknown(self, words):
        """ The subset of `words` that do not appear in the dictionary

            Args:
                words (list): List of words to determine which are not in the \
                corpus
            Returns:
                set: The set of those words from the input that are not in \
                the corpus """
        words = [ENSURE_UNICODE(w) for w in words]
        tmp = [
            w if self._case_sensitive else w.lower()
            for w in words
            if self._check_if_should_check(w)
        ]
        return set(w for w in tmp if w not in self._word_frequency.dictionary)

    def edit_distance_1(self, word):
        """ Compute all strings that are one edit away from `word` using only
            the letters in the corpus

            Args:
                word (str): The word for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance one from the \
                provided word """
        word = ENSURE_UNICODE(word).lower() if not self._case_sensitive else ENSURE_UNICODE(word)
        if self._check_if_should_check(word) is False:
            return {word}
        letters = self._word_frequency.letters
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(self, word):
        """ Compute all strings that are two edits away from `word` using only
            the letters in the corpus

            Args:
                word (str): The word for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance two from the \
                provided word """
        word = ENSURE_UNICODE(word).lower() if not self._case_sensitive else ENSURE_UNICODE(word)
        return [
            e2 for e1 in self.edit_distance_1(word) for e2 in self.edit_distance_1(e1)
        ]

    def __edit_distance_alt(self, words):
        """ Compute all strings that are 1 edits away from all the words using
            only the letters in the corpus

            Args:
                words (list): The words for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance two from the \
                provided words """
        words = [ENSURE_UNICODE(w) for w in words]
        tmp = [
            w if self._case_sensitive else w.lower()
            for w in words
            if self._check_if_should_check(w)
        ]
        return [e2 for e1 in tmp for e2 in self.known(self.edit_distance_1(e1))]

    def _check_if_should_check(self, word):
        if len(word) == 1 and word in string.punctuation:
            return False
        if len(word) > self._word_frequency.longest_word_length + 3:  # magic number to allow removal of up to 2 letters.
            return False
        try:  # check if it is a number (int, float, etc)
            float(word)
            return False
        except ValueError:
            pass

        return True


class WordFrequency(object):
    """ Store the `dictionary` as a word frequency list while allowing for
        different methods to load the data and update over time """

    __slots__ = [
        "_dictionary",
        "_total_words",
        "_unique_words",
        "_letters",
        "_tokenizer",
        "_case_sensitive",
        "_longest_word_length"
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

    def __contains__(self, key):
        """ turn on contains """
        key = ENSURE_UNICODE(key)
        key = key if self._case_sensitive else key.lower()
        return key in self._dictionary

    def __getitem__(self, key):
        """ turn on getitem """
        key = ENSURE_UNICODE(key)
        key = key if self._case_sensitive else key.lower()
        return self._dictionary[key]

    def pop(self, key, default=None):
        """ Remove the key and return the associated value or default if not
            found

            Args:
                key (str): The key to remove
                default (obj): The value to return if key is not present """
        key = ENSURE_UNICODE(key)
        key = key if self._case_sensitive else key.lower()
        return self._dictionary.pop(key, default)

    @property
    def dictionary(self):
        """ Counter: A counting dictionary of all words in the corpus and the \
            number of times each has been seen

            Note:
                Not settable """
        return self._dictionary

    @property
    def total_words(self):
        """ int: The sum of all word occurances in the word frequency \
                 dictionary

            Note:
                Not settable """
        return self._total_words

    @property
    def unique_words(self):
        """ int: The total number of unique words in the word frequency list

            Note:
                Not settable """
        return self._unique_words

    @property
    def letters(self):
        """ str: The listing of all letters found within the corpus

            Note:
                Not settable """
        return self._letters

    @property
    def longest_word_length(self):
        """ int: The longest word length in the dictionary

            Note:
                Not settable """
        return self._longest_word_length

    def tokenize(self, text):
        """ Tokenize the provided string object into individual words

            Args:
                text (str): The string object to tokenize
            Yields:
                str: The next `word` in the tokenized string
            Note:
                This is the same as the `spellchecker.split_words()` """
        text = ENSURE_UNICODE(text)
        for word in self._tokenizer(text):
            yield word if self._case_sensitive else word.lower()

    def keys(self):
        """ Iterator over the key of the dictionary

            Yields:
                str: The next key in the dictionary
            Note:
                This is the same as `spellchecker.words()` """
        for key in self._dictionary.keys():
            yield key

    def words(self):
        """ Iterator over the words in the dictionary

            Yields:
                str: The next word in the dictionary
            Note:
                This is the same as `spellchecker.keys()` """
        for word in self._dictionary.keys():
            yield word

    def items(self):
        """ Iterator over the words in the dictionary

            Yields:
                str: The next word in the dictionary
                int: The number of instances in the dictionary
            Note:
                This is the same as `dict.items()` """
        for word in self._dictionary.keys():
            yield word, self._dictionary[word]

    def load_dictionary(self, filename, encoding="utf-8"):
        """ Load in a pre-built word frequency list

            Args:
                filename (str): The filepath to the json (optionally gzipped) \
                file to be loaded
                encoding (str): The encoding of the dictionary """
        with load_file(filename, encoding) as data:
            data = data if self._case_sensitive else data.lower()
            self._dictionary.update(json.loads(data))
            self._update_dictionary()

    def load_text_file(self, filename, encoding="utf-8", tokenizer=None):
        """ Load in a text file from which to generate a word frequency list

            Args:
                filename (str): The filepath to the text file to be loaded
                encoding (str): The encoding of the text file
                tokenizer (function): The function to use to tokenize a string
        """
        with load_file(filename, encoding=encoding) as data:
            self.load_text(data, tokenizer)

    def load_text(self, text, tokenizer=None):
        """ Load text from which to generate a word frequency list

            Args:
                text (str): The text to be loaded
                tokenizer (function): The function to use to tokenize a string
        """
        text = ENSURE_UNICODE(text)
        if tokenizer:
            words = [x if self._case_sensitive else x.lower() for x in tokenizer(text)]
        else:
            words = self.tokenize(text)

        self._dictionary.update(words)
        self._update_dictionary()

    def load_words(self, words):
        """ Load a list of words from which to generate a word frequency list

            Args:
                words (list): The list of words to be loaded """
        words = [ENSURE_UNICODE(w) for w in words]
        self._dictionary.update(
            [word if self._case_sensitive else word.lower() for word in words]
        )
        self._update_dictionary()

    def add(self, word):
        """ Add a word to the word frequency list

            Args:
                word (str): The word to add """
        word = ENSURE_UNICODE(word)
        self.load_words([word])

    def remove_words(self, words):
        """ Remove a list of words from the word frequency list

            Args:
                words (list): The list of words to remove """
        words = [ENSURE_UNICODE(w) for w in words]
        for word in words:
            self._dictionary.pop(word if self._case_sensitive else word.lower())
        self._update_dictionary()

    def remove(self, word):
        """ Remove a word from the word frequency list

            Args:
                word (str): The word to remove """
        word = ENSURE_UNICODE(word)
        self._dictionary.pop(word if self._case_sensitive else word.lower())
        self._update_dictionary()

    def remove_by_threshold(self, threshold=5):
        """ Remove all words at, or below, the provided threshold

            Args:
                threshold (int): The threshold at which a word is to be \
                removed """
        keys = [x for x in self._dictionary.keys()]
        for key in keys:
            if self._dictionary[key] <= threshold:
                self._dictionary.pop(key)
        self._update_dictionary()

    def _update_dictionary(self):
        """ Update the word frequency object """
        self._longest_word_length = 0
        self._total_words = sum(self._dictionary.values())
        self._unique_words = len(self._dictionary.keys())
        self._letters = set()
        for key in self._dictionary:
            if len(key) > self._longest_word_length:
                self._longest_word_length = len(key)
            self._letters.update(key)
