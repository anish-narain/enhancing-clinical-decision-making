import pandas as pd
import re
import time
import random
import csv  
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

def load_data(file_path):
    df = pd.read_csv(file_path)
    df.fillna('', inplace=True)
    return df

def select_random_start(num_rows, min_rows=15):
    if num_rows < min_rows:
        raise ValueError(f"The dataset must contain at least {min_rows} rows to process.")
    return random.randint(0, num_rows - min_rows)

def create_prompt_template():
    return PromptTemplate(
        template=(
            "Context: You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible.\n"
            "Task: Determine if the patient had pneumonia.\n"
            "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
            "Discharge Text:\n{discharge_text}\n\n"
            "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
        ),
        input_variables=["discharge_text"]
    )

def preprocess_text_moderate(text):
    # Remove redundant underscores (e.g., "___")
    text = re.sub(r'___+', '_', text)

    # Replace multiple spaces with a single space
    text = re.sub(r' {2,}', ' ', text)

    # Replace multiple newlines with a single newline
    text = re.sub(r'\n{3,}', '\n\n', text)  # Keep double newlines for section separation
    text = re.sub(r'\n{2}', '\n', text)  # Replace any double newlines with a single newline
    
    # Strip leading and trailing spaces
    text = text.strip()
    
    return text

def preprocess_text_severe(text):
    # Remove multiple spaces and replace with a single space
    text = re.sub(r'\s+', ' ', text)

    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    
    # Remove unnecessary punctuation (e.g., "___")
    text = re.sub(r'___+', '', text)
    
    # Strip leading and trailing spaces
    text = text.strip()

    return text
    
def chunk_text(text, chunk_size, overlap):
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def check_for_pneumonia(discharge_text, llm, prompt_template, chunk_size, chunk_overlap):
    chunks = chunk_text(discharge_text, chunk_size, chunk_overlap)
    results = []
    for chunk in chunks:
        prompt = prompt_template.format(discharge_text=chunk)
        try:
            response = llm.invoke(prompt)
            results.append(response.strip())
        except Exception as e:
            results.append(f"Error invoking model: {e}")
    pneumonia_mentions = [res for res in results if "Yes" in res]
    if pneumonia_mentions:
        return "Yes", pneumonia_mentions[0], len(discharge_text) # Return pneumonia result, explanation, and length of discharge_text
    else:
        return "No", results[0] if results else "No sufficient data", len(discharge_text) # Return pneumonia result, explanation, and length of discharge_text

def process_patients(df, start_index, num_patients, llm, prompt_template, chunk_size, chunk_overlap, output_csv_file, progress_report_file):
    processing_time = []
    with open(output_csv_file, 'a', newline='') as csvfile, open(progress_report_file, 'a') as report_file:
        # Open the CSV file for writing
        fieldnames = ['hadm_id', 'discharge_text_length', 'pneumonia_detected', 'time_taken']
        # Define the column names
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Only write header if the file is empty
        if csvfile.tell() == 0:
            writer.writeheader()  # Write the header row
        
        for i in range(start_index, start_index + num_patients):
            current_hadm_id = df['hadm_id'].values[i]
            start_time = time.time()
            data = df[df['hadm_id'] == current_hadm_id]
            if data.empty:
                result = f"No data found for hadm_id: {current_hadm_id}"
            else:
                discharge_text = data['discharge_text'].values[0]
                processed_text = preprocess_text_severe(discharge_text)
                pneumonia_result, explanation, discharge_text_length = check_for_pneumonia(processed_text, llm, prompt_template, chunk_size, chunk_overlap)
                end_time = time.time()
                elapsed_time = end_time - start_time
                minutes, seconds = divmod(elapsed_time, 60)
                processing_time.append(elapsed_time)
                # Write data to CSV file
                writer.writerow({
                    'hadm_id': current_hadm_id,
                    'discharge_text_length': discharge_text_length,
                    'pneumonia_detected': pneumonia_result,
                    'time_taken': round(elapsed_time)
                })
                csvfile.flush()  # Flush the buffer to ensure data is written
                
                # Write data to progress report file
                report_file.write(f"Patient Number: {i}, HADM ID: {current_hadm_id}, Discharge Text Length: {discharge_text_length}, Pneumonia Detected: {pneumonia_result}, Time Taken: {round(elapsed_time)}\n")
                report_file.flush()  # Flush the buffer to ensure data is written

def main(file_path, model_name, chunk_size, chunk_overlap, output_csv_file, progress_report_file, num_patients):
    df = load_data(file_path)
    #start_index = select_random_start(len(df))
    start_index = 0
    prompt_template = create_prompt_template()
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    process_patients(df, start_index, num_patients, llm, prompt_template, chunk_size, chunk_overlap, output_csv_file, progress_report_file)

if __name__ == "__main__":
    main(
        file_path='/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv',
        model_name="llama3",
        chunk_size=4096,
        chunk_overlap=100,
        output_csv_file='speed-trial-1.csv',  # Change the output file name to a CSV file
        progress_report_file='speed_progress_report.txt',  # Path to the progress report file
        num_patients = 15
    )
