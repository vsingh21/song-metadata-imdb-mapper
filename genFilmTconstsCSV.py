# -*- coding: utf-8 -*-
"""
Processes the 'all_songs.json' file and a TSV file containing title information
(e.g., IMDb's title.basics.tsv) to map unique film titles and their release years
found in the song data to their corresponding unique IMDb title identifiers (tconst).

The script performs the following steps:
1. Loads the song data from 'all_songs.json'.
2. Extracts all unique combinations of (film title, year) from the song data.
   Titles are normalized (stripped, lowercased) for matching.
3. Reads the 'title.basics.tsv' file line by line.
4. Filters the TSV data to include only entries where 'titleType' is 'movie'.
5. For each movie entry in the TSV, it normalizes the title and year.
6. Checks if the normalized (title, year) combination from the TSV exists
   in the set extracted from the song data.
7. If a match is found, it stores the mapping from the (title, year) tuple
   to the title's 'tconst'.
8. Finally, it writes these mappings (Title, tconst) into a CSV file named
   'film_tconsts.csv'.
"""

import json  # For loading the JSON data file.
import csv   # For writing the output data in CSV format.

# --- Configuration ---
SONGS_JSON_FILE = "all_songs.json"          # Input JSON file containing song data.
TITLE_BASICS_TSV_FILE = "title.basics.tsv" # Input TSV file with title details (e.g., from IMDb).
OUTPUT_CSV_FILE = "film_tconsts.csv"     # Output CSV file for film title-ID mappings.

# --- Step 1: Load song data and extract unique film-year combinations ---

print(f"Loading song data from {SONGS_JSON_FILE}...")
try:
    # Open and load the JSON file containing the list of song dictionaries.
    with open(SONGS_JSON_FILE, "r", encoding="utf-8") as f:
        song_data = json.load(f)
except FileNotFoundError:
    print(f"Error: Input file not found: {SONGS_JSON_FILE}")
    exit(1) # Exit if the essential input file is missing.
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {SONGS_JSON_FILE}. Is the file valid?")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while loading {SONGS_JSON_FILE}: {e}")
    exit(1)

print("Extracting unique (film title, year) combinations from song data...")
# Use a set to store unique tuples of (lowercase_film_title, year).
# This efficiently handles duplicates and prepares for quick lookups later.
film_set = set()
# Iterate through each song dictionary in the loaded list.
for entry in song_data:
    # Process only if the 'film' key exists and its value is not empty/None.
    film_title = entry.get("film")
    if film_title:
        # Normalize the film title: remove leading/trailing whitespace and convert to lowercase.
        normalized_title = film_title.strip().lower()
        # Get the year associated with the film entry.
        year = entry.get("year") # Year should already be int or None from previous script
        # Add the (normalized_title, year) tuple to the set.
        # This automatically handles duplicates. Year can be None here.
        film_set.add((normalized_title, year))

print(f"Found {len(film_set)} unique (film, year) combinations in song data.")

# --- Step 2: Map film-year combinations to tconst from title.basics.tsv ---

print(f"Reading {TITLE_BASICS_TSV_FILE} and mapping films to IDs...")
# Dictionary to store the mapping: {(lowercase_title, year): tconst}
film_to_id = {}

