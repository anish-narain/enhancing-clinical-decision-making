import pandas as pd
from transformers import LlamaTokenizer

def count_tokens(text):
    # Load the tokenizer
    tokenizer = LlamaTokenizer.from_pretrained('huggingface/llama-3b')

    # Tokenize the text
    tokens = tokenizer.tokenize(text)
    
    # Count the number of tokens
    token_count = len(tokens)
    
    return token_count

# Load your data
df = pd.read_csv('/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv')
df.fillna('', inplace=True)

# Define your example_hadm_id
example_hadm_id = df['hadm_id'].values[0]


# Filter data
data = df[df['hadm_id'] == example_hadm_id]
if data.empty:
    print(f"No data found for hadm_id: {example_hadm_id}")
else:
    discharge_text = data['discharge_text'].values[0]
    token_count = count_tokens(discharge_text)
    print(f"Number of tokens: {token_count}")
