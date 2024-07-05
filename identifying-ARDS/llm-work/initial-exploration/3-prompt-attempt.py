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
chunk_size_val = 4000
chunk_overlap_val = 100

# Define the structured PromptTemplate for checking pneumonia
template = """
        <|begin_of_text|>
        <|start_header_id|>system<|end_header_id|>
        {system_prompt}
        <|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        {user_prompt}
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """

prompt_template = PromptTemplate(
    input_variables=["system_prompt", "user_prompt"],
    template=template
)

# Function to check for pneumonia in discharge text
def check_for_pneumonia(discharge_text):
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    
    system_prompt = "You are a clinician reviewing clinical notes for patients in an ICU."
    user_prompt = f"Check if there is any mention of pneumonia in the text.\nDischarge Text:\n{discharge_text}\n\nQuery: Does the text mention pneumonia? Answer strictly in 'Yes' or 'No'. Give a sentence explaining why:"
    
    prompt = prompt_template.format(system_prompt=system_prompt, user_prompt=user_prompt)
    
    try:
        response = llm.invoke(prompt)
        return response.strip()
    except Exception as e:
        return f"Error invoking model: {e}"

# Example hadm_id to check for pneumonia
example_hadm_id = df['hadm_id'].values[0]

# Measure the time taken to check for pneumonia for the example hadm_id
start_time = time.time()

data = df[df['hadm_id'] == example_hadm_id]
if data.empty:
    print(f"No data found for hadm_id: {example_hadm_id}")
else:
    discharge_text = data['discharge_text'].values[0]
    pneumonia_result = check_for_pneumonia(discharge_text)

    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    # Display the result and time taken
    print(f"\nInformation for hadm_id {example_hadm_id}:\n")
    print(f"\nDoes the patient have pneumonia?: {pneumonia_result}")
    print(f"\nModel Info: {model_name}, chunk_size={chunk_size_val}, chunk_overlap={chunk_overlap_val}")
    print(f"Time taken: {int(minutes):02d} min and {int(seconds):02d} secs")