try:
    # Open the TSV file containing title basics. 'rt' mode is read text (default).
    with open(TITLE_BASICS_TSV_FILE, "rt", encoding="utf-8") as f:
        # Read the header line and split into column names.
        headers = f.readline().strip().split('\t')
        print(f"TSV Headers found: {headers}")

        # Check if essential columns are present
        required_headers = ["tconst", "titleType", "primaryTitle", "startYear"]
        if not all(h in headers for h in required_headers):
            missing = [h for h in required_headers if h not in headers]
            print(f"Error: Missing required columns in {TITLE_BASICS_TSV_FILE}: {missing}")
            exit(1)

        processed_lines = 0
        matched_films = 0
        # Process each subsequent line representing a title entry.
        for line in f:
            processed_lines += 1
            # Split the line into fields based on the tab delimiter.
            cols = line.strip().split('\t')
            # Ensure the number of fields matches the number of headers.
            if len(cols) != len(headers):
                # print(f"Warning: Skipping line {processed_lines + 1} due to mismatched field count ({len(cols)} fields, expected {len(headers)}). Line: '{line.strip()}'")
                continue # Skip malformed lines

            # Create a dictionary mapping header names to column values for easy access.
            entry_dict = dict(zip(headers, cols))

            # --- Filtering: Only process entries that are movies ---
            # IMDb's titleType column specifies the type (movie, tvSeries, short, etc.)
            if entry_dict.get("titleType") != "movie":
                continue # Skip this entry if it's not a movie.

            # --- Data Extraction and Normalization ---
            # Extract the primary title, strip whitespace, and convert to lowercase.
            title = entry_dict.get("primaryTitle", "").strip().lower()
            # Extract the start year.
            year_str = entry_dict.get("startYear", "\\N") # Default to \N if missing

            # Convert year string to integer if it's not the null value "\\N".
            # Handle potential errors during conversion, although "\\N" check helps.
            year_int = None
            if year_str != "\\N":
                try:
                    year_int = int(year_str)
                except ValueError:
                    # print(f"Warning: Skipping line {processed_lines + 1} due to invalid year format: '{year_str}'")
                    continue # Skip if year is not a valid integer

            # --- Matching ---
            # Create the key tuple (normalized_title, year_integer) for lookup.
            lookup_key = (title, year_int)

            # Check if this exact (title, year) combination exists in the set
            # derived from our initial song data.
            if lookup_key in film_set:
                # If a match is found, map this key to the title's unique ID (tconst).
                tconst = entry_dict.get("tconst")
                if tconst and tconst != r'\N': # Ensure tconst is valid
                    # Store the mapping. If multiple tconst match the same key,
                    # the last one encountered in the file will overwrite previous ones.
                    film_to_id[lookup_key] = tconst
                    matched_films += 1
                    # Optional: Remove from set if assuming one-to-one mapping needed
                    # film_set.remove(lookup_key)

            # Optional: Add progress indicator for large files
            if processed_lines % 100000 == 0:
                 print(f"  Processed {processed_lines} lines from TSV...")


except FileNotFoundError:
    print(f"Error: Input file not found: {TITLE_BASICS_TSV_FILE}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while reading {TITLE_BASICS_TSV_FILE}: {e}")
    exit(1)

print(f"Finished reading TSV. Processed {processed_lines} lines. Found IDs for {len(film_to_id)} films.")
unmatched_count = len(film_set) - len(film_to_id)
if unmatched_count > 0 :
    print(f"Warning: Could not find IDs for {unmatched_count} (film, year) combinations from the song data.")


# --- Step 3: Write the results to a CSV file ---

print(f"Writing results to {OUTPUT_CSV_FILE}...")
try:
    # Open the output CSV file in write mode.
    with open(OUTPUT_CSV_FILE, "w", newline='', encoding="utf-8") as f:
        # Create a CSV writer object.
        writer = csv.writer(f)
        # Write the header row.
        writer.writerow(["primaryTitle", "tconst"]) # Note: Year is not written, only used for matching.
        # Iterate through the dictionary containing the {(film, year): tconst} mappings.
        for (film, year), tconst in film_to_id.items():
            # Write the film title (capitalized) and its corresponding tconst.
            # The year is part of the key used for matching but isn't written here by default.
            writer.writerow([film.title(), tconst])

    print(f"Successfully saved film title-ID mappings to {OUTPUT_CSV_FILE}")

except IOError as e:
    print(f"Error writing to {OUTPUT_CSV_FILE}: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while writing the CSV: {e}")
    exit(1)

print("Script finished.")