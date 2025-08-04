import os
import logging
import csv
from typing import Dict

KNOWN_PROGRAM_IDS: Dict[str, str] = {}

def load_program_ids_from_csv(file_path: str):
    global KNOWN_PROGRAM_IDS
    KNOWN_PROGRAM_IDS = {}
    total_rows = 0
    filtered_count = 0
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        raise FileNotFoundError(f"Program IDs CSV file not found or is empty: {file_path}")
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total_rows += 1
            if 'program_address' in row and 'project_name' in row:
                # Filter out entries with empty or whitespace-only names
                program_address = row['program_address'].strip()
                project_name = row['project_name'].strip()
                if program_address and project_name:
                    KNOWN_PROGRAM_IDS[program_address] = project_name
                else:
                    filtered_count += 1
    logging.info(f"Loaded {len(KNOWN_PROGRAM_IDS)} known programs from {total_rows} total entries ({filtered_count} filtered out)")

# Load program IDs at startup
try:
    # Get the path relative to this module's location
    module_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(module_dir)
    csv_path = os.path.join(project_root, 'data', 'program_ids.csv')
    load_program_ids_from_csv(csv_path)
except FileNotFoundError as e:
    logging.error(f"Failed to load program IDs: {e}")
    # Depending on criticality, you might want to exit or use a fallback
    # For now, we'll let it proceed with an empty dict if the file is missing/empty
except Exception as e:
    logging.error(f"An unexpected error occurred while loading program IDs: {e}")

if __name__ == "__main__":
    print(KNOWN_PROGRAM_IDS)
