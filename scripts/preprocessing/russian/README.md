# Preprocess for Russian language

Defaut russian dataset from OpenSubtitles isn't so big and don't so useful, good baseline, but it could be done much better using large datasets.

To create a dictionary on more then 3 million words we need:

1. Install dependencies. __Dont forget to activate virtual environment!__
    
    ```sh
    cd scripts/preprocessing/russian
    ./install_dependencies.sh
    ```

    This will automatically install `spaCy`, `corus` libraries and download datasets.

2. Run `preprocess.py` file

    ```sh
    python preprocess.py
    ```

    Preprocessing lenta.ru dataset will dure ~5 hours (I suggest you use `screen` terminal tool, to avoid accidental closing terminal session)

    After script finish its work, two files will appear: `ru_lenta.txt` and 
    `ru_include.txt`

3. Copy `ru_include.txt` to `scripts/data`

After all of this steps, you could run `build_dictionary.py` using `ru_lenta.txt` with `-f` tag.