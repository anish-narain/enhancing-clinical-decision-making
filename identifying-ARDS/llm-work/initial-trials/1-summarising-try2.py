import pandas as pd
from transformers import pipeline, AutoTokenizer

df = pd.read_csv('/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv')

# Replace NaN values with empty strings
df.fillna('', inplace=True)

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")

# Function to summarize text using the pipeline
def summarize_text(text, max_chunk_size=1024, summary_max_length=150, summary_min_length=30):
    tokenized_text = tokenizer.encode(text, truncation=False)
    chunks = [tokenized_text[i:i + max_chunk_size] for i in range(0, len(tokenized_text), max_chunk_size)]
    
    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        try:
            summary = summarizer(chunk_text, max_length=summary_max_length, min_length=summary_min_length, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            print(f"Error summarizing text: {chunk_text[:100]}...")  # Print a snippet of the text causing the issue
            print(e)
            summaries.append("")

    return ' '.join(summaries)

# Function to summarize text for a single hadm_id
def summarize_for_hadm_id(hadm_id, df):
    # Filter the dataframe for the specific hadm_id
    data = df[df['hadm_id'] == hadm_id]

    if data.empty:
        print(f"No data found for hadm_id: {hadm_id}")
        return

    discharge_text = data['discharge_text'].values[0]
    radiology_texts = data['radiology_texts'].str.replace('\|\|\|', ' ', regex=True).values[0]
    ecd_combined_reports = data['ecd_combined_reports'].str.replace('\|\|\|', ' ', regex=True).values[0]

    discharge_summary = summarize_text(discharge_text)
    radiology_summary = summarize_text(radiology_texts)
    ecd_summary = summarize_text(ecd_combined_reports)

    return {
        'discharge_summary': discharge_summary,
        'radiology_summary': radiology_summary,
        'ecd_summary': ecd_summary
    }

# Example hadm_id to summarize (replace with an actual hadm_id from your data)
example_hadm_id = df['hadm_id'].values[0]

# Summarize the text for the example hadm_id
summaries = summarize_for_hadm_id(example_hadm_id, df)

# Display the summaries
print(f"Summaries for hadm_id {example_hadm_id}:\n")
print("Discharge Summary:\n", summaries['discharge_summary'])
print("\nRadiology Summary:\n", summaries['radiology_summary'])
print("\nECD Summary:\n", summaries['ecd_summary'])
