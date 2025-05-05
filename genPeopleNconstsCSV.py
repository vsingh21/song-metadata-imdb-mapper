""" 
Maps names of people from the JSON file of Giitayan songs to unique IMDb IDs using the publicly-accessible TSV names file.
"""

import json
import csv

SONGS_JSON_FILE = "all_songs.json"
NAME_BASICS_TSV_FILE = "name.basics.tsv"
OUTPUT_CSV_FILE = "people_nconsts.csv"

# Load people names from JSON file.
print(f"Loading song data from {SONGS_JSON_FILE}...")
try:
    with open(SONGS_JSON_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f)
except FileNotFoundError:
    print(f"Error: Input file not found: {SONGS_JSON_FILE}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {SONGS_JSON_FILE}.")
    exit(1)
except Exception as e:
    print(f"Unexpected error loading {SONGS_JSON_FILE}: {e}")
    exit(1)

print("Extracting unique names from song data...")
people_set = set()
for song in songs:
    for person in song.get("people", []):
        name = person.strip().lower()
        if name:
            people_set.add(name)

print(f"Found {len(people_set)} unique names in song data.")

# Match names to IDs from the TSV names file.
print(f"Reading {NAME_BASICS_TSV_FILE} and mapping names to IDs...")
name_to_id = {}
try:
    with open(NAME_BASICS_TSV_FILE, "r", encoding="utf-8") as f:
        headers = f.readline().strip().split('\t')
        if "primaryName" not in headers or "nconst" not in headers:
            print(f"Error: Missing 'primaryName' or 'nconst' in TSV headers.")
            exit(1)

        processed_lines = 0
        matched_names = 0
        for line in f:
            processed_lines += 1
            fields = line.strip().split('\t')
            if len(fields) != len(headers):
                continue

            entry = dict(zip(headers, fields))
            name = entry.get("primaryName", "").strip().lower()
            if name in people_set:
                nconst = entry.get("nconst")
                if nconst and nconst != r'\N':
                    name_to_id[name] = nconst
                    matched_names += 1

            if processed_lines % 100000 == 0:
                print(f"  Processed {processed_lines} lines...")

except FileNotFoundError:
    print(f"Error: Input file not found: {NAME_BASICS_TSV_FILE}")
    exit(1)
except Exception as e:
    print(f"Unexpected error reading TSV: {e}")
    exit(1)

print(f"Processed {processed_lines} lines. Found IDs for {len(name_to_id)} names.")
unmatched_count = len(people_set) - len(name_to_id)
if unmatched_count > 0:
    print(f"Warning: {unmatched_count} names had no matching ID.")

# Write name-ID mappings to CSV file.
print(f"Writing results to {OUTPUT_CSV_FILE}...")
try:
    with open(OUTPUT_CSV_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["primaryName", "nconst"])
        for name, nconst in name_to_id.items():
            writer.writerow([name.title(), nconst])
    print(f"Successfully saved name-ID mappings to {OUTPUT_CSV_FILE}")
except IOError as e:
    print(f"Error writing to CSV: {e}")
    exit(1)
except Exception as e:
    print(f"Unexpected error writing CSV: {e}")
    exit(1)

print("Script finished.")
