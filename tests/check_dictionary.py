""" Check for common errors in the dictionary """

import unittest
import os
import sys

sys.path.append("..")

from spellchecker import SpellChecker

spell = SpellChecker(distance=1)
freq_ratios = {}
for w in sys.stdin :
    if not w.startswith('"') :
        continue
    w = w[1:w.find('"', 1)]

    # spell check this work, using other words in the dictionary
    corr = spell.ranked_candidates(w, always=True)[0]
    freq_w    = spell.__getitem__(w)
    freq_corr = spell.__getitem__(corr)

    # if this word is less common than a candidate correction, report that
    if freq_w < freq_corr :
      freq_ratios[w] = (freq_w/freq_corr, corr)

for w in sorted (freq_ratios, key = lambda x: freq_ratios[x]) :
    print (w, freq_ratios[w][1], freq_ratios[w][0])
