# -*- coding: utf-8 -*-
''' Unittest class '''
from __future__ import division

import unittest

from spellchecker import SpellChecker


class TestSpellChecker(unittest.TestCase):
    def test_correction(self):
        ''' test spell checker corrections '''
        spell = SpellChecker()
        self.assertEqual(spell.correction('ths'), 'the')
        self.assertEqual(spell.correction('ergo'), 'ergo')
        self.assertEqual(spell.correction('alot'), 'a lot')
        self.assertEqual(spell.correction('this'), 'this')

    def test_candidates(self):
        ''' test spell checker candidates '''
        spell = SpellChecker()
        cands = {'tes', 'tps', 'th', 'thi', 'tvs', 'tds', 'tbs', 'bhs', 'thf',
                 'chs', 'tis', 'thes', 'tls', 'tho', 'thu', 'thr', 'dhs',
                 "th'", 'thus', 'ts', 'ehs', 'tas', 'ahs', 'thos', 'thy',
                 'tcs', 'nhs', 'the', 'tss', 'hs', 'lhs', 'vhs', "t's", 'tha',
                 'whs', 'ghs', 'rhs', 'this'}
        self.assertEqual(spell.candidates('ths'), cands)
        self.assertEqual(spell.candidates('the'), {'the'})

    def test_words(self):
        spell = SpellChecker()
        res = ['this', 'is', 'a', 'test', 'of', 'this']
        self.assertEqual(spell.words('This is a test of this'), res)

    def test_word_frequency(self):
        spell = SpellChecker()
        # if the default load changes so will this...
        self.assertEqual(spell.word_frequency['the'], 6187925)

    def test_word_probability(self):
        spell = SpellChecker()
        # if the default load changes so will this...
        num = spell.word_frequency['the']
        denom = spell.word_frequency.total_words
        self.assertEqual(spell.word_probability('the'), num / denom)

    def test_word_known(self):
        ''' test if the word is a `known` word or not '''
        spell = SpellChecker()
        self.assertEqual(spell.known(['this']), {'this'})
        self.assertEqual(spell.known(['sherlock']), {'sherlock'})
        self.assertEqual(spell.known(['holmes']), {'holmes'})
        self.assertEqual(spell.known(['known']), {'known'})

        self.assertEqual(spell.known(['foobar']), set())
        self.assertEqual(spell.known(['ths']), set())
        self.assertEqual(spell.known(['ergos']), set())

    def test_unknown_words(self):
        spell = SpellChecker()
        self.assertEqual(spell.unknown(['this']), set())
        self.assertEqual(spell.unknown(['sherlock']), set())
        self.assertEqual(spell.unknown(['holmes']), set())
        self.assertEqual(spell.unknown(['known']), set())

        self.assertEqual(spell.unknown(['foobar']), {'foobar'})
        self.assertEqual(spell.unknown(['ths']), {'ths'})
        self.assertEqual(spell.unknown(['ergos']), {'ergos'})
