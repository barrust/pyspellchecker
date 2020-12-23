"""
    https://t-redactyl.io/blog/2017/06/text-cleaning-in-multiple-languages.html
    https://github.com/LuminosoInsight/python-ftfy
    https://github.com/nltk/nltk/issues/1558
    https://www.nltk.org/api/nltk.tokenize.html


    http://opus.nlpl.eu/OpenSubtitles2018.php

    English Input:      http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.en.gz
    Spanish Input:      http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.es.gz
    German Input:       http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.de.gz
    French Input:       http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.fr.gz
    Portuguese Input:   http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.pt.gz
"""
import contextlib
import json
import gzip
import os
import string
import sys
from collections import Counter

from nltk.tag import pos_tag
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize.toktok import ToktokTokenizer

STRING_PUNCTUATION = tuple(string.punctuation)
DIGETS = tuple(string.digits)


@contextlib.contextmanager
def load_file(filename, encoding):
    """ Context manager to handle opening a gzip or text file correctly and
        reading all the data

        Args:
            filename (str): The filename to open
            encoding (str): The file encoding to use
        Yields:
            str: The string data from the file read
    """
    if filename[-3:].lower() == ".gz":
        with gzip.open(filename, mode="rt", encoding=encoding) as fobj:
            yield fobj
    else:
        with open(filename, mode="r", encoding=encoding) as fobj:
            yield fobj


def export_word_frequency(filepath, word_frequency):
    """ Export a word frequency as a json object

        Args:
            filepath (str):
            word_frequency (Counter):
    """
    with open(filepath, 'w') as f:
        json.dump(word_frequency, f, indent="", sort_keys=True, ensure_ascii=False)


def build_word_frequency(filepath, language, output_path):
    """ Parse the passed in text file (likely from Open Subtitles) into
        a word frequency list and write it out to disk

        Args:
            filepath (str):
            language (str):
            output_path (str):
        Returns:
            Counter: The word frequency as parsed from the file
        Note:
            This only removes words that are proper nouns (attempts to...) and
            anything that starts or stops with something that is not in the alphabet.
    """
    word_frequency = Counter()
    if language == "es":
        tok = ToktokTokenizer()
    else:
        tok = WhitespaceTokenizer()

    idx = 0
    with load_file(filepath, 'utf-8') as fobj:
        for line in fobj:
            # tokenize into parts
            parts = tok.tokenize(line)

            # Attempt to remove proper nouns
            # Remove things that have leading or trailing non-alphabetic characters.
            tagged_sent = pos_tag(parts)
            words = [word[0].lower() for word in tagged_sent if word[0] and not word[1] == "NNP" and word[0][0].isalpha() and word[0][-1].isalpha()]

            # print(words)
            if words:
                word_frequency.update(words)

            idx += 1

            if idx % 100000 == 0:
                print("completed: {} rows".format(idx))
        # end file loop
    print("completed: {} rows".format(idx))
    export_word_frequency(output_path, word_frequency)

    return word_frequency


def clean_english(word_frequency):
    """ Clean an English word frequency list

        Args:
            word_frequency (Counter):
    """
    letters = set("abcdefghijklmnopqrstuvwxyz'")

    # remove words with invalid characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # Remove double punctuations (a-a-a-able) or (a'whoppinganda'whumping)
    double_punc = list()
    for key in word_frequency:
        if key.count("'") > 1 or key.count(".") > 2:
            double_punc.append(key)
    for misfit in double_punc:
        word_frequency.pop(misfit)

    # remove ellipses
    ellipses = list()
    for key in word_frequency:
        if ".." in key:
            ellipses.append(key)
    for misfit in ellipses:
        word_frequency.pop(misfit)

    # leading double a, "a." and "a'"
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa") and key not in ("aardvark", "aardvarks"):
            double_a.append(key)
        elif  key.startswith("a'"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers (5 or less)
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= 5:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    return word_frequency


def clean_spanish(word_frequency):
    """ Clean a Spanish word frequency list

        Args:
            word_frequency (Counter):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzáéíóúüñ")

    # fix issues with words containing other characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # fix issues with more than one accent marks

    # fix misplaced "ü" marks

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers (5 or less)
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= 5:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    return word_frequency


def clean_german(word_frequency):
    """ Clean a German word frequency list

        Args:
            word_frequency (Counter):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzäöüß")

    # fix issues with words containing other characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers (5 or less)
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= 5:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    return word_frequency


def clean_french(word_frequency):
    """ Clean a French word frequency list

        Args:
            word_frequency (Counter):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzéàèùâêîôûëïüÿçœæ")

    # fix issues with words containing other characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers (5 or less)
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= 5:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    return word_frequency


def clean_portuguese(word_frequency):
    """ Clean a Portuguese word frequency list

        Args:
            word_frequency (Counter):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzáâãàçéêíóôõú")

    # fix issues with words containing other characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers (5 or less)
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= 5:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    return word_frequency


def _parse_args():
    """parse arguments for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Build a new dictionary (word frequency) using the OpenSubtitles2018 project')
    parser.add_argument("-l", "--language", required=True, help="The language being built", choices=['en', 'es', 'de', 'fr', 'pt'])
    parser.add_argument("-p", "--path", help="The path to the downloaded text file OR the saved word frequency json")
    parser.add_argument("-P", "--parse_input", action="store_true", help="Add this if providing a text file to be parsed")

    args = parser.parse_args()

    # validate that we have a path, if needed!
    if args.parse_input:
        if not args.path:
            raise Exception("A path is required if parsing a text file!")

    if args.path:
        args.path = os.path.abspath(os.path.realpath(args.path))

        if not os.path.exists(args.path):
            raise FileNotFoundError("File Not FoundA valid path is required if parsing a text file!")

    return args


if __name__ == '__main__':
    args = _parse_args()

    # get current path to find where the script is currently
    script_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.abspath("{}/../".format(script_path))
    resources_path = os.path.abspath("{}/resources/".format(module_path))

    print(script_path)
    print(module_path)
    print(resources_path)

    # Should we re-process a file?
    if args.parse_input:
        json_path = os.path.join(script_path, "data", "{}.json".format(args.language))
        print(json_path)
        word_frequency = build_word_frequency(args.path, args.language, json_path)
    else:
        json_path = os.path.join(script_path, "data", "{}_full.json.gz".format(args.language))
        print(json_path)
        with load_file(json_path, 'utf-8') as f:
            word_frequency = json.load(f)

    # clean up the dictionary
    if args.language == "en":
        word_frequency = clean_english(word_frequency)
    elif args.language == "es":
        word_frequency = clean_spanish(word_frequency)
    elif args.language == "de":
        word_frequency = clean_german(word_frequency)
    elif args.language == "fr":
        word_frequency = clean_french(word_frequency)
    elif args.language == "pt":
        word_frequency = clean_portuguese(word_frequency)

    # export word frequency for review!
    export_word_frequency(os.path.join(script_path, "{}.json".format(args.language)), word_frequency)
