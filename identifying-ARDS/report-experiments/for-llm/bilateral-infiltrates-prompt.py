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

def create_prompt_template():
    return PromptTemplate(
        template=(
            "Context: You are a clinician receiving chunks of radiology reports for patients in an ICU. Please do the reviewing as quickly as possible.\n"
            "Task: Determine if the patient suffered from bilateral infiltrates.\n"
            "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
            "Discharge Text:\n{radiology_texts}\n\n"
            "Query: Does the chunk of text mention that the patient suffered from bilateral infiltrates? Answer strictly in 'Yes' or 'No'.  Then provide a reason for your response."
        ),
        input_variables=["radiology_texts"]
    )

def chunk_text(text, chunk_size, overlap):
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def check_for_bilateral_infiltrates(radiology_texts, llm, prompt_template, chunk_size, chunk_overlap):
    if not radiology_texts:  # Check if radiology_texts is empty or not
        return None, "No radiology text available", 0  # Return None if there is no radiology_texts entry

    chunks = chunk_text(radiology_texts, chunk_size, chunk_overlap)
    results = []
    for chunk in chunks:
        prompt = prompt_template.format(radiology_texts=chunk)
        try:
            response = llm.invoke(prompt)
            results.append(response.strip())
        except Exception as e:
            results.append(f"Error invoking model: {e}")
    explanation = results if results else "No sufficient data"
    return explanation, len(radiology_texts) # Return explanation and length of radiology_texts

def process_patients(df, start_index, num_patients, llm, prompt_template, chunk_size, chunk_overlap, output_csv_file, progress_report_file, model_name):
    processing_time = []
    with open(output_csv_file, 'a', newline='') as csvfile, open(progress_report_file, 'a') as report_file:
        fieldnames = ['model_name', 'hadm_id', 'radiology_texts_length', 'time_taken', 'explanation']
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
                radiology_texts = data['radiology_texts'].values[0] if 'radiology_texts' in data.columns else ''
                explanation, radiology_texts_length = check_for_bilateral_infiltrates(radiology_texts, llm, prompt_template, chunk_size, chunk_overlap)
                end_time = time.time()
                elapsed_time = end_time - start_time
                minutes, seconds = divmod(elapsed_time, 60)
                processing_time.append(elapsed_time)
                writer.writerow({
                    'model_name': model_name,
                    'hadm_id': current_hadm_id,
                    'radiology_texts_length': radiology_texts_length,
                    'time_taken': round(elapsed_time),
                    'explanation': explanation
                })
                csvfile.flush()
                
                report_file.write(f"Model: {model_name}, Patient Number: {i}, HADM ID: {current_hadm_id}, Radiology Text Length: {radiology_texts_length}, Time Taken: {round(elapsed_time)}, Explanation: {explanation}\n")
                report_file.flush()

def main(file_path, model_names, chunk_size, chunk_overlap, output_csv_file, progress_report_file, num_patients):
    df = load_data(file_path)
    start_index = 1949  # You can change this to select_random_start(len(df)) if you want a random start index
    prompt_template = create_prompt_template()
    for model_name in model_names:
        llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
        process_patients(df, start_index, num_patients, llm, prompt_template, chunk_size, chunk_overlap, output_csv_file, progress_report_file, model_name)

if __name__ == "__main__":
    model_names = ["stablelm-zephyr:3b", "llama3", "phi3:mini", "gemma", "mistral"]
    main(
        file_path='/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv',
        model_names=model_names,
        chunk_size=4096,
        chunk_overlap=100,
        output_csv_file='bi-model-output.csv',
        progress_report_file='bi-model-output.txt',
        num_patients=6
    )
