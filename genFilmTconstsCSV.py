"""
Maps film titles from the JSON file of Giitayan songs to unique IMDb IDs using the publicly-accessible TSV titles file.
Writes the mappings to a CSV file.
"""

import json
import csv

SONGS_JSON_FILE = "all_songs.json"
TITLE_BASICS_TSV_FILE = "title.basics.tsv"
OUTPUT_CSV_FILE = "film_tconsts.csv"

# Loads information from the JSON file of song data.
print(f"Loading song data from {SONGS_JSON_FILE}...")
try:
    with open(SONGS_JSON_FILE, "r", encoding="utf-8") as f:
        song_data = json.load(f)
except FileNotFoundError:
    print(f"Error: Input file not found: {SONGS_JSON_FILE}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {SONGS_JSON_FILE}. Is the file valid?")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while loading {SONGS_JSON_FILE}: {e}")
    exit(1)

# Extracts film information from the JSON file of song data.
print("Extracting unique (film title, year) combinations...")
film_set = set()
for entry in song_data:
    film_title = entry.get("film")
    if film_title:
        normalized_title = film_title.strip().lower()
        year = entry.get("year")
        film_set.add((normalized_title, year))

print(f"Found {len(film_set)} unique (film, year) combinations.")

print(f"Reading {TITLE_BASICS_TSV_FILE} and mapping films to IDs...")
film_to_id = {}

# Matches film titles to IDs from the TSV titles file.
try:
    with open(TITLE_BASICS_TSV_FILE, "rt", encoding="utf-8") as f:
        headers = f.readline().strip().split('\t')
        required = ["tconst", "titleType", "primaryTitle", "startYear"]
        if not all(h in headers for h in required):
            missing = [h for h in required if h not in headers]
            print(f"Error: Missing required columns in {TITLE_BASICS_TSV_FILE}: {missing}")
            exit(1)

        processed_lines = 0
        matched_films = 0

        for line in f:
            processed_lines += 1
            cols = line.strip().split('\t')
            if len(cols) != len(headers):
                continue

            entry = dict(zip(headers, cols))
            if entry.get("titleType") != "movie":
                continue

            title = entry.get("primaryTitle", "").strip().lower()
            year_str = entry.get("startYear", "\\N")

            year_int = None
            if year_str != "\\N":
                try:
                    year_int = int(year_str)
                except ValueError:
                    continue

            key = (title, year_int)
            if key in film_set:
                tconst = entry.get("tconst")
                if tconst and tconst != r'\N':
                    film_to_id[key] = tconst
                    matched_films += 1

            if processed_lines % 100000 == 0:
                print(f"  Processed {processed_lines} lines...")

except FileNotFoundError:
    print(f"Error: Input file not found: {TITLE_BASICS_TSV_FILE}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while reading {TITLE_BASICS_TSV_FILE}: {e}")
    exit(1)

# Determines the number of successful mappings.
print(f"Finished reading TSV. Found IDs for {len(film_to_id)} films.")
unmatched_count = len(film_set) - len(film_to_id)
if unmatched_count > 0:
    print(f"Warning: Could not find IDs for {unmatched_count} film entries.")

# Writes title-ID mappings to CSV file.
print(f"Writing results to {OUTPUT_CSV_FILE}...")
try:
    with open(OUTPUT_CSV_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["primaryTitle", "tconst"])
        for (film, year), tconst in film_to_id.items():
            writer.writerow([film.title(), tconst])

    print(f"Successfully saved mappings to {OUTPUT_CSV_FILE}")

except IOError as e:
    print(f"Error writing to {OUTPUT_CSV_FILE}: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while writing the CSV: {e}")
    exit(1)

print("Script finished.")
