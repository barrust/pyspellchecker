# pyspellchecker

Pure Python Spell Checking based on
[Peter Norvig's](https://norvig.com/spell-correct.html) blog post on setting up
a simple spell checking algorithm.

It uses a [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
algorithm to find permutations within an edit distance of 2 from the
original word. It then compares all permutations (insertions, deletions,
replacements, and transpositions) to known words in a word frequency list.
Those words that are found more often in the frequency list are `more likely`
the correct results.


## Installation

The easiest method to install is using pip:

``` bash
pip install pyspellchecker
```

To install from source:
``` bash
git clone https://github.com/barrust/pyspellchecker.git
cd pyspellchecker
python setup.py install
```

As always, I highly recommend using the [Pipenv](https://github.com/pypa/pipenv)
package to help manage dependencies!

## Quickstart

After installation, using pyspellchecker should be fairly straight forward:

``` python
from spellchecker import SpellChecker


spell = SpellChecker()

# find those words that may be misspelled
misspelled = spell.unknown(['something', 'is', 'hapenning', 'here'])

for word in misspelled:
    # Get the one `most likely` answer
    print(spell.correction(word))

    # Get a list of `likely` options
    print(spell.candidates(word))
```
