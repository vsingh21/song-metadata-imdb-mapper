# Song Metadata IMDb Linker Project (CWL 207 Final Project)

## Overview

This project automates the process of fetching song metadata from a specific online [source](https://www.giitaayan.com/), extracting relevant information (like film title, year of release, associated people) if such data is available, and then linking these films and people to their respective unique identifiers (tconst and nconst) from IMDb datasets in the final output files.

The project consists of three main scripts that should be run sequentially:

1.  **Fetch Song Data:** The file `getGiitaayanData.py` downloads song metadata files, parses them, and creates a structured JSON file (`all_songs.json`).
2.  **Map People to IMDb IDs:** The file `genPeopleNconstsCSV.py` reads the JSON file and maps each extracted person's name to their IMDb `nconst` using the `name.basics.tsv` dataset. Outputs `people_nconsts.csv`.
3.  **Map Films to IMDb IDs:** The file `genFilmTconstsCSV.py` reads the JSON file and maps the extracted film titles (along with their release year) to their IMDb `tconst` using the `title.basics.tsv` dataset. Outputs `film_tconsts.csv`.

## Prerequisites

### 1. Data Files (IMDb Datasets)
This project requires two dataset files from IMDb's non-commercial datasets:

* **Go to:** [IMDb Non-Commercial Datasets Page](https://developer.imdb.com/non-commercial-datasets/)
* **Download the following files:**
    * `name.basics.tsv.gz` - Contains information about people referenced in a given song related to either the film of use or those involved in the song's production.
    * `title.basics.tsv.gz` - Contains information about film titles that featured a given song.
* **Place the unzipped files:** Make sure the unzipped `name.basics.tsv` and `title.basics.tsv` files are located in the **same directory** as the Python scripts.

## Project Files

```
├── getGiitaayanData.py         # Script to fetch and parse song metadata  
├── genPeopleNconstsCSV.py      # Script to map people to IMDb IDs (nconst)  
├── genFilmTconstsCSV.py        # Script to map films to IMDb IDs (tconst)  
├── name.basics.tsv             # IMDb dataset (downloaded and unzipped)  
├── title.basics.tsv            # IMDb dataset (downloaded and unzipped)  
├── README.md                   # This file  
```

### Output Files  
*Generated after running the scripts above:*

```
├── all_songs.json              
├── people_nconsts.csv          
├── film_tconsts.csv            
```

## How to Use

Run the scripts sequentially from your terminal in the project directory:

1.  **Fetch and Parse Song Data:**
    ```bash
    python getGiitaayanData.py
    ```
    This will create the `all_songs.json` file. Wait for it to complete before proceeding.

2.  **Map People Names to IMDb IDs:**
    ```bash
    python genPeopleNconstsCSV.py
    ```
    This reads `all_songs.json` and `name.basics.tsv`, then creates `people_nconsts.csv`.

3.  **Map Film Titles to IMDb IDs:**
    ```bash
    python genFilmTconstsCSV.py
    ```
    This reads `all_songs.json` and `title.basics.tsv`, then creates `film_tconsts.csv`.

## Output Files Description

* **`all_songs.json`**: A JSON array where each object represents a song and contains:
    * `id`: The original identifier from the Giitaayan database.
    * `film`: The associated film title (string or null).
    * `year`: The release year of the film (integer or null).
    * `people`: A sorted list of unique names (actors, singers, etc.) associated with the song.
* **`people_nconsts.csv`**: A CSV file mapping cleaned names related to the songs to their corresponding IMDb `nconst` identifier. Contains columns: `primaryName`, `nconst`.
* **`film_tconsts.csv`**: A CSV file mapping cleaned film titles which used a given song to their corresponding IMDb `tconst` identifier. Contains columns: `primaryTitle`, `tconst`. (Note: The year is used for matching but not included in this output file).

