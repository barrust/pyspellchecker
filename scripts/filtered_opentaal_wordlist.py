""" Desc:   A script to download list of approved Dutch words made by OpenTaal.
            Exclude word in nl.json that are not in list by Opentaal.
            Add all words of opentaal list with frequency 50 or if they excist already increase
            the frequency with 50.
    Author: Lode Nachtergaele
"""

import sys
import requests
import json
from collections import Counter
from pathlib import Path

MINIMUM_FREQUENCY = 50

wordlist_file = Path("nl_opentaal_wordlist.txt")

if not wordlist_file.exists():
    url = "https://raw.githubusercontent.com/OpenTaal/opentaal-wordlist/master/wordlist.txt"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        with open("nl_opentaal_wordlist.txt", mode="wb") as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download nl_opentaal_wordlist.txt. Status code:", response.status_code)
        sys.Exit()

word_opentaal_json = Counter()
with open("nl_opentaal_wordlist.txt", mode="r", encoding="utf-8") as file:
    for word in file:
        word_opentaal_json[word.strip()] = MINIMUM_FREQUENCY

with open("nl_opentaal_wordlist.json", mode="w", encoding="utf-8") as f:
    json.dump(word_opentaal_json, f, indent="", sort_keys=True, ensure_ascii=False)
print("Created file nl_opentaal_wordlist.json with all known dutch words correctly spelled.")
print("Compress the file with: gzip nl_opentaal_wordlist.json")

# Read the nl.json generated with build_dictionary.py
with open("nl.json", mode="r", encoding="utf-8") as f:
    word_frequency_json = json.load(f)

# Remove words that do not appear in opentaal list and
# create a list of excluded words
opentaal_words = set(word_opentaal_json.keys())
excluded_words = {}
for word, frequency in word_frequency_json.items():
    if word not in opentaal_words:
        excluded_words[word] = frequency

# Write the excluded words to file nl_exclude.txt
with open("nl_exclude.txt", mode="w", encoding="utf-8") as f:
    sorted_excluded_words = sorted(excluded_words.items(), key=lambda x: x[1])
    for excluded_word, frequency in sorted_excluded_words:
        f.write(f"{excluded_word} \n")
