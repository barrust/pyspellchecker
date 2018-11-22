# pyspellchecker

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
