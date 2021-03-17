import re

import spacy
from corus import load_lenta2

from tqdm import tqdm


def clear_sent(sent):
    sent = re.sub(r'[^-\w]+', ' ', sent.text)
    sent = re.sub(r'(\s-\s*|-\s+)', ' ', sent)
    return sent.strip()


def get_records_total_num():
    records = load_lenta2('lenta-ru-news.csv.bz2')
    for i, _ in enumerate(records):
        pass
    return i + 1


def preprocess_lenta2_dataset():
    records = load_lenta2('lenta-ru-news.csv.bz2')
    total_records = 800975

    nlp = spacy.load('ru_core_news_sm')

    with open('ru_lenta.txt', 'a+') as file:
        for record in tqdm(records, total=total_records):
            text = record.text
            sents = nlp(text).sents
            for sent in sents:
                file.write(clear_sent(sent))
                file.write('\n')


if __name__ == '__main__':
    # print(get_records_total_num())
    preprocess_lenta2_dataset()
