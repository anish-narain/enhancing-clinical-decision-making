import pandas as pd
import time
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

# Load your data
df = pd.read_csv('/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv')
df.fillna('', inplace=True)

# Define model parameters
model_name = "llama3"
chunk_size_val = 4096
chunk_overlap_val = 100

# Define the structured PromptTemplate for checking pneumonia
prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible.\n"
        "Task: Determine if the patient had pneumonia.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
    ),
    input_variables=["discharge_text"]
)

# Function to split text into chunks
def chunk_text(text, chunk_size, overlap):
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Function to check for pneumonia in discharge text
def check_for_pneumonia(discharge_text, llm):
    # Chunk the discharge text
    chunks = chunk_text(discharge_text, chunk_size_val, chunk_overlap_val)
    
    # Process each chunk
    results = []
    for chunk in chunks:
        prompt = prompt_template.format(discharge_text=chunk)
        
        try:
            response = llm.invoke(prompt)
            results.append(response.strip())
        except Exception as e:
            results.append(f"Error invoking model: {e}")

    # Aggregate results 
    pneumonia_mentions = [res for res in results if "Yes" in res]
    if pneumonia_mentions:
        return "Yes", pneumonia_mentions[0]  # Return the first mention explaining why
    else:
        return "No", results[0] if results else "No sufficient data"

# Instantiate the model once
llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

# Define output file
output_file = '6-mult-llama3-text2.txt'

# Store processing time
processing_time = []

# Process the first 15 patient IDs
for i in range(min(15, len(df))):
    example_hadm_id = df['hadm_id'].values[i]

    start_time = time.time()

    data = df[df['hadm_id'] == example_hadm_id]
    if data.empty:
        result = f"No data found for hadm_id: {example_hadm_id}"
    else:
        discharge_text = data['discharge_text'].values[0]
        pneumonia_result, explanation = check_for_pneumonia(discharge_text, llm)

        end_time = time.time()

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(elapsed_time, 60)

        # Store time in seconds for that patient
        processing_time.append(elapsed_time)

        # Create the result string
        result = (
            f"\nPATIENT NUMBER {i}\n"
            f"\nInformation for hadm_id {example_hadm_id}:\n"
            f"\nDoes the patient have pneumonia?: {pneumonia_result}"
            f"\nExplanation: {explanation}"
            f"\nModel Info: {model_name}, chunk_size={chunk_size_val}, chunk_overlap={chunk_overlap_val}"
            f"\nTime taken: {int(minutes):02d} min and {int(seconds):02d} secs"
            f"\nCumulative time: {processing_time}"
        )

    # Write the result to the text file
    with open(output_file, 'a') as file:
        file.write(result + '\n')
