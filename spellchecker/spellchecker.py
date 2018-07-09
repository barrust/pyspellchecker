''' SpellChecker Module; simple, intuitive spell checker based on the post by
    Peter Norvig. See: https://norvig.com/spell-correct.html '''
from __future__ import absolute_import, division, unicode_literals

import os
import re
import json
import gzip
import string
from collections import Counter


class SpellChecker(object):
    ''' The SpellChecker class encapsulates the basics needed to accomplish a
        simple spell checking algorithm. It is based on the work by
        Peter Norvig (https://norvig.com/spell-correct.html)

        Args:
            language (str): The language of the dictionary to load or None \
            for no dictionary. Supported languages are `en`, `es`, `de`, and \
            `fr`. Defaults to `en`
            local_dictionary (str): The path to a locally stored word \
            frequency dictionary '''

    def __init__(self, language='en', local_dictionary=None):
        self._word_frequency = WordFrequency()
        if local_dictionary:
            self._word_frequency.load_dictionary(local_dictionary)
        if language:
            filename = '{}.json.gz'.format(language)
            here = os.path.dirname(__file__)
            full_filename = os.path.join(here, 'resources', filename)
            if not os.path.exists(full_filename):
                msg = ('The provided dictionary language ({}) does not '
                       'exist!').format(language)
                raise ValueError(msg)
            self._word_frequency.load_dictionary(full_filename)

    def __contains__(self, key):
        ''' setup easier known checks '''
        return key in self._word_frequency

    def __getitem__(self, key):
        ''' setup easier frequency checks '''
        return self._word_frequency[key]

    @property
    def word_frequency(self):
        ''' WordFrequency: An encapsulation of the word frequency `dictionary`

            Note:
                Not settable '''
        return self._word_frequency

    @staticmethod
    def words(text):
        ''' Split text into individual `words` using a simple whitespace regex

            Args:
                text (str): The text to split into individual words
            Returns:
                list(str): A listing of all words in the provided text '''
        return _words(text)

    def word_probability(self, word, total_words=None):
        ''' Calculate the probability of the `word` being the desired, correct
            word

            Args:
                word (str): The word for which the word probability is \
                calculated
                total_words (int): The total number of words to use in the \
                calculation; use the default for using the whole word \
                frequency
            Returns:
                float: The probability that the word is the correct word '''
        if total_words is None:
            total_words = self._word_frequency.total_words
        return self._word_frequency.dictionary[word] / total_words

    def correction(self, word):
        ''' The most probable correct spelling for the word

            Args:
                word (str): The word to correct
            Returns:
                str: The most likely candidate '''
        return max(self.candidates(word), key=self.word_probability)

    def candidates(self, word):
        ''' Generate possible spelling corrections for the provided word up to
            an edit distance of two, if and only when needed

            Args:
                word (str): The word for which to calculate candidate spellings
            Returns:
                set: The set of words that are possible candidates '''
        return (self.known([word]) or self.known(self.edit_distance_1(word)) or
                self.known(self.edit_distance_2(word)) or {word})

    def known(self, words):
        ''' The subset of `words` that appear in the dictionary of words

            Args:
                words (list): List of words to determine which are in the \
                corpus
            Returns:
                set: The set of those words from the input that are in the \
                corpus '''
        return set(w for w in words if w in self._word_frequency.dictionary or
                   not self._check_if_should_check(w))

    def unknown(self, words):
        ''' The subset of `words` that do not appear in the dictionary

            Args:
                words (list): List of words to determine which are not in the \
                corpus
            Returns:
                set: The set of those words from the input that are not in \
                the corpus '''
        tmp = [w for w in words if self._check_if_should_check(w)]
        return set(w for w in tmp if w not in self._word_frequency.dictionary)

    def edit_distance_1(self, word):
        ''' Compute all strings that are one edit away from `word` using only
            the letters in the corpus

            Args:
                word (str): The word for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance two from the \
                provided word '''
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
        ''' Compute all strings that are two edits away from `word` using only
            the letters in the corpus

            Args:
                word (str): The word for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance one from the \
                provided word '''
        return (e2 for e1 in self.edit_distance_1(word)
                for e2 in self.edit_distance_1(e1))

    @staticmethod
    def _check_if_should_check(word):
        if len(word) == 1 and word in string.punctuation:
            return False
        try:  # check if it is a number (int, float, etc)
            float(word)
            return False
        except ValueError:
            pass

        return True

class WordFrequency(object):
    ''' Store the `dictionary` as a word frequency list while allowing for
        different methods to load the data and update over time '''

    def __init__(self):
        self._dictionary = Counter()
        self._total_words = 0
        self._unique_words = 0
        self._letters = set()

    def __contains__(self, key):
        ''' turn on contains '''
        return key in self._dictionary

    def __getitem__(self, key):
        ''' turn on getitem '''
        return self._dictionary[key]

    @property
    def dictionary(self):
        ''' Counter: A counting dictionary of all words in the corpus and the \
            number of times each has been seen

            Note:
                Not settable '''
        return self._dictionary

    @property
    def total_words(self):
        ''' int: The sum of all word occurances in the word frequency \
                 dictionary

            Note:
                Not settable '''
        return self._total_words

    @property
    def unique_words(self):
        ''' int: The total number of unique words in the word frequency list

            Note:
                Not settable '''
        return self._unique_words

    @property
    def letters(self):
        ''' str: The listing of all letters found within the corpus

            Note:
                Not settable '''
        return self._letters

    def load_dictionary(self, filename):
        ''' Load in a pre-built word frequency list

            Args:
                filename (str): The filepath to the json (optionally gzipped) \
                file to be loaded '''
        try:
            with gzip.open(filename, 'rt') as fobj:
                data = fobj.read().lower()
        except OSError:
            with open(filename, 'r') as fobj:
                data = fobj.read().lower()
        self._dictionary.update(json.loads(data, encoding='utf8'))
        self._update_dictionary()

    def load_text_file(self, filename):
        ''' Load in a text file from which to generate a word frequency list

            Args:
                filename (str): The filepath to the text file to be loaded '''
        with open(filename, 'r') as fobj:
            self.load_text(fobj.read())

    def load_text(self, text):
        ''' Load text from which to generate a word frequency list

            Args:
                text (str): The text to be loaded '''
        self._dictionary.update(_words(text))
        self._update_dictionary()

    def load_words(self, words):
        ''' Load a list of words from which to generate a word frequency list

            Args:
                text (list): The list of words to be loaded '''
        self._dictionary.update([word.lower() for word in words])
        self._update_dictionary()

    def _update_dictionary(self):
        ''' Update the word frequency object '''
        self._total_words = sum(self._dictionary.values())
        self._unique_words = len(self._dictionary.keys())
        self._letters = set()
        for key in self._dictionary:
            self._letters.update(key)


def _words(text):
    ''' Parse the text into words; currently removes punctuation '''
    return re.findall(r'\w+', text.lower())
