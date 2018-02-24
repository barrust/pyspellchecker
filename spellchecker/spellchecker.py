from __future__ import absolute_import

import os
import re
from collections import Counter

import spellchecker.info as base  # to get a relative file path!


class SpellChecker(object):

    def __init__(self):
        # Should allow passing in a different file
        dirpath = os.path.dirname(base.__file__)
        full_filename = os.path.join(dirpath, 'resources', 'old_books.txt')
        self.dictionary = None
        with open(full_filename) as fobj:
            self.dictionary = Counter(self.words(fobj.read()))

    def words(self, text):
        return re.findall(r'\w+', text.lower())

    def P(self, word, N=None):
        "Probability of `word`."
        if N is None:
            N = sum(self.dictionary.values())
        return self.dictionary[word] / N

    def correction(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edit_distance_1(word)) or self.known(self.edit_distance_2(word)) or [word])

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.dictionary)

    def edit_distance_1(self, word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edit_distance_1(word) for e2 in self.edit_distance_1(e1))
