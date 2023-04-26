""" Desc:   A script to automate the building of multiple dictionaries based on
            known areas of concern due to the original source of the data. The
            script can be run from the source directly (-P and -p) once a
            sutable text file is obtained. It can also be run on a previously
            generated word frequency list to remove known problem areas.
    Author: Tyler Barrus
    Notes:  The original inputs are from OpenSubtitles (http://opus.nlpl.eu/OpenSubtitles2018.php):
            English Input:    http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.en.gz
            Spanish Input:    http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.es.gz
            German Input:     http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.de.gz
            French Input:     http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.fr.gz
            Portuguese Input: http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.pt.gz
            Russian Input:    http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.ru.gz
            Arabic Input:     http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.ar.gz
            Basque Input:     http://opus.nlpl.eu/download.php?f=OpenSubtitles/v2018/mono/OpenSubtitles.raw.au.gz
            Latvian Input:    https://huggingface.co/datasets/RaivisDejus/latvian-text
    Requirements:
            The script requires more than the standard library to run in its
            entirety. You will also need to install the NLTK package to build a
            dictionary from scratch. Otherwise, no additional packages are
            required.
"""
import contextlib
import json
import gzip
import os
import string
from collections import Counter


STRING_PUNCTUATION = tuple(string.punctuation)
DIGETS = tuple(string.digits)
MINIMUM_FREQUENCY = 50


@contextlib.contextmanager
def load_file(filename, encoding="utf-8"):
    """Context manager to handle opening a gzip or text file correctly and
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
    """Export a word frequency as a json object

    Args:
        filepath (str):
        word_frequency (Counter):
    """
    with open(filepath, "w") as f:
        json.dump(word_frequency, f, indent="", sort_keys=True, ensure_ascii=False)


def build_word_frequency(filepath, language, output_path):
    """Parse the passed in text file (likely from Open Subtitles) into
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
    # NLTK is only needed in this portion of the project
    try:
        from nltk.tag import pos_tag
        from nltk.tokenize import WhitespaceTokenizer
        from nltk.tokenize.toktok import ToktokTokenizer
    except ImportError as ex:
        raise ImportError("To build a dictioary from scratch, NLTK is required!\n{}".format(ex.message))

    word_frequency = Counter()
    if language == "es":
        tok = ToktokTokenizer()
    else:
        tok = WhitespaceTokenizer()

    idx = 0
    with load_file(filepath, "utf-8") as fobj:
        for line in fobj:
            # tokenize into parts
            parts = tok.tokenize(line)

            # Attempt to remove proper nouns
            # Remove things that have leading or trailing non-alphabetic characters.
            tagged_sent = pos_tag(parts)
            words = [
                word[0].lower()
                for word in tagged_sent
                if word[0] and not word[1] == "NNP" and word[0][0].isalpha() and word[0][-1].isalpha()
            ]

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


def export_misfit_words(misfit_filepath, word_freq_filepath, word_frequency):
    with load_file(word_freq_filepath, "utf-8") as f:
        source_word_frequency = json.load(f)

    source_words = set(source_word_frequency.keys())
    final_words = set(word_frequency.keys())

    misfitted_words = source_words.difference(final_words)
    misfitted_words = sorted(list(misfitted_words))

    with open(misfit_filepath, "w+") as file:
        for word in misfitted_words:
            file.write(word)
            file.write("\n")


