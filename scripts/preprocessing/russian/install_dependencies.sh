#!/bin/bash
pip install -U pip setuptools wheel spacy==3.0.5
python -m spacy download ru_core_news_sm
pip install git+https://github.com/natasha/corus.git
wget https://github.com/yutkin/Lenta.Ru-News-Dataset/releases/download/v1.1/lenta-ru-news.csv.bz2
wget http://opencorpora.org/files/export/dict/dict.opcorpora.txt.bz2
