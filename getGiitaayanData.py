"""
Fetches song metadata files from a specified GitHub repository, parses them
to extract relevant information like film title, year, and associated people
(actors, singers, composers, lyricists), and compiles this data into a
structured JSON file.

This script iterates through a predefined range of file IDs, constructs the URL
for each file, retrieves the content, uses regular expressions to extract
specific fields, processes the extracted data, and saves the aggregated results.
"""

import os           # Used for potential future file system operations (though not currently used).
import re           # Regular expression operations, core for parsing the text files.
import json         # Used for encoding the final data structure into JSON format.
import requests     # Used for making HTTP requests to fetch files from the web.

# --- Configuration ---
# Range of file IDs to process. Assumes files are named sequentially (e.g., 1.isb.txt, 2.isb.txt).
FILE_IDS = range(1, 3501)
# Base URL for the raw content of the song metadata files in the GitHub repository.
BASE_URL = "https://raw.githubusercontent.com/v9y/giit/master/docs/"
# Output file path for the aggregated JSON data.
OUTPUT_JSON_FILE = "all_songs.json"

# --- Helper Functions ---

def extract_field(pattern, text):
    """
    Searches the text for a given regex pattern and extracts the first captured group.

    Args:
        pattern (str): The regular expression pattern with one capturing group.
                       The pattern should target the desired data within the text.
        text (str): The input string to search within.

    Returns:
        str or None: The stripped text of the first captured group if a match is found,
                     otherwise None.
    """
    match = re.search(pattern, text)
    # Return the captured group, stripping leading/trailing whitespace, if a match exists.
    return match.group(1).strip() if match else None

def extract_people_field(field, text):
    """
    Extracts a comma-separated list of names associated with a specific field tag.

    This function constructs a regex pattern based on the field name (e.g., '\\starring{...}%')
    and uses `extract_field` to get the raw comma-separated string. It then splits
    this string into a list of names.

    Args:
        field (str): The name of the field tag (e.g., 'starring', 'singer', 'music', 'lyrics').
        text (str): The input string containing the tagged data.

    Returns:
        list[str]: A list of names extracted from the specified field. Returns an empty
                   list if the field tag is not found or contains no names.
    """
    # Construct the regex pattern dynamically based on the field name.
    # Example: r"\\starring\{(.+?)\}%"
    # It looks for \{field_name}{content}% and captures the 'content'.
    # The '?' makes the '+' quantifier non-greedy.
    pattern = fr"\\{field}\{{(.+?)\}}%"
    raw_names_string = extract_field(pattern, text)

    # If no string was extracted, return an empty list.
    if not raw_names_string:
        return []

    # Split the raw string by commas and strip whitespace from each resulting name.
    return [name.strip() for name in raw_names_string.split(',')]

# --- Main Processing Logic ---

# List to hold the dictionaries, where each dictionary represents a song's data.
all_songs_data = []
# Set containing field names expected to contain lists of people.
PEOPLE_FIELDS = {'starring', 'singer', 'music', 'lyrics'}

print("Starting data fetching and parsing...")

# Loop through each file ID in the specified range.
for i in FILE_IDS:
    # Construct the full URL for the current file.
    file_url = f"{BASE_URL}{i}.isb.txt"

    try:
        # Attempt to fetch the file content from the URL.
        response = requests.get(file_url, timeout=10) # Added timeout for robustness
        # Raise an exception if the HTTP request returned an error status (e.g., 404 Not Found).
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle potential errors during the request (network issues, timeouts, bad status codes).
        print(f"Failed to fetch {file_url}. Error: {e}")
        continue # Skip to the next file ID if fetching fails.

    # Get the text content of the response.
    text_content = response.text

    # --- Data Extraction ---
    # Extract the film title using the specific regex pattern.
    film_title = extract_field(r"\\film\{(.+?)\}%", text_content)

    # Extract the year.
    year_str = extract_field(r"\\year\{(.+?)\}%", text_content)
    year_int = None # Default to None if year is not found or invalid.
    if year_str and year_str.isdigit():
        # Convert to integer only if it's a valid string of digits.
        year_int = int(year_str)
    elif year_str:
        # Log if year is found but is not purely digits.
        print(f"Warning: Non-digit year found for ID {i}: '{year_str}'")


    # --- People Extraction ---
    # Use a set to automatically handle duplicate names across different fields.
    people_set = set()
    # Iterate through the predefined fields that contain people's names.
    for field_name in PEOPLE_FIELDS:
        # Extract names for the current field and add them to the set.
        # The update method adds all elements from the returned list to the set.
        people_set.update(extract_people_field(field_name, text_content))

    # --- Structuring Data ---
    # Create a dictionary to store the extracted data for the current song.
    song_data = {
        "id": i,                      # The original file ID.
        "film": film_title,           # Extracted film title (can be None).
        "year": year_int,             # Extracted year as integer (can be None).
        "people": sorted(list(people_set)) # Convert the set of people to a sorted list.
    }

    # Add the processed song data to the main list.
    all_songs_data.append(song_data)
    # Provide progress feedback.
    # print(f"Parsed: {i}")
    # print(all_songs_data[-1]) # Uncomment for detailed debugging during processing

print(f"Finished processing {len(all_songs_data)} files.")

# --- Saving Data ---
print(f"Saving all collected data to {OUTPUT_JSON_FILE}...")
try:
    # Open the output file in write mode with UTF-8 encoding.
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        # Dump the list of song data dictionaries into the file as JSON.
        # indent=2 makes the JSON file human-readable.
        # ensure_ascii=False allows non-ASCII characters (like names) to be written directly.
        json.dump(all_songs_data, f, indent=2, ensure_ascii=False)
    print("Successfully saved data.")
except IOError as e:
    # Handle potential errors during file writing.
    print(f"Error saving data to {OUTPUT_JSON_FILE}: {e}")
except Exception as e:
    # Catch any other unexpected errors during JSON serialization or file handling.
    print(f"An unexpected error occurred during saving: {e}")

print("Script finished.")