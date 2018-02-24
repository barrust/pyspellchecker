# -*- coding: utf-8 -*-
'''
Unittest class
'''
import unittest

from spellchecker import SpellChecker


class TestSpellChecker(unittest.TestCase):
    def test_correction(self):
        ''' test spell checker corrections '''
        spell = SpellChecker()
        self.assertEqual(spell.correction('ths'), 'the')
        self.assertEqual(spell.correction('ergo'), 'ergot')
        self.assertEqual(spell.correction('this'), 'this')

    def test_candidates(self):
        ''' test spell checker candidates '''
        spell = SpellChecker()
        self.assertEqual(spell.candidates('ths'), {'tis', 'tss', 'th', 'thus', 'the', 'this', 'thy'})
        self.assertEqual(spell.candidates('the'), {'the'})

    def test_words(self):
        spell = SpellChecker()
        self.assertEqual(spell.words('This is a test of this'), ['this', 'is', 'a', 'test', 'of', 'this'])

    def test_word_frequency(self):
        spell = SpellChecker()
        # if the default load changes so will this...
        self.assertEqual(spell.word_frequency.dictionary['the'], 79809)

    def test_word_probability(self):
        spell = SpellChecker()
        # if the default load changes so will this...
        self.assertEqual(spell.word_probability('the'), 0.07154004401278254)

    def test_word_known(self):
        ''' test if the word is a `known` word or not '''
        spell = SpellChecker()
        self.assertEqual(spell.known(['this']), {'this'})
        self.assertEqual(spell.known(['sherlock']), {'sherlock'})
        self.assertEqual(spell.known(['holmes']), {'holmes'})
        self.assertEqual(spell.known(['known']), {'known'})

        self.assertEqual(spell.known(['foobar']), set())
        self.assertEqual(spell.known(['ths']), set())
        self.assertEqual(spell.known(['ergo']), set())

    def test_unknown_words(self):
        spell = SpellChecker()
        self.assertEqual(spell.unknown(['this']), set())
        self.assertEqual(spell.unknown(['sherlock']), set())
        self.assertEqual(spell.unknown(['holmes']), set())
        self.assertEqual(spell.unknown(['known']), set())

        self.assertEqual(spell.unknown(['foobar']), {'foobar'})
        self.assertEqual(spell.unknown(['ths']), {'ths'})
        self.assertEqual(spell.unknown(['ergo']), {'ergo'})
