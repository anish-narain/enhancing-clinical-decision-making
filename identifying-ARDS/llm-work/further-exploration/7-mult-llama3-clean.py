import pandas as pd
import time
import random
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
        return "Yes", pneumonia_mentions[0]
    else:
        return "No", results[0] if results else "No sufficient data"

def process_patients(df, start_index, num_patients, llm, prompt_template, chunk_size, chunk_overlap, output_file):
    processing_time = []
    for i in range(start_index, start_index + num_patients):
        current_hadm_id = df['hadm_id'].values[i]
        start_time = time.time()
        data = df[df['hadm_id'] == current_hadm_id]
        if data.empty:
            result = f"No data found for hadm_id: {current_hadm_id}"
        else:
            discharge_text = data['discharge_text'].values[0]
            pneumonia_result, explanation = check_for_pneumonia(discharge_text, llm, prompt_template, chunk_size, chunk_overlap)
            end_time = time.time()
            elapsed_time = end_time - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            processing_time.append(elapsed_time)
            result = (
                f"\nPATIENT NUMBER {i - start_index + 1}\n"
                f"\nInformation for hadm_id {current_hadm_id}:\n"
                f"\nDoes the patient have pneumonia?: {pneumonia_result}"
                f"\nExplanation: {explanation}"
                f"\nModel Info: {llm.model}, chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
                f"\nTime taken: {int(minutes):02d} min and {int(seconds):02d} secs"
                f"\nCumulative time: {processing_time}"
            )
        with open(output_file, 'a') as file:
            file.write(result + '\n')

def main(file_path, model_name, chunk_size, chunk_overlap, output_file, num_patients=15):
    df = load_data(file_path)
    #start_index = select_random_start(len(df))
    start_index = 0
    prompt_template = create_prompt_template()
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    process_patients(df, start_index, num_patients, llm, prompt_template, chunk_size, chunk_overlap, output_file)

if __name__ == "__main__":
    main(
        file_path='/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv',
        model_name="llama3",
        chunk_size=4096,
        chunk_overlap=100,
        output_file='7-mult-llama3-text1-clean.txt'
    )
