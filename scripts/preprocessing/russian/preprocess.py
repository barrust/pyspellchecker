import bz2
import re

import spacy
from corus import load_lenta2
from tqdm import tqdm


def clear_sent(sent):
    """Remove all non-letters symbols, except `-`

    Args:
        sent (str): Sentence

    Returns:
        str: Cleared sentence
    """
    sent = re.sub(r'[^-\w]+', ' ', sent)
    sent = re.sub(r'(\s-\s*|-\s+)', ' ', sent)
    return sent.strip()


def get_records_total_num():
    """Get total numbers of texts in lenta.ru dataset

    Returns:
        int: Total number of texts
    """
    records = load_lenta2('lenta-ru-news.csv.bz2')
    for i, _ in enumerate(records, 1):
        pass
    return i


def preprocess_lenta2_dataset():
    """Create textfile, where each row is a cleared sentence
    """
    nlp = spacy.load('ru_core_news_sm')
    records = load_lenta2('lenta-ru-news.csv.bz2')

    with open('ru_lenta.txt', 'a+') as file:
        for record in tqdm(records, total=800975, desc="Dataset"):
            text = record.text
            sents = nlp(text).sents
            for sent in sents:
                file.write(clear_sent(sent.text))
                file.write('\n')


def get_opcorpora_total_num():
    """Get total numbers of rows in opcorpora.txt.bz2

    Returns:
        int: Total number of rows
    """
    with bz2.open('dict.opcorpora.txt.bz2', 'rt') as archive:
        for i, _ in enumerate(archive, 1):
            pass
    return i


def generate_include_file():
    """Create textfile, where each row is a word, which should be added 
    to the dictionary
    """
    with bz2.open('dict.opcorpora.txt.bz2', 'rt') as archive:
        with open('ru_include.txt', 'w+') as file:
            for line in tqdm(archive, total=5924073, desc="Include"):
                line = line.strip()
                if (not line) or line.isdigit():
                    continue

                word = line.lower().split('\t', 1)[0]
                file.write(f"{word}\n")


if __name__ == '__main__':
    preprocess_lenta2_dataset()
    generate_include_file()
