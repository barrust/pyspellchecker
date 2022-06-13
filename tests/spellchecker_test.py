# coding=UTF-8
""" Unittest class """

import unittest
import os

from spellchecker import SpellChecker


class TestSpellChecker(unittest.TestCase):
    """test the spell checker class"""

    def test_correction(self):
        """test spell checker corrections"""
        spell = SpellChecker()
        self.assertEqual(spell.correction("ths"), "the")
        self.assertEqual(spell.correction("ergo"), "ergo")
        # self.assertEqual(spell.correction('alot'), 'a lot')
        self.assertEqual(spell.correction("this"), "this")
        self.assertEqual(spell.correction("-"), "-")
        self.assertEqual(spell.correction("1213"), "1213")
        self.assertEqual(spell.correction("1213.9"), "1213.9")

    def test_candidates(self):
        """test spell checker candidates"""
        spell = SpellChecker()
        cands = {
            "tes",
            "thas",
            "tis",
            "thes",
            "thus",
            "thu",
            "thy",
            "thi",
            "tas",
            "tus",
            "thos",
            "tho",
            "tha",
            "the",
            "this",
        }
        self.assertEqual(spell.candidates("ths"), cands)
        self.assertEqual(spell.candidates("the"), {"the"})
        self.assertEqual(spell.candidates("-"), {"-"})
        # something that cannot exist... should return None...
        self.assertEqual(spell.candidates("manasaeds"), None)

    def test_words(self):
        """test the parsing of words"""
        spell = SpellChecker()
        res = ["This", "is", "a", "test", "of", "this"]
        self.assertEqual(spell.split_words("This is a test of this"), res)

    def test_words_more_complete(self):
        """test the parsing of words"""
        spell = SpellChecker()
        res = ["This", "is", "a", "test", "of", "the", "word", "parser", "It", "should", "work", "correctly"]
        self.assertEqual(spell.split_words("This is a test of the word parser. It should work correctly!!!"), res)

    def test_word_frequency(self):
        """test word frequency"""
        spell = SpellChecker()
        # if the default load changes so will this...
        self.assertEqual(spell.word_frequency["the"], 76138318)

    def test_word_usage_frequency(self):
        """test the word usage frequency calculation"""
        spell = SpellChecker()
        # if the default load changes so will this...
        num = spell.word_frequency["the"]
        denom = spell.word_frequency.total_words
        self.assertEqual(spell.word_usage_frequency("the"), num / denom)

    def test_word_known(self):
        """test if the word is a `known` word or not"""
        spell = SpellChecker()
        self.assertEqual(spell.known(["this"]), {"this"})
        self.assertEqual(spell.known(["sherlock"]), {"sherlock"})
        self.assertEqual(spell.known(["holmes"]), {"holmes"})
        self.assertEqual(spell.known(["known"]), {"known"})

        self.assertEqual(spell.known(["-"]), set())
        self.assertEqual(spell.known(["foobar"]), set())
        self.assertEqual(spell.known(["ths"]), set())
        self.assertEqual(spell.known(["ergos"]), set())

    def test_unknown_words(self):
        """test the unknown word functionality"""
        spell = SpellChecker()
        self.assertEqual(spell.unknown(["this"]), set())
        self.assertEqual(spell.unknown(["sherlock"]), set())
        self.assertEqual(spell.unknown(["holmes"]), set())
        self.assertEqual(spell.unknown(["known"]), set())
        self.assertEqual(spell.unknown(["-"]), set())

        self.assertEqual(spell.unknown(["foobar"]), {"foobar"})
        self.assertEqual(spell.unknown(["ths"]), {"ths"})
        self.assertEqual(spell.unknown(["ergos"]), {"ergos"})

    def test_word_in(self):
        """test the use of the `in` operator"""
        spell = SpellChecker()
        self.assertTrue("key" in spell)
        self.assertFalse("wantthis" in spell)  # a known excluded word

    def test_word_contains(self):
        """test the contains functionality"""
        spell = SpellChecker()
        self.assertEqual(spell["the"], 76138318)

    def test_spanish_dict(self):
        """test loading in the spanish dictionary"""
        spell = SpellChecker(language="es")
        res = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "á",
            "é",
            "í",
            "ñ",
            "ó",
            "ú",
            "ü",
        ]
        self.assertEqual(sorted(list(spell.word_frequency.letters)), res)
        self.assertTrue("mañana" in spell)
        self.assertEqual(spell["que"], 37141781)

    def test_multiple_dicts(self):
        """test loading in multiple dictionaries"""
        es = SpellChecker(language="es")
        self.assertEqual(es["a"], 25517457)
        en = SpellChecker(language="en")
        self.assertEqual(en["a"], 48779620)
        spell = SpellChecker(language=["en", "es"])
        self.assertEqual(spell["a"], 74297077)  # 48779620 + 25517457

    def test_missing_dictionary(self):
        try:
            SpellChecker(language="no")
        except ValueError as ex:
            msg = "The provided dictionary language (no) does not exist!"
            self.assertEqual(str(ex), msg)

    def test_load_external_dictionary(self):
        """test loading a local dictionary"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)
        self.assertEqual(spell["a"], 1)
        self.assertTrue("apple" in spell)

    def test_edit_distance_one(self):
        """test a case where edit distance must be one"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath, distance=1)
        self.assertEqual(spell.candidates("hike"), {"bike"})

    def test_edit_distance_two(self):
        """test a case where edit distance must be two"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)
        self.assertEqual(spell.candidates("ale"), {"a", "apple"})

    def test_edit_distance_one_property(self):
        """check the property setting of the distance property"""
        spell = SpellChecker(distance=1)
        self.assertEqual(spell.distance, 1)
        spell.distance = 2
        self.assertEqual(spell.distance, 2)

    def test_edit_distance_invalud(self):
        """check the property setting of the distance property on invalid inputs"""
        spell = SpellChecker(distance=None)
        self.assertEqual(spell.distance, 2)
        spell.distance = 1
        self.assertEqual(spell.distance, 1)
        spell.distance = "string"
        self.assertEqual(spell.distance, 2)

    def test_load_text_file(self):
        """test loading a text file"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_doc.txt".format(here)
        spell = SpellChecker(language=None)  # just from this doc!
        spell.word_frequency.load_text_file(filepath)
        self.assertEqual(spell["a"], 3)
        self.assertEqual(spell["storm"], 2)
        self.assertFalse("awesome" in spell)
        self.assertTrue(spell["whale"])
        self.assertTrue("waves" in spell)

    def test_remove_words(self):
        """test is a word is removed"""
        spell = SpellChecker()
        self.assertEqual(spell["the"], 76138318)
        spell.word_frequency.remove_words(["the"])
        self.assertEqual(spell["the"], 0)

    def test_remove_word(self):
        """test a single word removed"""
        spell = SpellChecker()
        self.assertEqual(spell["the"], 76138318)
        spell.word_frequency.remove("the")
        self.assertEqual(spell["the"], 0)

    def test_remove_by_threshold(self):
        """test removing everything below a certain threshold"""
        spell = SpellChecker()
        cnt = 0
        for key in spell.word_frequency.keys():
            if spell.word_frequency[key] < 300:
                cnt += 1
        self.assertGreater(cnt, 0)
        spell.word_frequency.remove_by_threshold(300)
        cnt = 0
        for key in spell.word_frequency.words():  # synonym for keys
            if spell.word_frequency[key] < 300:
                cnt += 1
        self.assertEqual(cnt, 0)

    def test_remove_by_threshold_using_items(self):
        """test removing everything below a certain threshold; using items to test"""
        spell = SpellChecker()
        cnt = 0
        for _, val in spell.word_frequency.items():
            if val < 300:
                cnt += 1
        self.assertGreater(cnt, 0)
        spell.word_frequency.remove_by_threshold(300)
        cnt = 0
        for _, val in spell.word_frequency.items():  # synonym for keys
            if val < 300:
                cnt += 1
        self.assertEqual(cnt, 0)

    def test_add_word(self):
        """test adding a word"""
        spell = SpellChecker()
        self.assertEqual(spell["appt"], 0)
        spell.word_frequency.add("appt")
        self.assertEqual(spell["appt"], 1)

    def test_checking_odd_word(self):
        """test checking a word that is really a number"""
        spell = SpellChecker()
        self.assertEqual(spell.edit_distance_1("12345"), {"12345"})

    def test_unique_words(self):
        """test the unique word count"""
        spell = SpellChecker()
        self.assertEqual(spell.word_frequency.unique_words, len(list(spell.word_frequency.keys())))

    def test_import_export_json(self):
        """test the export functionality as json"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)

        spell = SpellChecker(language=None, local_dictionary=filepath)
        spell.word_frequency.add("meh")
        new_filepath = "{}/resources/small_dictionary_new.json".format(here)
        spell.export(new_filepath, gzipped=False)

        sp = SpellChecker(language=None, local_dictionary=new_filepath)
        self.assertTrue("meh" in sp)
        self.assertFalse("bananna" in sp)

        os.remove(new_filepath)

    def test_import_export_gzip(self):
        """test the export functionality as gzip"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)

        spell = SpellChecker(language=None, local_dictionary=filepath)
        spell.word_frequency.add("meh")
        new_filepath = "{}/resources/small_dictionary_new.json.gz".format(here)
        spell.export(new_filepath, gzipped=True)

        sp = SpellChecker(language=None, local_dictionary=new_filepath)
        self.assertTrue("meh" in sp)
        self.assertFalse("bananna" in sp)

        os.remove(new_filepath)

    def test_capitalization_when_case_sensitive_defaults_to_false(self):
        """test that capitalization doesn't affect in comparisons"""
        spell = SpellChecker(language=None)
        spell.word_frequency.add("Bob")
        spell.word_frequency.add("Bob")
        spell.word_frequency.add("Bab")
        self.assertEqual("Bob" in spell, True)
        self.assertEqual("BOb" in spell, True)
        self.assertEqual("BOB" in spell, True)
        self.assertEqual("bob" in spell, True)

        words = ["Bb", "bb", "BB"]
        self.assertEqual(spell.unknown(words), {"bb"})

        known_words = ["BOB", "bOb"]
        self.assertEqual(spell.known(known_words), {"bob"})

        self.assertEqual(spell.candidates("BB"), {"bob", "bab"})
        self.assertEqual(spell.correction("BB"), "bob")

    def test_large_words(self):
        """test checking for words that are clearly larger than the largest dictionary word"""
        spell = SpellChecker(language=None, distance=2)
        spell.word_frequency.add("Bob")

        words = ["Bb", "bb", "BB"]
        self.assertEqual(spell.unknown(words), {"bb"})

        known_words = ["BOB", "bOb"]
        self.assertEqual(spell.known(known_words), {"bob"})

        self.assertEqual(spell.correction("bobs"), "bob")
        self.assertEqual(spell.correction("bobb"), "bob")
        self.assertEqual(spell.correction("bobby"), "bob")
        self.assertEqual(spell.word_frequency.longest_word_length, 3)
        self.assertIsNone(spell.correction("bobbys"))

    def test_extremely_large_words(self):
        """test when a word is just extreamly large"""
        spell = SpellChecker()
        horrible_word = "thisisnotarealisticwordthisisnotarealisticwordthisisnotarealisticwordthisisnotarealisticword"
        self.assertEqual(spell.correction(horrible_word), horrible_word)

    def test_capitalization_when_case_sensitive_true(self):
        """test that capitalization affects comparisons"""
        spell = SpellChecker(language=None, case_sensitive=True)
        spell.word_frequency.add("Bob")
        self.assertEqual("Bob" in spell, True)
        self.assertEqual("BOb" in spell, False)
        self.assertEqual("BOB" in spell, False)
        self.assertEqual("bob" in spell, False)

        words = ["Bb", "bb", "BB"]
        self.assertEqual(spell.unknown(words), {"Bb", "bb", "BB"})

        case_variant_words = ["BOB", "bOb"]
        self.assertEqual(spell.known(case_variant_words), set())

        self.assertEqual(spell.candidates("Bb"), {"Bob"})
        self.assertEqual(spell.candidates("bob"), {"Bob"})
        self.assertEqual(spell.correction("Bb"), "Bob")
        self.assertEqual(spell.correction("bob"), "Bob")
        self.assertEqual(spell.unknown(["bob"]), {"bob"})

    def test_capitalization_when_language_set(self):
        """test that capitalization doesn't affect comparisons when language not None"""
        spell = SpellChecker(language="en")
        self.assertEqual(spell.known(["Bike"]), {"bike"})

    def test_pop(self):
        """test the popping of a word"""
        spell = SpellChecker()
        self.assertEqual("apple" in spell, True)
        self.assertGreater(spell.word_frequency.pop("apple"), 1)
        self.assertEqual("apple" in spell, False)

    def test_pop_default(self):
        """test the default value being set for popping a word"""
        spell = SpellChecker()
        self.assertEqual("appleies" in spell, False)
        self.assertEqual(spell.word_frequency.pop("appleies", False), False)

    def test_adding_unicode(self):
        """test adding a unicode word to the dictionary"""
        spell = SpellChecker()
        spell.word_frequency.load_words(["mañana"])
        self.assertEqual("ñ" in spell.word_frequency.letters, True)

        here = os.path.dirname(__file__)
        new_filepath = "{}/resources/small_dictionary_new.json.gz".format(here)
        spell.export(new_filepath, gzipped=True)

        spell2 = SpellChecker(language=None, local_dictionary=new_filepath)
        self.assertEqual("mañana" in spell2, True)

        os.remove(new_filepath)

    def test_tokenizer_file(self):
        """def using a custom tokenizer for file loading"""

        def tokens(txt):
            for x in txt.split():
                yield x

        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_doc.txt".format(here)
        spell = SpellChecker(language=None)  # just from this doc!
        spell.word_frequency.load_text_file(filepath, tokenizer=tokens)
        self.assertEqual(spell["a"], 3)
        self.assertEqual(spell["storm"], 1)
        self.assertEqual(spell["storm."], 1)
        self.assertFalse("awesome" in spell)
        self.assertTrue(spell["whale"])
        self.assertTrue("sea." in spell)

    def test_tokenizer_provided(self):
        """Test passing in a tokenizer"""

        def tokens(txt):
            for x in txt.split():
                yield x

        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_doc.txt".format(here)
        spell = SpellChecker(language=None, tokenizer=tokens)  # just from this doc!
        spell.word_frequency.load_text_file(filepath)
        self.assertEqual(spell["a"], 3)
        self.assertEqual(spell["storm"], 1)
        self.assertEqual(spell["storm."], 1)
        self.assertFalse("awesome" in spell)
        self.assertTrue(spell["whale"])
        self.assertTrue("sea." in spell)

    def test_bytes_input(self):
        """Test using bytes instead of unicode as input"""

        var = b"bike"

        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)
        spell = SpellChecker(language=None, local_dictionary=filepath)

        self.assertTrue(var in spell)
        self.assertEqual(spell[var], 60)

    def test_split_words(self):
        """test using split_words"""
        spell = SpellChecker()
        res = spell.split_words("This isn't a good test, but it is a test!!!!")
        self.assertEqual(set(res), set(["This", "isn't", "a", "good", "test", "but", "it", "is", "a", "test"]))

    def test_iter_spellchecker(self):
        """Test using the iterator on the SpellChecker"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)

        spell = SpellChecker(language=None, local_dictionary=filepath)

        cnt = 0
        for word in spell:
            self.assertTrue(word in spell)
            cnt += 1
        self.assertEqual(cnt, len(spell.word_frequency.dictionary))

    def test_iter_word_frequency(self):
        """Test using the iterator on the WordFrequency"""
        here = os.path.dirname(__file__)
        filepath = "{}/resources/small_dictionary.json".format(here)

        spell = SpellChecker(language=None, local_dictionary=filepath)

        cnt = 0
        for word in spell.word_frequency:
            self.assertTrue(word in spell)
            cnt += 1
        self.assertEqual(cnt, len(spell.word_frequency.dictionary))

    def test_case_sensitive_parse_words(self):
        """Test using the parse words to generate a case sensitive dict"""
        spell = SpellChecker(language=None, case_sensitive=True)
        spell.word_frequency.load_text("This is a Test of the test!")
        self.assertTrue("This" in spell)
        self.assertFalse("this" in spell)

    def test_case_insensitive_parse_words(self):
        """Test using the parse words to generate a case insensitive dict"""
        spell = SpellChecker(language=None, case_sensitive=False)
        spell.word_frequency.load_text("This is a Test of the test!")
        # in makes sure it is lower case in this instance
        self.assertTrue("this" in spell)

    def test_language_list(self):
        """Test pulling a list of supported languages"""
        langs = SpellChecker.languages()
        self.assertIn("en", langs)
        self.assertIn("de", langs)
        self.assertIn("es", langs)
        self.assertNotIn("ja", langs)

    def test_nan_correction(self):
        """Test that nan does not get skipped because of float('nan')"""
        spell = SpellChecker()

        if "nan" in spell:
            self.assertEqual(spell.candidates("nan"), {"nan"})
            spell.word_frequency.remove("nan")
        self.assertNotEqual(spell.candidates("nan"), {"nan"})
