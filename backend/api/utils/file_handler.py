import os
import csv

def extract_csv_headers(file_path):
    """Extracts the header row from a CSV file."""
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return next(reader, [])  # Get the first row as header

def get_file_size(file_path):
    """Returns file size in MB."""
    return round(os.path.getsize(file_path) / (1024 * 1024), 2)
