''' SpellChecker Module; simple, intuitive spell checker based on the post by
    Peter Norvig. See: https://norvig.com/spell-correct.html '''
from __future__ import absolute_import, division

import os
import re
import string
from collections import Counter

import spellchecker.info as base


class SpellChecker(object):
    ''' The SpellChecker class encapsulates the basics needed to accomplish a
        simple spell checking algorithm. It is based on the work by
        Peter Norvig (https://norvig.com/spell-correct.html) '''

    def __init__(self):
        # Should allow passing in a different file
        dirpath = os.path.dirname(base.__file__)
        full_filename = os.path.join(dirpath, 'resources', 'old_books.txt')
        self.word_frequency = WordFrequency()
        self.word_frequency.load_text_file(full_filename)

    @staticmethod
    def words(text):
        ''' split text into individual `words` '''
        return _words(text)

    def word_probability(self, word, total_words=None):
        "Probability of `word` being the desired word"
        if total_words is None:
            total_words = self.word_frequency.total_words
        return self.word_frequency.dictionary[word] / total_words

    def correction(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.word_probability)

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edit_distance_1(word)) or
                self.known(self.edit_distance_2(word)) or [word])

    def known(self, words):
        "The subset of `words` that appear in the dictionary of words."
        return set(w for w in words if w in self.word_frequency.dictionary)

    def unknown(self, words):
        ''' The subset of `words` that do not appear in the dictionary'''
        return set(w for w in words if w not in self.word_frequency.dictionary)

    @staticmethod
    def edit_distance_1(word):
        "All edits that are one edit away from `word`."
        letters = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(self, word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edit_distance_1(word)
                for e2 in self.edit_distance_1(e1))


class WordFrequency(object):
    ''' Private-like class to store the `dictionary` allowing for different
        methods to load the data and update over time '''

    def __init__(self):
        self.dictionary = Counter()
        self.total_words = 0

    def load_text_file(self, filename):
        ''' Load a text file to calculate the word frequencies '''
        with open(filename) as fobj:
            self.dictionary.update(_words(fobj.read()))
        self.total_words = sum(self.dictionary.values())

    def load_text(self, text):
        ''' Load text to calculate the word frequencies '''
        self.dictionary.update(_words(text))
        self.total_words = sum(self.dictionary.values())

    def load_words(self, words):
        ''' Load a list of words to calculate word frequencies '''
        self.dictionary.update(words)
        self.total_words = sum(self.dictionary.values())


def _words(text):
    ''' Parse the text into words; currently removes punctuation '''
    return re.findall(r'\w+', text.lower())
