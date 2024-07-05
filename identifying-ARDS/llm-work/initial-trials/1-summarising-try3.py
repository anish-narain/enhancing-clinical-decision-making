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
    # Tokenize text and split into chunks
    tokenized_text = tokenizer.encode(text, truncation=False)
    chunks = [tokenized_text[i:i + max_chunk_size] for i in range(0, len(tokenized_text), max_chunk_size)]
    
    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        try:
            summary = summarizer(chunk_text, max_length=summary_max_length, min_length=summary_min_length, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            print(f"Error summarizing text chunk: {chunk_text[:100]}...")  # Print a snippet of the text causing the issue
            print(e)
            summaries.append("")  # Append empty string for error cases

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



'''
Output:
(base) anishnarain@192 llm-work % python3 1-summarising-try3.py 
2024-05-30 15:21:17.576786: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: SSE4.1 SSE4.2, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Token indices sequence length is longer than the specified maximum sequence length for this model (8081 > 1024). Running this sequence through the model will result in indexing errors
Token indices sequence length is longer than the specified maximum sequence length for this model (1026 > 1024). Running this sequence through the model will result in indexing errors

Error summarizing text chunk:  
Name:  ___                    Unit No:   ___
 
Admission Date:  ___              Discharge Date:  ...
index out of range in self

Error summarizing text chunk:  intact. Preserved sensation throughout. ___ 
strength throughout. Gait assessment deferred  
PSYCH:...
index out of range in self

Error summarizing text chunk: 
1. No hydronephrosis of the right kidney. Left kidney is 
surgically absent.

CXR ___: 
Lung volume...
index out of range in self

Error summarizing text chunk:                          **FINAL REPORT ___

   URINE CULTURE (Final ___:    NO GROWTH

DIRECT INFLU...
index out of range in self

Error summarizing text chunk:  Site: ENDOTRACHEAL
      Source: Endotracheal. 

   GRAM STAIN (Final ___: 
      >25 PMNs and <10 ...
index out of range in self

Error summarizing text chunk:  dialysis.  
Patient received antibiotic coverage for aspiration pneumonia. 
The patient was extubat...
index out of range in self

Error summarizing text chunk: thromycin *NF* 5 mg/g ___ TID 
Sarna Lotion 1 Appl TP QID:PRN pruritus  
Gabapentin 100 mg PO/NG TID...
index out of range in self

Error summarizing text chunk: CHEST RADIOGRAPH

INDICATION:  Sepsis, intubation, evaluation for interval change.

COMPARISON:  ___...
index out of range in self

Error summarizing text chunk:  worsening edema; 
nevertheless, a variety of causes including hemorrhage, pneumonia and
worsening d...
index out of range in self

Error summarizing text chunk:  size since prior examination.
No hemorrhage, significant mass effect, or large vascular territorial...
index out of range in self

Error summarizing text chunk:  Florid colonic diverticulosis without evidence of diverticulitis.

6.  Decrease in size of right ad...
index out of range in self

Error summarizing text chunk: atic
lesions with many of the previously noted foci obscured by the new lung
parenchymal opacities. ...
index out of range in self






Summaries for hadm_id 20015730:

Discharge Summary:
         You were admitted to hospital for treatment for Renal Cell Carcinoma . Your kidney function has since improved and your creatinine was 1.2 at discharge . You had necrosis (damage) to your fingertips from some of your medications .

Radiology Summary:
       The left kidney is surgically absent. The bipolar diameter of the right kidney is 9.8 cm. The urinary bladder is empty with a Foley catheter in situ . There is no evident pneumothorax. The patient has metastatic renal cell carcinoma .

ECD Summary:
  Atrial fibrillation with rapid ventricular response - premature ventricular contractions or aberrant ventricular conduction . Sinus rhythm with PACs Poor R wave progression - probable normal variant Lateral T wave changes are nonspecific . Borderline ECG with frequent multifocal PVCs .

'''