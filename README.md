# Song Metadata IMDb Linker Project (CWL 207 Final Project)

## Overview

This project automates the process of fetching song metadata from a specific online source, extracting relevant information (like film title, year, associated people), and then linking these films and people to their respective unique identifiers (tconst and nconst) from IMDb datasets.

The project consists of three main scripts that should be run sequentially:

1.  **Fetch Song Data:** Downloads song metadata files, parses them, and creates a structured JSON file (`all_songs.json`).
2.  **Map People to IMDb IDs:** Reads the JSON file and maps the extracted people's names to their IMDb `nconst` using the `name.basics.tsv` dataset. Outputs `people_nconsts.csv`.
3.  **Map Films to IMDb IDs:** Reads the JSON file and maps the extracted film titles (along with their release year) to their IMDb `tconst` using the `title.basics.tsv` dataset. Outputs `film_tconsts.csv`.

## Prerequisites

### 1. Software
* **Python 3:** Ensure you have Python 3 installed on your system. You can download it from [python.org](https://www.python.org/).
* **Python Libraries:** You need the `requests` library. Install it using pip:
    ```bash
    pip install requests
    ```
    *(The `json` and `csv` libraries are included with Python)*

### 2. Data Files (IMDb Datasets)
This project requires two dataset files from IMDb's non-commercial datasets.

* **Go to:** [IMDb Non-Commercial Datasets Page](https://developer.imdb.com/non-commercial-datasets/)
* **Download the following files:**
    * `name.basics.tsv.gz` - Contains information about people (actors, directors, etc.).
    * `title.basics.tsv.gz` - Contains information about titles (movies, TV shows, etc.).
* **Unzip the files:** After downloading, you need to unzip both `.gz` files. You can use tools like 7-Zip (Windows), Keka (macOS), or the `gunzip` command (Linux/macOS):
    ```bash
    gunzip name.basics.tsv.gz
    gunzip title.basics.tsv.gz
    ```
* **Place the files:** Make sure the unzipped `name.basics.tsv` and `title.basics.tsv` files are located in the **same directory** as the Python scripts.

## Project Files

├── 01_fetch_song_data.py      # Script to fetch and parse song metadata
├── 02_map_names_to_nconst.py  # Script to map people to IMDb IDs (nconst)
├── 03_map_films_to_tconst.py  # Script to map films to IMDb IDs (tconst)
├── name.basics.tsv            # (Downloaded and unzipped from IMDb)
├── title.basics.tsv           # (Downloaded and unzipped from IMDb)
├── README.md                  # This file
--- Output files (will be generated after running scripts) ---

├── all_songs.json             # Output of script 01
├── people_nconsts.csv         # Output of script 02
├── film_tconsts.csv           # Output of script 03


*(Note: You might need to rename your script files to match `01_...`, `02_...`, `03_...` if you haven't already, or adjust the commands below accordingly.)*

## How to Use

Run the scripts sequentially from your terminal in the project directory:

1.  **Fetch and Parse Song Data:**
    ```bash
    python 01_fetch_song_data.py
    ```
    This will create the `all_songs.json` file. Wait for it to complete before proceeding.

2.  **Map People Names to IMDb IDs:**
    ```bash
    python 02_map_names_to_nconst.py
    ```
    This reads `all_songs.json` and `name.basics.tsv`, then creates `people_nconsts.csv`.

3.  **Map Film Titles to IMDb IDs:**
    ```bash
    python 03_map_films_to_tconst.py
    ```
    This reads `all_songs.json` and `title.basics.tsv`, then creates `film_tconsts.csv`.

## Output Files Description

* **`all_songs.json`**: A JSON array where each object represents a song and contains:
    * `id`: The original identifier from the source.
    * `film`: The associated film title (string or null).
    * `year`: The release year of the film (integer or null).
    * `people`: A sorted list of unique names (actors, singers, etc.) associated with the song.
* **`people_nconsts.csv`**: A CSV file mapping cleaned, title-cased names found in the songs to their corresponding IMDb `nconst` identifier. Contains columns: `primaryName`, `nconst`.
* **`film_tconsts.csv`**: A CSV file mapping cleaned, title-cased film titles found in the songs to their corresponding IMDb `tconst` identifier. Contains columns: `primaryTitle`, `tconst`. (Note: The year is used for matching but not included in this output file).

