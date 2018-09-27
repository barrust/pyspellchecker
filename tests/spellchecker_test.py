''' Unittest class '''
from __future__ import division

import unittest
import os

from spellchecker import SpellChecker


class TestSpellChecker(unittest.TestCase):
    ''' test the spell checker class '''

    def test_correction(self):
        ''' test spell checker corrections '''
        spell = SpellChecker()
        self.assertEqual(spell.correction('ths'), 'the')
        self.assertEqual(spell.correction('ergo'), 'ergo')
        self.assertEqual(spell.correction('alot'), 'a lot')
        self.assertEqual(spell.correction('this'), 'this')
        self.assertEqual(spell.correction('-'), '-')
        self.assertEqual(spell.correction('1213'), '1213')
        self.assertEqual(spell.correction('1213.9'), '1213.9')

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
        self.assertEqual(spell.candidates('-'), {'-'})

    def test_words(self):
        ''' rest the parsing of words '''
        spell = SpellChecker()
        res = ['this', 'is', 'a', 'test', 'of', 'this']
        self.assertEqual(spell.words('This is a test of this'), res)

    def test_word_frequency(self):
        ''' test word frequency '''
        spell = SpellChecker()
        # if the default load changes so will this...
        self.assertEqual(spell.word_frequency['the'], 6187925)

    def test_word_probability(self):
        ''' test the word probability calculation '''
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
        self.assertEqual(spell.known(['-']), {'-'})

        self.assertEqual(spell.known(['foobar']), set())
        self.assertEqual(spell.known(['ths']), set())
        self.assertEqual(spell.known(['ergos']), set())

    def test_unknown_words(self):
        ''' test the unknown word functionality '''
        spell = SpellChecker()
        self.assertEqual(spell.unknown(['this']), set())
        self.assertEqual(spell.unknown(['sherlock']), set())
        self.assertEqual(spell.unknown(['holmes']), set())
        self.assertEqual(spell.unknown(['known']), set())
        self.assertEqual(spell.unknown(['-']), set())

        self.assertEqual(spell.unknown(['foobar']), {'foobar'})
        self.assertEqual(spell.unknown(['ths']), {'ths'})
        self.assertEqual(spell.unknown(['ergos']), {'ergos'})

    def test_word_in(self):
        ''' test the use of the `in` operator '''
        spell = SpellChecker()
        self.assertTrue('key' in spell)
        self.assertFalse('rando' in spell)

    def test_word_contains(self):
        ''' test the contains functionality '''
        spell = SpellChecker()
        self.assertEqual(spell['the'], 6187925)

    def test_spanish_dict(self):
        ''' test loading in the spanish dictionary '''
        spell = SpellChecker(language='es')
        res = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'ª', 'º', 'à', 'á', 'â', 'ã', 'ä', 'å', 'ç', 'è', 'é', 'ê', 'ë',
               'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'ö', 'ø', 'ù', 'ú',
               'û', 'ü', 'ý', 'ń', 'ż', 'ž', 'у']
        self.assertEqual(sorted(list(spell.word_frequency.letters)), res)
        self.assertTrue('mañana' in spell)
        self.assertEqual(spell['que'], 12131641)

    def test_missing_dictionary(self):
        try:
            spell = SpellChecker(language='no')
        except ValueError as ex:
            msg = 'The provided dictionary language (no) does not exist!'
            self.assertEqual(str(ex), msg)

    def test_load_external_dictionary(self):
        ''' test loading a local dictionary '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_dictionary.json'.format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)
        self.assertEqual(spell['a'], 1)
        self.assertTrue('apple' in spell)

    def test_edit_distance_two(self):
        ''' test a case where edit distance must be two '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_dictionary.json'.format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)
        self.assertEqual(spell.candidates('ale'), {'a', 'apple'})

    def test_load_text_file(self):
        ''' test loading a text file '''
        here = os.path.dirname(__file__)
        filepath = '{}/resources/small_doc.txt'.format(here)
        spell = SpellChecker(language=None)  # just from this doc!
        spell.word_frequency.load_text_file(filepath)
        self.assertEqual(spell['a'], 3)
        self.assertEqual(spell['storm'], 2)
        self.assertFalse('awesome' in spell)
        self.assertTrue(spell['whale'])
        self.assertTrue('waves' in spell)

    def test_remove_words(self):
        spell = SpellChecker()
        self.assertEqual(spell['teh'], 6)
        spell.word_frequency.remove_words(['teh'])
        self.assertEqual(spell['teh'], 0)

    def test_remove_word(self):
        spell = SpellChecker()
        self.assertEqual(spell['teh'], 6)
        spell.word_frequency.remove('teh')
        self.assertEqual(spell['teh'], 0)

    def test_add_word(self):
        spell = SpellChecker()
        self.assertEqual(spell['meh'], 0)
        spell.word_frequency.add('meh')
        self.assertEqual(spell['meh'], 1)
