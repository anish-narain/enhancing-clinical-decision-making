"""
HOW TO RUN
python3 query-radiology.py
"""

import csv
import random

radiology_csv_path = "/Users/anishnarain/Documents/FYP-Files/MIMIC-IV/clinical-notes/note/radiology.csv"
radiology_csv_length = 2321355 # number of rows
output_text_file = "text-files/radiology-text.txt"
multi_output_text_file = "text-files/radiology-text-multi.txt"

def get_unique_row_count(csv_file_path):
    unique_note_ids = set()
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            unique_note_ids.add(row['note_id'])
    return len(unique_note_ids)

def find_unique_note_types(csv_file_path):
    unique_note_types = set()

    # To display progress
    total_rows = radiology_csv_length
    processed_rows = 0

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                unique_note_types.add(row['note_type'])

                # To display progress using print statements
                processed_rows += 1
                if processed_rows % 1000 == 0:  # Update for every 1000 lines processed
                    print(f"Processed {processed_rows}/{total_rows} rows...")

    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

    print(f"\nProcessed {processed_rows}/{total_rows} rows. Done.")
    return unique_note_types

def find_text_for_note_id(note_id, csv_file_path):
    found = False
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['note_id'] == note_id:
                text = row['text']
                print(text)
                found = True
                break
    
    if not found:
        print("Note ID not found in the CSV file.")
    else:
        write_text_to_file(note_id, text)

def write_text_to_file(note_id, text):
    with open(output_text_file, 'a', encoding='utf-8') as file:
        file.write(f"text entry for {note_id}: {text}\n")
    print(f"Text entry for {note_id} written to {output_text_file}")

def find_note_ids_by_note_type(note_type, csv_file_path):
    note_ids = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['note_type'] == note_type:
                note_ids.append(row['note_id'])
    return note_ids

def get_random_note_ids(note_ids, num_samples=5):
    return random.sample(note_ids, min(num_samples, len(note_ids)))

def find_text_for_note_ids(note_ids, csv_file_path, output_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        notes_dict = {row['note_id']: row['text'] for row in reader}
    
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for note_id in note_ids:
            if note_id in notes_dict:
                text = notes_dict[note_id]
                output_file.write(f"text entry for {note_id}: {text}\n")
                print(f"Text entry for {note_id} written to {output_file_path}")
            else:
                print(f"Note ID {note_id} not found in the CSV file.")


# Usage example
if __name__ == "__main__":
    """
    # Finding different types of Notes in Radiology (should be AR and RR)
    unique_note_types = find_unique_note_types(radiology_csv_path)
    if unique_note_types is not None:
        print("Unique note types found: ", unique_note_types)
    """

    """
    # Prints and writes to text file the clinical notes for entry with provided note id
    note_id = input("Enter the note ID (example 10000032-RR-15): \n")
    find_text_for_note_id(note_id, radiology_csv_path)
    """

    # Returns some random note ids and writes to text file
    note_type = input("Enter the note type (RR or AR): ").upper()
    note_ids = get_random_note_ids(find_note_ids_by_note_type(note_type, radiology_csv_path))
    if note_ids:
        print(note_ids)
        find_text_for_note_ids(note_ids, radiology_csv_path, multi_output_text_file)
    else:
        print("No note IDs found for the specified note type.")

