pyspellchecker
===============================================================================

.. image:: https://badge.fury.io/py/pyspellchecker.svg
    :target: https://badge.fury.io/py/pyspellchecker
.. image:: https://travis-ci.org/barrust/pyspellchecker.svg?branch=master
    :target: https://travis-ci.org/barrust/pyspellchecker
.. image:: https://coveralls.io/repos/github/barrust/pyspellchecker/badge.svg?branch=master
    :target: https://coveralls.io/github/barrust/pyspellchecker?branch=master
.. image:: http://pepy.tech/badge/pyspellchecker
    :target: http://pepy.tech/count/pyspellchecker
    :alt: Downloads


Pure Python Spell Checking based on `Peter
Norvig's <https://norvig.com/spell-correct.html>`__ blog post on setting
up a simple spell checking algorithm.

It uses a `Levenshtein Distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`__
algorithm to find permutations within an edit distance of 2 from the
original word. It then compares all permutations (insertions, deletions,
replacements, and transpositions) to known words in a word frequency
list. Those words that are found more often in the frequency list are
**more likely** the correct results.

``pyspellchecker`` supports multiple languages including English, Spanish,
German, French, and Portuguese. Dictionaries were generated using
the `WordFrequency project <https://github.com/hermitdave/FrequencyWords>`__ on GitHub.

``pyspellchecker`` supports **Python 3** and Python 2.7 but, as always, Python 3
is the preferred version!

``pyspellchecker`` allows for the setting of the Levenshtein Distance to check.
For longer words, it is highly recommended to use a distance of 1 and not the
default 2. See the quickstart to find how one can change the distance parameter.


Installation
-------------------------------------------------------------------------------

The easiest method to install is using pip:

.. code:: bash

    pip install pyspellchecker

To install from source:

.. code:: bash

    git clone https://github.com/barrust/pyspellchecker.git
    cd pyspellchecker
    python setup.py install

As always, I highly recommend using the
`Pipenv <https://github.com/pypa/pipenv>`__ package to help manage
dependencies!


Quickstart
-------------------------------------------------------------------------------

After installation, using ``pyspellchecker`` should be fairly straight
forward:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()

    # find those words that may be misspelled
    misspelled = spell.unknown(['something', 'is', 'hapenning', 'here'])

    for word in misspelled:
        # Get the one `most likely` answer
        print(spell.correction(word))

        # Get a list of `likely` options
        print(spell.candidates(word))



If the Word Frequency list is not to your liking, you can add additional
text to generate a more appropriate list for your use case.

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()  # loads default word frequency list
    spell.word_frequency.load_text_file('./my_free_text_doc.txt')

    # if I just want to make sure some words are not flagged as misspelled
    spell.word_frequency.load_words(['microsoft', 'apple', 'google'])
    spell.known(['microsoft', 'google'])  # will return both now!


If the words that you wish to check are long, it is recommended to reduce the
`distance` to 1. This can be accomplished either when initializing the spell
check class or after the fact.

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker(distance=1)  # set at initialization

    # do some work on longer words

    spell.distance = 2  # set the distance parameter back to the default



Additional Methods
-------------------------------------------------------------------------------

`On-line documentation <http://pyspellchecker.readthedocs.io/en/latest/>`__ is available; below contains the cliff-notes version of some of the available functions:


``correction(word)``: Returns the most probable result for the
misspelled word

``candidates(word)``: Returns a set of possible candidates for the
misspelled word

``known([words])``: Returns those words that are in the word frequency
list

``unknown([words])``: Returns those words that are not in the frequency
list

``word_probability(word)``: The frequency of the given word out of all
words in the frequency list

The following are less likely to be needed by the user but are available:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``edit_distance_1(word)``: Returns a set of all strings at a Levenshtein
Distance of one based on the alphabet of the selected language

``edit_distance_2(word)``: Returns a set of all strings at a Levenshtein
Distance of two based on the alphabet of the selected language


Credits
-------------------------------------------------------------------------------

* `Peter Norvig <https://norvig.com/spell-correct.html>`__ blog post on setting up a simple spell checking algorithm

* `hermetdave's WordFrequency project <https://github.com/hermitdave/FrequencyWords>`__ for providing the basis for Non-English dictionaries
