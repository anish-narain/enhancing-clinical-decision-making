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

# Define models
model_names = ["stablelm-zephyr:3b", "llama3", "phi3:mini", "gemma", "mistral"]
chunk_size_val = 2048
chunk_overlap_val = 100

# Function to summarize text using LangChain and Ollama
def summarize_text_ollama(text, model_name):
    llm = Ollama(model=model_name, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    chain = load_summarize_chain(llm, chain_type="stuff")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size_val, chunk_overlap=chunk_overlap_val)
    docs = text_splitter.create_documents([text])
    
    result = chain.invoke(docs)
    return result['output_text']

# Function to summarize text for a single hadm_id
def summarize_for_hadm_id(hadm_id, df, model_name):
    data = df[df['hadm_id'] == hadm_id]

    if data.empty:
        with open('summary-results-trial3.txt', 'a') as f:
            f.write(f"No data found for hadm_id: {hadm_id}\n")
        return

    discharge_text = data['discharge_text'].values[0]
    radiology_texts = data['radiology_texts'].str.replace('\|\|\|', ' ', regex=True).values[0]
    ecd_combined_reports = data['ecd_combined_reports'].str.replace('\|\|\|', ' ', regex=True).values[0]

    discharge_summary = summarize_text_ollama(discharge_text, model_name)
    #radiology_summary = summarize_text_ollama(radiology_texts, model_name)
    #ecd_summary = summarize_text_ollama(ecd_combined_reports, model_name)

    return {
        'discharge_summary': discharge_summary,
        #'radiology_summary': radiology_summary,
        #'ecd_summary': ecd_summary
    }

# Example hadm_id to summarize
# example_hadm_id = df['hadm_id'].values[1]
example_hadm_id = 20050336

# Write the summaries and time taken to a file
with open('summary-results-trial3.txt', 'w') as f:
    for model_name in model_names:
        # Measure the time taken to summarize the text for the example hadm_id
        start_time = time.time()
        summaries = summarize_for_hadm_id(example_hadm_id, df, model_name)
        end_time = time.time()

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(elapsed_time, 60)

        f.write(f"\n{model_name} =============================================")
        f.write(f"\nSummaries for hadm_id {example_hadm_id} using model {model_name}:\n")
        f.write("Discharge Summary:\n" + summaries['discharge_summary'] + "\n")
        #f.write("\nRadiology Summary:\n" + summaries['radiology_summary'] + "\n")
        #f.write("\nECD Summary:\n" + summaries['ecd_summary'] + "\n")

        f.write(f"\nModel Info: {model_name}, chunk_size={chunk_size_val}, chunk_overlap={chunk_overlap_val}\n")
        f.write(f"Summarisation time: {int(minutes):02d} min and {int(seconds):02d} secs\n")
