"""
Fetches song metadata files from Giitaayan, extracts film info and names
(actors, singers, composers, lyricists), and compiles the data into a JSON file.
"""

import os
import re
import json
import requests

FILE_IDS = range(1, 3501)
BASE_URL = "https://raw.githubusercontent.com/v9y/giit/master/docs/"
OUTPUT_JSON_FILE = "all_songs.json"

def extract_field(pattern, text):
    # Extracts the first regex group match from text.
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None

def extract_people_field(field, text):
    # Extracts a list of names from a given metadata field.
    pattern = fr"\\{field}\{{(.+?)\}}%"
    raw_names_string = extract_field(pattern, text)
    if not raw_names_string:
        return []
    return [name.strip() for name in raw_names_string.split(',')]

all_songs_data = []
PEOPLE_FIELDS = {'starring', 'singer', 'music', 'lyrics'}

print("Starting data fetching and parsing...")

for i in FILE_IDS:
    file_url = f"{BASE_URL}{i}.isb.txt"

    # Fetches each song.
    try:
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {file_url}. Error: {e}")
        continue

    text_content = response.text

    # Extracts film information.
    film_title = extract_field(r"\\film\{(.+?)\}%", text_content)
    year_str = extract_field(r"\\year\{(.+?)\}%", text_content)
    year_int = int(year_str) if year_str and year_str.isdigit() else None

    if year_str and not year_str.isdigit():
        print(f"Warning: Non-digit year found for ID {i}: '{year_str}'")

    # Extracts people information.
    people_set = set()
    for field_name in PEOPLE_FIELDS:
        people_set.update(extract_people_field(field_name, text_content))

    # Structures collected info into a JSON format.
    song_data = {
        "id": i,
        "film": film_title,
        "year": year_int,
        "people": sorted(list(people_set))
    }

    all_songs_data.append(song_data)

print(f"Finished processing {len(all_songs_data)} files.")
print(f"Saving all collected data to {OUTPUT_JSON_FILE}...")

# Writes data to a JSON file.
try:
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_songs_data, f, indent=2, ensure_ascii=False)
    print("Successfully saved data.")
except IOError as e:
    print(f"Error saving data to {OUTPUT_JSON_FILE}: {e}")
except Exception as e:
    print(f"An unexpected error occurred during saving: {e}")

print("Script finished.")
