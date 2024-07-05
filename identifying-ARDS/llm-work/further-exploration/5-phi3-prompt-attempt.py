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
model_name = "phi3:mini"
chunk_size_val = 2048
chunk_overlap_val = 100

# Define the structured PromptTemplate for checking pneumonia
template = """
        <|system|>
        {system_prompt}<|endoftext|>
        <|user|>
        {user_prompt}<|endoftext|>
        <|assistant|>
        """

prompt_template = PromptTemplate(
    input_variables=["system_prompt", "user_prompt"],
    template=template
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
def check_for_pneumonia(discharge_text):
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    
    system_prompt = "You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible."
    user_prompt_template = (
        "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
    )

    # Chunk the discharge text
    chunks = chunk_text(discharge_text, chunk_size_val, chunk_overlap_val)
    
    # Process each chunk
    results = []
    for chunk in chunks:
        user_prompt = user_prompt_template.format(discharge_text=chunk)
        prompt = prompt_template.format(system_prompt=system_prompt, user_prompt=user_prompt)
        
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

# Example hadm_id to check for pneumonia
example_hadm_id = df['hadm_id'].values[0]

# Measure the time taken to check for pneumonia for the example hadm_id
start_time = time.time()

data = df[df['hadm_id'] == example_hadm_id]
if data.empty:
    print(f"No data found for hadm_id: {example_hadm_id}")
else:
    discharge_text = data['discharge_text'].values[0]
    pneumonia_result, explanation = check_for_pneumonia(discharge_text)

    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    # Display the result and time taken
    print(f"\nInformation for hadm_id {example_hadm_id}:\n")
    print(f"\nDoes the patient have pneumonia?: {pneumonia_result}")
    print(f"\nExplanation: {explanation}")
    print(f"\nModel Info: {model_name}, chunk_size={chunk_size_val}, chunk_overlap={chunk_overlap_val}")
    print(f"Time taken: {int(minutes):02d} min and {int(seconds):02d} secs")

