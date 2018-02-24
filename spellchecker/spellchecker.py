''' SpellChecker Module; simple, intuitive spell checker based on the post by
    Peter Norvig. See: https://norvig.com/spell-correct.html '''
from __future__ import absolute_import

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
        self.dictionary = Counter()
        with open(full_filename) as fobj:
            self.dictionary.update(self.words(fobj.read()))
        self.total_words = sum(self.dictionary.values())

    @staticmethod
    def words(text):
        ''' Parse the text into words; currently removes punctuation '''
        return re.findall(r'\w+', text.lower())

    def word_probability(self, word, total_words=None):
        "Probability of `word` being the desired word"
        if total_words is None:
            total_words = self.total_words
        return self.dictionary[word] / total_words

    def correction(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.word_probability)

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edit_distance_1(word)) or
                self.known(self.edit_distance_2(word)) or [word])

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.dictionary)

    def unknown(self, words):
        ''' The subset of `words` that do not appear in the dictionary'''
        return set(w for w in words if w not in self.dictionary)

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
