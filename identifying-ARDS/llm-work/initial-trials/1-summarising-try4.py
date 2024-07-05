import pandas as pd
from transformers import pipeline, AutoTokenizer

df = pd.read_csv('/Users/anishnarain/Documents/FYP-Files/git/identifying-ARDS/data-preprocessing/csv-files/ards-cohort-notes.csv')

# Replace NaN values with empty strings
df.fillna('', inplace=True)

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")

# Function to summarize text using the pipeline
def summarize_text(text, max_chunk_size=512, summary_max_length=150, summary_min_length=30):
    # Tokenize text and split into chunks
    tokenized_text = tokenizer.encode(text, truncation=False)
    chunks = [tokenized_text[i:i + max_chunk_size] for i in range(0, len(tokenized_text), max_chunk_size)]
    
    summaries = []
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        try:
            if len(chunk) <= 1024:
                summary = summarizer(chunk_text, max_length=summary_max_length, min_length=summary_min_length, do_sample=False)[0]['summary_text']
                summaries.append(summary)
            else:
                print(f"Chunk size exceeds limit: {len(chunk)} tokens")
                summaries.append("")  # Skip chunks that are too large
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
2024-05-30 15:13:48.150141: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: SSE4.1 SSE4.2, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Token indices sequence length is longer than the specified maximum sequence length for this model (8081 > 1024). Running this sequence through the model will result in indexing errors
Your max_length is set to 150, but your input_length is only 92. Since this is a summarization task, where outputs shorter than the input are typically wanted, you might consider decreasing max_length manually, e.g. summarizer('...', max_length=46)
Summaries for hadm_id 20015730:

Discharge Summary:
  Mr.    is a boy with met renal cell carc admitted on   2 weeks of high dose  therapy . He has been on prophylactic cipro throughout his stay . Vancomycin was started empirically  the setting of  severe dermatitis, and he has been  on pro-phyactic cripro . His Tmax during his stay has been 99.5 on  with no elevated temps .  The patient has a history of kidney cancer, but his mother had ovarian cancer, no obvious signs of lymphoma, who is now healthy . He has been diagnosed with anemia with folate deficiency, anemia, cysticria, migraines, sputum production, dysuria, urinary frequency, urinary urgency, focal  numbness, focal .numbness and focal weakness are symptoms .  The distal  and adjacent soft tissues  are  within normal limits on the images presented . No previous images. No evidence of calcification or ischemia, infection, or inflammation. Nasogastric tube just passed the gastroesophageal junction .  The left atrium is elongated. The left ventricular wall thickness, cavity size, and global systolic function are normal . The ascending aorta is mildly dilated. There is no aortic valve stenosis. The mitral valve appears structurally normal with trivial mitral regurgitation. id colonic diverticulosis without evidence of diverticulitis .  The left kidney is  purposefullysurgically absent . No hydronephrosis of the right kidney . A more focal opacity at the left lung base  would be better evaluated after hemodynamic status is optimized .  No evidence of DVT or DVT in either lower extremity . Bronchial lavage, right mid lobe:  NEGATIVE FOR MALIGNANT CELLS. No viral inclusions noted . Diffuse infiltrative pulmonary abnormality more pronounced .  The final report was published at the end of the week . The report was compiled by Stool.com . It is the first time the report has been published in the public .  Pneumocystis jirovecii (carinii) is a low yield procedure based on our low yield results from pulmonary Histoplasmosis, Coccidioidomycosis, Aspergillosis or Mucormycosis is strongly suspected . If you have any other medical concerns, please call Virology at the University of Manchester Virology (GMT) within 1 week if additional testing is needed .  The patient was transferred from floor to ICU on dopamine  and neo; dopamine was converted to levophed . Initial central venous O2 saturation  was 91% . Pulsus was normal  at 5.5; Echocardiogram as above was largely unremarkable . Blood cultures eventually grew out of MRSA, with subsequent cultures negative until  vancomycin-resistant Enterococcus .  MRSA/VRE bacteremia: S/p line removals; Patient completed 15-day course of linezolid . Antibiotics were d/c'd on ___ and  patient has been stable, afebrile without leukocytosis since . Anemia: likely multifactorial due to poor nutrition, acute acute nutrition, and marrow suppression .  Atrial fibrillation with rapid ventricular response- Occurred  at morning of ___. Became more hypotensive, received two attempts at DC cardioversion, transient sinus rhythm restored,  then converted back into a fib . Amiodarone load and drip was  started, converted to sinus . Cardiac enzymes were flat, lower extremity ultrasound negative for DVT . Patient likely had  induced renal injury, with possible ischemic acute tubular necrosis . He was not continued on his anti-hypertensives as SBPs were 130-140 .  Patient developed significant skin breakdown, particularly on his fingertips . Lumbar puncture was  purposefullydeferred given intracranial mass . Patient can have formal neurocognitive outpatient work-up if deemed necessary by his PCP .  Lipitor 20mg; Folic Acid 1 mg Tablet Sig: One (1) Tablet PO DAILY (Daily) Pantoprazole 40 mg Tablet, Delayed Release (E.C.) Sig:  One  Tablet PO Q24H (every 24 hours) as needed for nausea/vomiting, insomnia or anxiety . Diphenhydramine HCl 25 mg Capsule Sig: ___ Capsules PO Q6H (every 6 hours) As needed for pruritis . White Petrolatum-Mineral Oil    Topical QID (4 times a day) as necessary for dry skin .  Hydroxyzine HCl 25 mg Tablet Sig: One (1) Tablet PO Q6H (every 6 hours) as needed for pruritis . Fentanyl 25 mcg/hr Patch 72 hr Sig: Remove previous  patch before applying. Do not drive while using this.  50 17 gram/dose Powder Sig: One (1) Tablet, Delayed Release (E.C.) PO DAILY (Daily) as needed for constipation . ZOFRAN ODT 8 mg Tablet, Rapid Dissolve Sig: 1 Tablet, Rapid Dissolve PO every eight (8) hours as necessary for nausea .  You also had skin damage to your sacrum (above your buttocks)  from the ___.  The ___ services should help you change these dressings . Plastic surgery saw you and your finger  stabilize your finger .

