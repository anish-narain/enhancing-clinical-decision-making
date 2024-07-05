import pandas as pd
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

def create_prompt_template(task):
    return PromptTemplate(
        template=(
            f"Context: You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible.\n"
            f"Task: Determine if the patient suffered from {task}.\n"
            f"Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
            f"Text:\n{{text}}\n\n"
            f"Query: Does the chunk of text mention that the patient suffered from {task}? Answer strictly in 'Yes' or 'No'."
        ),
        input_variables=["text"]
    )

def chunk_text(text, chunk_size, overlap):
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def check_for_condition(text, llm, prompt_template, chunk_size, chunk_overlap):
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    results = []
    for chunk in chunks:
        prompt = prompt_template.format(text=chunk)
        try:
            response = llm.invoke(prompt)
            results.append(response.strip())
        except Exception as e:
            results.append(f"Error invoking model: {e}")
    condition_mentions = [res for res in results if "Yes" in res]
    if condition_mentions:
        return "Yes", condition_mentions[0], len(text)
    else:
        return "No", results[0] if results else "No sufficient data", len(text)

def process_patients(df, start_index, num_patients, llm, prompt_template_cardiac, prompt_template_discharge, chunk_size, chunk_overlap, output_csv_file, progress_report_file):
    processing_time = []
    with open(output_csv_file, 'a', newline='') as csvfile, open(progress_report_file, 'a') as report_file:
        fieldnames = ['hadm_id', 'text_length', 'cardiac_failure_detected', 'time_taken']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        for i in range(start_index, start_index + num_patients):
            current_hadm_id = df['hadm_id'].values[i]
            start_time = time.time()
            data = df[df['hadm_id'] == current_hadm_id]
            if data.empty:
                result = f"No data found for hadm_id: {current_hadm_id}"
            else:
                ecd_combined_reports = data['ecd_combined_reports'].values[0]
                cardiac_failure_result, explanation, ecd_combined_reports_length = check_for_condition(ecd_combined_reports, llm, prompt_template_cardiac, chunk_size, chunk_overlap)
                
                if cardiac_failure_result == "No":
                    discharge_text = data['discharge_text'].values[0]
                    cardiac_failure_result, explanation, discharge_text_length = check_for_condition(discharge_text, llm, prompt_template_discharge, chunk_size, chunk_overlap)
                    
                end_time = time.time()
                elapsed_time = end_time - start_time
                processing_time.append(elapsed_time)
                
                writer.writerow({
                    'hadm_id': current_hadm_id,
                    'text_length': max(ecd_combined_reports_length, len(discharge_text)),
                    'cardiac_failure_detected': cardiac_failure_result,
                    'time_taken': round(elapsed_time)
                })
                csvfile.flush()
                
                report_file.write(f"Patient Number: {i}, HADM ID: {current_hadm_id}, Text Length: {max(ecd_combined_reports_length, len(discharge_text))}, Cardiac Failure Detected: {cardiac_failure_result}, Time Taken: {round(elapsed_time)}\n")
                report_file.flush()

def main(file_path, model_name, chunk_size, chunk_overlap, output_csv_file, progress_report_file, num_patients):
    df = load_data(file_path)
    start_index = select_random_start(len(df))
    prompt_template_cardiac = create_prompt_template("cardiac failure")
    prompt_template_discharge = create_prompt_template("cardiac failure")
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    process_patients(df, start_index, num_patients, llm, prompt_template_cardiac, prompt_template_discharge, chunk_size, chunk_overlap, output_csv_file, progress_report_file)

if __name__ == "__main__":
    main(
        file_path='/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv',
        model_name="llama3",
        chunk_size=4096,
        chunk_overlap=100,
        output_csv_file='cardiac_failure-trial.csv',
        progress_report_file='cardiac_failure-trial.txt',
        num_patients = 15
    )
