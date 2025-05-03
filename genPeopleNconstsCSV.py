# -*- coding: utf-8 -*-
"""
Processes the 'all_songs.json' file (created by the previous script) and
a TSV file containing name information (e.g., IMDb's name.basics.tsv)
to map unique person names found in the song data to their corresponding
unique identifiers (like IMDb's nconst).

The script performs the following steps:
1. Loads the song data from 'all_songs.json'.
2. Extracts all unique, lowercased names from the 'people' lists within the song data.
3. Reads the 'name.basics.tsv' file line by line.
4. For each entry in the TSV, it checks if the 'primaryName' matches any name
   extracted from the song data.
5. If a match is found, it stores the mapping between the name and its 'nconst'.
6. Finally, it writes these mappings (Name, nconst) into a CSV file named
   'people_nconsts.csv'.
"""

import json  # For loading the JSON data file.
import csv   # For writing the output data in CSV format.

# --- Configuration ---
SONGS_JSON_FILE = "all_songs.json"          # Input JSON file containing song data.
NAME_BASICS_TSV_FILE = "name.basics.tsv"   # Input TSV file with name details (e.g., from IMDb).
OUTPUT_CSV_FILE = "people_nconsts.csv"     # Output CSV file for name-ID mappings.

# --- Step 1: Load people names from all_songs.json ---

print(f"Loading song data from {SONGS_JSON_FILE}...")
try:
    # Open and load the JSON file containing the list of song dictionaries.
    with open(SONGS_JSON_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f)
except FileNotFoundError:
    print(f"Error: Input file not found: {SONGS_JSON_FILE}")
    exit(1) # Exit if the essential input file is missing.
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {SONGS_JSON_FILE}. Is the file valid?")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while loading {SONGS_JSON_FILE}: {e}")
    exit(1)

print("Extracting unique names from song data...")
# Use a set to store unique names efficiently. Names are converted to lowercase
# for case-insensitive matching later.
people_set = set()
# Iterate through each song dictionary in the loaded list.
for song in songs:
    # Safely get the 'people' list using .get() which returns [] if 'people' key doesn't exist.
    people = song.get("people", [])
    # Iterate through each person's name in the list for the current song.
    for person in people:
        # Clean the name: remove leading/trailing whitespace and convert to lowercase.
        name = person.strip().lower()
        # Add the cleaned name to the set if it's not an empty string.
        if name:
            people_set.add(name)

print(f"Found {len(people_set)} unique names in song data.")

# --- Step 2: Map extracted people names to nconst from name.basics.tsv ---

print(f"Reading {NAME_BASICS_TSV_FILE} and mapping names to IDs...")
# Dictionary to store the mapping: {lowercase_name: nconst}
name_to_id = {}

try:
    # Open the TSV file containing name basics.
    with open(NAME_BASICS_TSV_FILE, "r", encoding="utf-8") as f:
        # Read the first line to get the headers (e.g., "nconst", "primaryName", ...).
        # Strip whitespace and split by tab character to get a list of headers.
        headers = f.readline().strip().split('\t')
        print(f"TSV Headers found: {headers}") # Log headers for verification

        # Check if essential columns are present
        if "primaryName" not in headers or "nconst" not in headers:
            print(f"Error: Missing required columns 'primaryName' or 'nconst' in {NAME_BASICS_TSV_FILE}")
            exit(1)

        processed_lines = 0
        matched_names = 0
        # Process each subsequent line in the TSV file.
        for line in f:
            processed_lines += 1
            # Split the line into fields based on the tab delimiter.
            fields = line.strip().split('\t')
            # Ensure the number of fields matches the number of headers to avoid errors.
            if len(fields) != len(headers):
                # print(f"Warning: Skipping line {processed_lines + 1} due to mismatched field count ({len(fields)} fields, expected {len(headers)}). Line: '{line.strip()}'")
                continue # Skip malformed lines

            # Create a dictionary mapping header names to field values for the current line.
            entry = dict(zip(headers, fields))

            # Extract the primary name, clean it (strip whitespace, lowercase).
            name = entry.get("primaryName", "").strip().lower() # Use .get for safety

            # Check if this cleaned name exists in the set of names derived from the song data.
            if name in people_set:
                # If it's a match, store the mapping from the name to the nconst.
                # Use .get for safety in case 'nconst' column was missing despite header check
                nconst = entry.get("nconst")
                if nconst and nconst != r'\N': # Ensure nconst is valid (IMDb uses \N for null)
                    name_to_id[name] = nconst
                    matched_names += 1
                    # Optional: Remove found name from set to potentially speed up future lookups?
                    # people_set.remove(name) # Be careful if multiple nconsts could map to one name

            # Optional: Add progress indicator for large files
            if processed_lines % 100000 == 0:
                 print(f"  Processed {processed_lines} lines from TSV...")


except FileNotFoundError:
    print(f"Error: Input file not found: {NAME_BASICS_TSV_FILE}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while reading {NAME_BASICS_TSV_FILE}: {e}")
    exit(1)

print(f"Finished reading TSV. Processed {processed_lines} lines. Found IDs for {len(name_to_id)} names.")
unmatched_count = len(people_set) - len(name_to_id)
if unmatched_count > 0 :
    print(f"Warning: Could not find IDs for {unmatched_count} names from the song data.")


# --- Step 3: Write the results to a CSV file ---

print(f"Writing results to {OUTPUT_CSV_FILE}...")
try:
    # Open the output CSV file in write mode.
    # newline='' prevents extra blank rows in the CSV on Windows.
    # encoding='utf-8' ensures proper handling of various characters.
    with open(OUTPUT_CSV_FILE, "w", newline='', encoding="utf-8") as f:
        # Create a CSV writer object.
        writer = csv.writer(f)
        # Write the header row to the CSV file.
        writer.writerow(["primaryName", "nconst"])
        # Iterate through the dictionary containing the name-ID mappings.
        for name, nconst in name_to_id.items():
            # Write each mapping as a row in the CSV.
            # Convert the name back to Title Case for better readability in the output file.
            writer.writerow([name.title(), nconst])

    print(f"Successfully saved name-ID mappings to {OUTPUT_CSV_FILE}")

except IOError as e:
    print(f"Error writing to {OUTPUT_CSV_FILE}: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while writing the CSV: {e}")
    exit(1)

print("Script finished.")