Radiology Summary:
  The heart is moderately enlarged and the heart is stable . A nasogastric tube is shown following a normal course and terminating in the distal stomach . There is no evidence of pneumoperitoneum and the bowel gas shadow appears unremarkable .  The diagnosis includes drug reaction, infectious etiology, and scattered atelectasis . The patient was diagnosed with renal cell carcinoma post IL-2 therapy . The prognosis is not significantly changed since six hours prior .  A man with renal cell carcinoma metastatic  to the lung with persistent hypotension . A focal opacity in the left lower lobe is unchanged and likely represents atelectasis or pneumonia . Recommend repeating imaging after Diuresis for further evaluation .  The ventricles and cortical sulci are normal in size and configuration . Gray-white matter differentiation is preserved . The intracranial arterial flow voids are patent . There are minimal mucosal thickening involving both maxillary sinuses . There is no evidence of restricted diffusion to suggest acute or prior hemorrhage .  The left peroneal vein is not well visualized secondary to the underlying edema, but the remaining remaining veins are normal without evidence of DVT . The ventricles and sulci are normal in caliber and configuration . The patient is status post left-left cancerous Renal cell carcinoma, now SBO versus.us .  The liver, spleen, gallbladder, and pancreas are unremarkable . Small bowel dilation without a clear transition point to suggest obstruction . A 7 cm segment of small bowel wall thickening may represent ischemia, infection, or inflammation . There is no free air, free fluid, or pathologic lymphadenopathy .  Renal cell carcinoma with recent treatment of IL-2 with persistent need for pressors . Florid colonic diverticulosis without evidence of diverticulaitis . Decrease in size of right adrenal nodule suggestive of response to therapy .  There has been placement of a right central venous catheter with its tip terminating in the distal SVC . Sub 2-cm right adrenal mass is stable . No significant interval change to some of the previously noted metastatic nodules .  The findings are concerning for small-bowel obstruction . No significant air is visualized within the large bowel . The right subclavian line tip is at the level of cavoatrial junction . There is also evidence of volume overload given the volume overload .  There is no acute hemorrhage, mass effect, or large vascular territorial infarct . No acute intracranial hemorrhage or mass effect . Mild opacification is seen in the bilateral sphenoid sinuses and new from prior .  The left kidney is surgically absent . The bipolar diameter of the right kidney is 9.8 cm. A cortical cyst is seen at the lower pole of the . right kidney . The urinary bladder is empty with a Foley catheter in situ .  The tip of the line projects over the upper SVC . There is no evidence of complication, particularly no pneumothorax . The retrocardiac opacity could have increased in the interval .

ECD Summary:
  Atrial fibrillation with rapid ventricular response - premature ventricular contractions or aberrant ventricular conduction . Sinus rhythm with PACs Poor R wave progression - probable normal variant Lateral T wave changes are nonspecific . Borderline ECG with frequent multifocal PVCs .

'''