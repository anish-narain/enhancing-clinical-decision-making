import pandas as pd
import time
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load your data
df = pd.read_csv('/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv')
df.fillna('', inplace=True)

# Define model
model_name = "stablelm-zephyr:3b"
chunk_size_val = 1024
chunk_overlap_val = 0

# Function to summarize text using LangChain and Ollama
def summarize_text_ollama(text):
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    chain = load_summarize_chain(llm, chain_type="stuff")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size_val, chunk_overlap=chunk_overlap_val)
    docs = text_splitter.create_documents([text])
    
    result = chain.invoke(docs)
    return result['output_text']

# Function to summarize text for a single hadm_id
def summarize_for_hadm_id(hadm_id, df):
    data = df[df['hadm_id'] == hadm_id]

    if data.empty:
        print(f"No data found for hadm_id: {hadm_id}")
        return

    discharge_text = data['discharge_text'].values[0]
    radiology_texts = data['radiology_texts'].str.replace('\|\|\|', ' ', regex=True).values[0]
    ecd_combined_reports = data['ecd_combined_reports'].str.replace('\|\|\|', ' ', regex=True).values[0]

    discharge_summary = summarize_text_ollama(discharge_text)
    radiology_summary = summarize_text_ollama(radiology_texts)
    ecd_summary = summarize_text_ollama(ecd_combined_reports)

    return {
        'discharge_summary': discharge_summary,
        'radiology_summary': radiology_summary,
        'ecd_summary': ecd_summary
    }

# Example hadm_id to summarize
example_hadm_id = df['hadm_id'].values[0]

# Measure the time taken to summarize the text for the example hadm_id
start_time = time.time()
summaries = summarize_for_hadm_id(example_hadm_id, df)
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
minutes, seconds = divmod(elapsed_time, 60)

# Display the summaries and time taken
print(f"\nSummaries for hadm_id {example_hadm_id}:\n")
print("Discharge Summary:\n", summaries['discharge_summary'])
print("\nRadiology Summary:\n", summaries['radiology_summary'])
print("\nECD Summary:\n", summaries['ecd_summary'])

print(f"\nModel Info: {model_name}, chunk_size={chunk_size_val}, chunk_overlap={chunk_overlap_val}")
print(f"Summarisation time: {int(minutes):02d} min and {int(seconds):02d} secs")