def clean_english(word_frequency, filepath_exclude, filepath_include):
    """Clean an English word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
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

    # remove words without a vowel
    no_vowels = list()
    vowels = set("aeiouy")
    for key in word_frequency:
        if vowels.isdisjoint(key):
            no_vowels.append(key)
    for misfit in no_vowels:
        word_frequency.pop(misfit)

    # Remove double punctuations (a-a-a-able) or (a'whoppinganda'whumping)
    double_punc = list()
    for key in word_frequency:
        if key.count("'") > 1 or key.count("-") > 1 or key.count(".") > 2:
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

    # leading or trailing doubles a, "a'", "zz", ending y's
    doubles = list()
    for key in word_frequency:
        if key.startswith("aa") and key not in ("aardvark", "aardvarks"):
            doubles.append(key)
        elif key.startswith("a'"):
            doubles.append(key)
        elif key.startswith("zz"):
            doubles.append(key)
        elif key.endswith("yy"):
            doubles.append(key)
        elif key.endswith("hh"):
            doubles.append(key)
    for misfit in doubles:
        word_frequency.pop(misfit)

    # common missing spaces
    missing_spaces = list()
    for key in word_frequency:
        if key.startswith("about") and key != "about":
            missing_spaces.append(key)
        elif key.startswith("above") and key != "above":
            missing_spaces.append(key)
        elif key.startswith("after") and key != "after":
            missing_spaces.append(key)
        elif key.startswith("against") and key != "against":
            missing_spaces.append(key)
        elif key.startswith("all") and word_frequency[key] < 15:
            missing_spaces.append(key)
        elif key.startswith("almost") and key != "almost":
            missing_spaces.append(key)
        # This one has LOTS of possibilities...
        elif key.startswith("to") and word_frequency[key] < 25:
            missing_spaces.append(key)
        elif key.startswith("can't") and key != "can't":
            missing_spaces.append(key)
        elif key.startswith("i'm") and key != "i'm":
            missing_spaces.append(key)
    for misfit in missing_spaces:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def clean_spanish(word_frequency, filepath_exclude, filepath_include):
    """Clean a Spanish word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
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
    # NOTE: Not sure there are any occurances but this is not possible as a valid word!
    duplicate_accents = list()
    for key in word_frequency:
        if (key.count("á") + key.count("é") + key.count("í") + key.count("ó") + key.count("ú")) > 1:
            duplicate_accents.append(key)
    for misfit in duplicate_accents:
        word_frequency.pop(misfit)

    # fix misplaced "ü" marks
    # NOTE: the ü must be just after a g and before an e or i only (with or without accent)!
    misplaced_u = list()
    for key in word_frequency:
        if not "ü" in key:
            continue
        idx = key.index("ü")
        if idx == 0 or idx == len(key) - 1:  # first or last letter
            misplaced_u.append(key)
            continue
        if key[idx - 1] != "g" and key[idx + 1] not in "eéií":
            misplaced_u.append(key)
    for misfit in misplaced_u:
        word_frequency.pop(misfit)

    # ción issues
    cion_issues = list()
    for key in word_frequency:
        if not key.endswith("cion"):
            continue
        base = key[:-4]
        n_key = "{}ción".format(base)
        if n_key in word_frequency:
            cion_issues.append(key)
    for misfit in cion_issues:
        word_frequency.pop(misfit)

    # remove words that start with a double a ("aa")
    double_a = list()
    for key in word_frequency:
        if key.startswith("aa"):
            double_a.append(key)
    for misfit in double_a:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def clean_german(word_frequency, filepath_exclude, filepath_include):
    """Clean a German word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
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

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def clean_french(word_frequency, filepath_exclude, filepath_include):
    """Clean a French word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
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

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def clean_portuguese(word_frequency, filepath_exclude, filepath_include):
    """Clean a Portuguese word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
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

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def clean_russian(word_frequency, filepath_exclude, filepath_include):
    """Clean an Russian word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
    """
    letters = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

    # remove words with invalid characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words without a vowel
    no_vowels = list()
    vowels = set("аеёиоуыэюя")
    for key in word_frequency:
        if vowels.isdisjoint(key):
            no_vowels.append(key)
    for misfit in no_vowels:
        word_frequency.pop(misfit)

    # remove ellipses
    ellipses = list()
    for key in word_frequency:
        if ".." in key:
            ellipses.append(key)
    for misfit in ellipses:
        word_frequency.pop(misfit)

    # leading or trailing doubles a, "a'", "zz", ending y's
    doubles = list()
    for key in word_frequency:
        if key.startswith("аа") and key not in ("аарон", "аарона", "аарону"):
            doubles.append(key)
        elif key.startswith("ээ") and key not in ("ээг"):
            doubles.append(key)
    for misfit in doubles:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def clean_arabic(word_frequency, filepath_exclude, filepath_include):
    """Clean an Arabic word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
    """
    letters = set("دجحإﻹﻷأآﻵخهعغفقثصضذطكمنتالبيسشظزوةىﻻرؤءئ")

    # remove words with invalid characters
    invalid_chars = list()
    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove ellipses
    ellipses = list()
    for key in word_frequency:
        if ".." in key:
            ellipses.append(key)
    for misfit in ellipses:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency

def clean_basque(word_frequency, filepath_exclude, filepath_include):
    """Clean a Basque word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
    """
    letters = set("abcdefghijklmnopqrstuvwxyzñ")

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

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency

def clean_latvian(word_frequency, filepath_exclude, filepath_include):
    """Clean a Latvian word frequency list

    Args:
        word_frequency (Counter):
        filepath_exclude (str):
        filepath_include (str):
    """
    letters = set("aābcčdeēfgģhiījkķlļmnņoprsštuūvzž")

    # remove words with invalid characters
    invalid_chars = list()

    for key in word_frequency:
        kl = set(key)
        if kl.issubset(letters):
            continue
        invalid_chars.append(key)
    for misfit in invalid_chars:
        word_frequency.pop(misfit)

    # remove words without a vowel
    no_vowels = list()
    vowels = set("aāiīeēouū")
    for key in word_frequency:
        if vowels.isdisjoint(key):
            no_vowels.append(key)
    for misfit in no_vowels:
        word_frequency.pop(misfit)

    # remove ellipses
    ellipses = list()
    for key in word_frequency:
        if ".." in key:
            ellipses.append(key)
    for misfit in ellipses:
        word_frequency.pop(misfit)

    # leading or trailing doubles aa or ii
    doubles = list()
    for key in word_frequency:
        if key.startswith("аа"):
            doubles.append(key)
        elif key.startswith("ii"):
            doubles.append(key)
    for misfit in doubles:
        word_frequency.pop(misfit)

    # remove single letters
    single_letters = list()
    for key in word_frequency:
        if len(key) == 1:
            single_letters.append(key)
    for misfit in single_letters:
        word_frequency.pop(misfit)

    # TODO: other possible fixes?

    # remove small numbers
    small_frequency = list()
    for key in word_frequency:
        if word_frequency[key] <= MINIMUM_FREQUENCY:
            small_frequency.append(key)
    for misfit in small_frequency:
        word_frequency.pop(misfit)

    # remove flagged misspellings
    with load_file(filepath_exclude) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                word_frequency.pop(line)

    # Add known missing words back in (ugh)
    with load_file(filepath_include) as fobj:
        for line in fobj:
            line = line.strip()
            if line in word_frequency:
                print("{} is already found in the dictionary! Skipping!")
            else:
                word_frequency[line] = MINIMUM_FREQUENCY

    return word_frequency


def _parse_args():
    """parse arguments for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build a new dictionary (word frequency) using the OpenSubtitles2018 project"
    )
    parser.add_argument(
        "-l", "--language", required=True, help="The language being built", choices=["en", "es", "de", "fr", "pt", "ru", "ar", "lv", "eu"]
    )
    parser.add_argument(
        "-f", "--file-path", help="The path to the downloaded text file OR the saved word frequency json"
    )
    parser.add_argument(
        "-p", "--parse-input", action="store_true", help="Add this if providing a text file to be parsed"
    )
    parser.add_argument(
        "-m", "--misfit-file", action="store_true", help="Create file with words which was removed from dictionary"
    )

    args = parser.parse_args()

    # validate that we have a path, if needed!
    if args.parse_input:
        if not args.file_path:
            raise Exception("A path is required if parsing a text file!")

    if args.file_path:
        args.file_path = os.path.abspath(os.path.realpath(args.file_path))

        if not os.path.exists(args.file_path):
            raise FileNotFoundError("File Not Found. A valid path is required if parsing a text file!")

    return args


