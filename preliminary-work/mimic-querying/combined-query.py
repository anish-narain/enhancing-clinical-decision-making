"""
HOW TO RUN
python3 combined-query.py radiology 10000032-RR-15
python3 combined-query.py discharge 10000032-DS-22
"""

import csv
import sys

# NOTE: could come up with a better path structure to make this more easily reproducible
radiology_csv_path = "/Users/anishnarain/Documents/FYP-Files/MIMIC-IV/clinical-notes/note/radiology.csv"
radiology_csv_length = 2321355 # it was useful to hard code this for the progress bar, but make sure to use get_unique_row_count to get the actual number in case using an updated dataset
discharge_csv_path = "/Users/anishnarain/Documents/FYP-Files/MIMIC-IV/clinical-notes/note/discharge.csv"
discharge_csv_length = 331793

# Output text file for both types of queries
output_text_file = {
    'radiology': "text-files/radiology-text.txt",
    'discharge': "text-files/discharge-text.txt"
}

def get_unique_row_count(csv_file_path):
    unique_note_ids = set()
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            unique_note_ids.add(row['note_id'])
    return len(unique_note_ids)

def find_unique_note_types(csv_file_path, total_rows):
    unique_note_types = set()
    processed_rows = 0

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                unique_note_types.add(row['note_type'])

                # To display progress using print statements
                processed_rows += 1
                print(f"Processed {processed_rows}/{total_rows} rows...") if (total_rows == radiology_csv_length and processed_rows % 10000 == 0) or (total_rows == discharge_csv_length and processed_rows % 1000 == 0) else None


    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

    print(f"\nProcessed {processed_rows}/{total_rows} rows. Done.")
    return unique_note_types

def find_text_for_note_id(note_id, csv_file_path, note_type):
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
        write_text_to_file(note_id, text, note_type)

def write_text_to_file(note_id, text, note_type):
    with open(output_text_file[note_type], 'a', encoding='utf-8') as file:
        file.write(f"text entry for {note_id}: {text}\n")
    print(f"Text entry for {note_id} written to {output_text_file[note_type]}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python combined_query.py [radiology|discharge] [note_id]")
        sys.exit(1)

    query_type = sys.argv[1]
    note_id = sys.argv[2]

    if query_type not in ['radiology', 'discharge']:
        print("Invalid query type. Choose 'radiology' or 'discharge'.")
        sys.exit(1)

    if query_type == 'radiology':
        csv_path = radiology_csv_path
        total_rows = radiology_csv_length
    else:
        csv_path = discharge_csv_path
        total_rows = discharge_csv_length

    find_text_for_note_id(note_id, csv_path, query_type)

    """
    unique_note_types = find_unique_note_types(csv_path, total_rows)
    if unique_note_types is not None:
        print("Unique note types found: ", unique_note_types)
    """
    
