from build_dictionary import load_file
import json
import gzip
import shutil

MINIMUM_FREQUENCY = 50

# Read the nl.json generated with build_dictionary.py
with load_file("data/nl_full.json.gz", encoding="utf-8") as f:
    word_frequency_json = json.load(f)

print(f"There are {len(word_frequency_json.keys())} words in data/nl_full.json.gz")

with load_file("data/nl_include.txt", encoding="utf-8") as f:
    words_to_include = f.read().split("\n")

print(f"There are {len(words_to_include)} words in data/nl_include.txt")

with load_file("data/nl_exclude.txt", encoding="utf-8") as f:
    words_to_exclude = f.read().split("\n")

print(f"There are {len(words_to_exclude)} words in data/nl_include.txt")

for word in words_to_include:
    frequency = word_frequency_json.get(word, 0)
    word_frequency_json[word] = frequency + MINIMUM_FREQUENCY

print(f"There are {len(word_frequency_json.keys())} words after adding words in data/nl_include.txt")

for word in words_to_exclude:
    del word_frequency_json[word.strip()]

print(f"There are {len(word_frequency_json.keys())} words after removing words in data/nl_exclude.txt")
print("Write resulting dict in json to data/nl.json")

with open("data/nl.json", "w") as f:
    json.dump(word_frequency_json, f, indent="", sort_keys=True, ensure_ascii=False)

# Compress the JSON file data/nl.json
with open("data/nl.json", "rb") as f_in:
    with gzip.open("data/nl.json.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