if __name__ == "__main__":
    args = _parse_args()

    # get current path to find where the script is currently
    script_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.abspath("{}/../".format(script_path))
    resources_path = os.path.abspath("{}/resources/".format(module_path))
    data_path = os.path.abspath("{}/data/".format(script_path))
    exclude_filepath = os.path.abspath("{}/{}_exclude.txt".format(data_path, args.language))
    include_filepath = os.path.abspath("{}/{}_include.txt".format(data_path, args.language))

    print(script_path)
    print(module_path)
    print(resources_path)
    print(exclude_filepath)
    print(include_filepath)

    # Should we re-process a file?
    if args.parse_input:
        json_path = os.path.join(script_path, "data", "{}_full.json".format(args.language))
        print(json_path)
        word_frequency = build_word_frequency(args.file_path, args.language, json_path)
    else:
        json_path = os.path.join(script_path, "data", "{}_full.json.gz".format(args.language))
        print(json_path)
        with load_file(json_path, "utf-8") as f:
            word_frequency = json.load(f)

    # create include and exclude files before cleaning
    for filepath in (include_filepath, exclude_filepath):
        with open(filepath, "a+"):
            pass

    # clean up the dictionary
    if args.language == "en":
        word_frequency = clean_english(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "es":
        word_frequency = clean_spanish(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "de":
        word_frequency = clean_german(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "fr":
        word_frequency = clean_french(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "pt":
        word_frequency = clean_portuguese(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "ru":
        word_frequency = clean_russian(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "ar":
        word_frequency = clean_arabic(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "eu":
        word_frequency = clean_basque(word_frequency, exclude_filepath, include_filepath)
    elif args.language == "lv":
        word_frequency = clean_latvian(word_frequency, exclude_filepath, include_filepath)

    # export word frequency for review!
    word_frequency_path = os.path.join(script_path, "{}.json".format(args.language))
    print(word_frequency_path)
    export_word_frequency(word_frequency_path, word_frequency)

    if args.misfit_file:
        misfit_filepath = os.path.abspath("{}/{}_misfit.txt".format(data_path, args.language))
        export_misfit_words(misfit_filepath, json_path, word_frequency)
