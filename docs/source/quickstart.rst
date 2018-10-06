.. _quickstart:

Quickstart
===============================================================================

``pyspellchecker`` is designed to be easy to use to get basic spell checking.

Installation
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The best experience is likely to use ``pip``:

.. code:: bash

    pip install pyspellchecker

If you are using virtual environments, it is recommended to use ``pipenv`` to
combine pip and virtual environments:

.. code:: bash

    pipenv install pyspellchecker

Read more about `Pipenv <https://github.com/pypa/pipenv>`__


Basic Usage
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Setting up the spell checker requires importing and initializing the instance.

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()


There are several methods to determine if a word is in the word frequency list:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell['morning']  # True
    'morning' in spell  # True

    # find those words from a list of words that are found in the dictionary
    spell.known(['morning', 'hapenning'])  # {'morning'}

    # find those words from a list of words that are not found in the dictionary
    spell.unknown(['morning', 'hapenning'])  # {'hapenning'}


Once a word is identified as misspelled, you can find the likeliest replacement:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()

    misspelled = spell.unknown(['morning', 'hapenning'])  # {'hapenning'}
    for word in misspelled:
        spell.correction(word)  # 'happening'


.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker(distance=1)  # set the Levenshtein Distance parameter

    # do additional work

    # now for shorter words, we can revert to Levenshtein Distance of 2!
    spell.distance = 2


Or if the word identified as the likeliest is not correct, a list of candidates
can also be pulled:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()

    misspelled = spell.unknown(['morning', 'hapenning'])  # {'hapenning'}
    for word in misspelled:
        spell.correction(word)  # {'penning', 'happening', 'henning'}


Changing Language
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To set the language of the dictionary to load, one must set the language
parameter on initialization.

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker(language='es')  # Spanish dictionary
    print(spell['mañana'])


Adding and Removing Terms from a Dictionary
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

There are several ways to add additional terms to your word frequency dictionary
including by filepath, string of text, or by a list of words.


To load a pre-defined dictionary file (either as a json file or a gzipped json
file):

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell.word_frequency.load_dictionary('./path-to-my-word-frequency.json')


To load a text document that will be parsed into individual words and each word
added to the frequency list:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell.word_frequency.load_text_file('./path-to-my-text-doc.txt')


To load plain text from input or another source:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell.word_frequency.load_text('Text to be parsed and added to the system')


Or update using a list of words:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell.word_frequency.load_words(['Text', 'to', 'be','added', 'to', 'the', 'system'])


Or add a single word:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell.word_frequency.add('Text')


Removing words is as simple as adding words:

.. code:: python

    from spellchecker import SpellChecker

    spell = SpellChecker()
    spell.word_frequency.remove_words(['Text', 'to', 'be','removed', 'from', 'the', 'system'])

    # or remove a single word
    spell.word_frequency.remove('meh')
