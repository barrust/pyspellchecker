# pyspellchecker

## Version 0.7.0
* Backwards Combatibility Change:
    * `spell.candidates` and `spell.correction` now return `None` if there are no valid corrections or candidates
* Remove misspelled words from [issue #120](https://github.com/barrust/pyspellchecker/issues/120)
* Update all default language dictionaries after updating the minimum frequency to 50 in `scripts/build_dictionary.py`
* Fix float("nan") issue; see [#125](https://github.com/barrust/pyspellchecker/issues/125)
* Include [Wikipedia's common typo list](https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines) to the exclude listing; see [#124](https://github.com/barrust/pyspellchecker/issues/124)

## Version 0.6.3
* Added class method to be able to get a listing of all supported languages
* Added type hinting
* Updated English dictionary to remove incorrect `cie` words; see [#112](https://github.com/barrust/pyspellchecker/issues/112)

## Version 0.6.2
* Add ability to load multiple languages at once; [see discussion](https://github.com/barrust/pyspellchecker/discussions/97)
* Fix default tokenizer to not enforce lower case; [#99](https://github.com/barrust/pyspellchecker/issues/99)

## Version 0.6.1
* Deprecated `spell.word_probability` since the name makes it seem that it is building a true probability; use `spell.word_usage_frequency` instead
* Added Russian language dictionary; [#91](https://github.com/barrust/pyspellchecker/pull/91) Thanks [@sviperm](https://github.com/sviperm)
* Include `__iter__` to both the `SpellChecker` and `WordFrequency` objects

## Version 0.6.0
* Removed **python 2.7** support
* Updated automated `scripts/build_dictionary.py` script to support adding missing words
* Updated `split_words()` to attempt to better handle punctuation; [#84](https://github.com/barrust/pyspellchecker/issues/84)
* Load pre-built dictionaries from relative location for use in `PyInstaller` and other executable tools; [#64](https://github.com/barrust/pyspellchecker/issues/64)

## Version 0.5.6
* ***NOTE:*** Last planned support for **Python 2.7**
* All dictionaries updated using the `scripts/build_dictionary.py` script

## Version 0.5.5
* Remove `encode` from the call to `json.loads()`

## Version 0.5.4
* Reduce words in `__edit_distance_alt` to improve memory performance; thanks [@blayzen-w](https://github.com/blayzen-w)

## Version 0.5.3
* Handle memory issues when trying to correct or find candidates for extremely long words

## Version 0.5.2
Ensure input is encoded correctly; resolves [#53](https://github.com/barrust/pyspellchecker/issues/53)

## Version 0.5.1
Handle windows encoding issues [#48](https://github.com/barrust/pyspellchecker/issues/48)
Deterministic order to corrections [#47](https://github.com/barrust/pyspellchecker/issues/47)

## Version 0.5.0
* Add tokenizer to the Spell object
* Add Support for local dictionaries to be case sensitive
[see PR #44](https://github.com/barrust/pyspellchecker/pull/44) Thanks [@davido-brainlabs](https://github.com/davido-brainlabs)
* Better python 2.7 support for reading gzipped files

## Version 0.4.0
* Add support for a tokenizer for splitting words into tokens

## Version 0.3.1
* Add full python 2.7 support for foreign dictionaries

## Version 0.3.0
* Ensure all checks against the word frequency are lower case
* Slightly better performance on edit distance of 2

## Version 0.2.2
* Minor package fix for non-wheel deployments

## Version 0.2.1
* Ignore case for language identifiers

## Version 0.2.0
* Changed `words` function to `split_words` to differentiate with the `word_frequency.words` function
* Added ***Portuguese*** dictionary: `pt`
* Add encoding argument to `gzip.open` and `open` dictionary loading and exporting
* Use of __slots__ for class objects

## Version 0.1.5
* Remove words based on threshold
* Add ability to iterate over words (keys) in the dictionary
* Add setting to to reduce the edit distance check
[see PR #17](https://github.com/barrust/pyspellchecker/pull/17) Thanks [@mrjamesriley](https://github.com/mrjamesriley)
* Added Export functionality:
   * json
   * gzip
* Updated logic for loading dictionaries to be either language or local_dictionary

## Version 0.1.4
* Ability to easily remove words
* Ability to add a single word
* Improved (i.e. cleaned up) English dictionary

## Version 0.1.3
* Better handle punctuation and numbers as the word to check

## Version 0.1.1
* Add support for language dictionaries
    * English, Spanish, French, and German
* Remove support for python 2; if it works, great!

## Version 0.1.0
* Move word frequency to its own class
* Add basic tests
* Readme documentation

## Version 0.0.1
* Initial release using code from Peter Norvig
* Initial release to pypi
