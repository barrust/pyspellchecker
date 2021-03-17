from abc import abstractmethod, ABCMeta
from build_dictionary import load_file


class BasePipeline(metaclass=ABCMeta):
    MINIMUM_FREQUENCY = 15

    @abstractmethod
    def __init__(self, exclude_path, include_path, misfit_path, *args) -> None:
        self.exclude_path = exclude_path
        self.include_path = include_path
        self.misfit_path = misfit_path
        self.pipeline = (*args,
                         self.remove_small_frequency,
                         self.remove_from_exclude_file,
                         self.add_from_include_file)

    def __call__(self, word_frequency):
        misfits = []
        for pipe in self.pipeline:
            misfit = pipe(word_frequency)
            if misfit:
                misfits += misfit
        return misfits

    def remove_small_frequency(self, word_frequency):
        # remove small numbers
        invalid_words = list()
        for word in word_frequency:
            if word_frequency[word] <= self.MINIMUM_FREQUENCY:
                invalid_words.append(word)
        for invalid_word in invalid_words:
            word_frequency.pop(invalid_word)
        return invalid_words

    def remove_from_exclude_file(self, word_frequency):
        # remove flagged misspellings
        with load_file(self.exclude_path) as fobj:
            for word in fobj:
                word = word.strip()
                if word in word_frequency:
                    word_frequency.pop(word)

    def add_from_include_file(self, word_frequency):
        # # Add known missing words back in (ugh)
        with load_file(self.include_path) as fobj:
            for word in fobj:
                word = word.strip()
                if word in word_frequency:
                    print("{} is already found in the dictionary! Skipping!")
                else:
                    word_frequency[word] = self.MINIMUM_FREQUENCY


class EnglishPipeline(BasePipeline):
    pass


class SpanishPipeline(BasePipeline):
    pass


class GermanPipeline(BasePipeline):
    pass


class FrenchPipeline(BasePipeline):
    pass


class PortuguesePipeline(BasePipeline):
    pass


class RussianPipeline(BasePipeline):
    def __init__(self, exclude_path, include_path, misfit_path) -> None:
        super().__init__(exclude_path, include_path, misfit_path,
                         self.remove_words_with_invalid_chars,
                         self.remove_words_without_vowel,
                         self.remove_ellipses,
                         self.remove_doubles)

    @classmethod
    def remove_words_with_invalid_chars(cls, word_frequency):
        valid_letters = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя-")
        invalid_words = list()
        for word in word_frequency:
            letters = set(word)
            if not letters.issubset(valid_letters):
                invalid_words.append(word)
        for invalid_word in invalid_words:
            word_frequency.pop(invalid_word)
        return invalid_words

    @classmethod
    def remove_words_without_vowel(cls, word_frequency):
        # remove words without a vowel
        invalid_words = list()
        vowels = set("аеёиоуыэюя")
        for word in word_frequency:
            if word in ['ржд']:
                continue
            if vowels.isdisjoint(word):
                invalid_words.append(word)
        for invalid_word in invalid_words:
            word_frequency.pop(invalid_word)
        return invalid_words

    @classmethod
    def remove_ellipses(cls, word_frequency):
        # remove ellipses
        invalid_words = list()
        for word in word_frequency:
            if ".." in word:
                invalid_words.append(word)
        for invalid_word in invalid_words:
            word_frequency.pop(invalid_word)
        return invalid_words

    @classmethod
    def remove_doubles(cls, word_frequency):
        # leading or trailing doubles a, "a'", "zz", ending y's
        invalid_words = list()
        for word in word_frequency:
            if word.startswith("аа") and (word not in ("аарон", "аарона", "аарону")):
                invalid_words.append(word)
            elif word.startswith("ээ") and (word not in ("ээг")):
                invalid_words.append(word)
        for invalid_word in invalid_words:
            word_frequency.pop(invalid_word)
        return invalid_words
