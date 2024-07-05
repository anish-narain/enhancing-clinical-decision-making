# LLM for producing ARDS Labels

## Initial Updates

From [`initial-exploration.md`](https://github.com/anish-narain/final-year-project/blob/main/identifying-ARDS/llm-work/initial-exploration.md), the following changes were made:

**#1** For most of the investigations, the prompt template being followed was 

```
pneumonia_prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician reviewing a discharge summary from clinical notes for patients in an ICU.\n"
        "Task: Determine if the patient had pneumonia.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the patient have pneumonia? Answer strictly in 'Yes' or 'No'. Give a sentence explaining why:"
    ),
    input_variables=["discharge_text"]
)
```

This was changed to reflect [documentation](https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3) about llama3's prompt format.

```
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

system_prompt = "You are a clinician reviewing clinical notes for patients in an ICU."
    user_prompt_template = (
        "Query: Check if there is any mention of pneumonia in the text. If so, does the text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
        "Discharge Text:\n{discharge_text}\n\n"
    )
```

**#2** Chunking was properly implemented.

```
 # Chunk the discharge text
    chunks = chunk_text(discharge_text, chunk_size_val, chunk_overlap_val)
    
    # Process each chunk
    results = []
    for chunk in chunks:
        user_prompt = user_prompt_template.format(discharge_text=chunk)
        prompt = prompt_template.format(system_prompt=system_prompt, user_prompt=user_prompt)
```


### `4-prompt-attempt.py`

Note the code was designed to only return the first explanation for a "Yes" in the final output.

**Trial 1**

Model Info: llama3, chunk_size=4000, chunk_overlap=100
Time taken: 01 min and 19 secs
```
PROMPT
system_prompt = "You are a clinician reviewing clinical notes for patients in an ICU."
user_prompt_template = (
    "Check if there is any mention of pneumonia in the text.\n"
    "Discharge Text:\n{discharge_text}\n\n"
    "Query: Does the text mention pneumonia? Answer strictly in 'Yes' or 'No'. Give a sentence explaining why:"
)
```

```
LLM REASONING
No.

The text does not mention pneumonia anywhere, so there is no mention of it in the discharge notes.Yes.

The text mentions pneumonia in point 4, which states "Bibasilar consolidative opacity concerning for pneumonia".Yes.

The text mentions pneumonia because it states that "Diffuse infiltrative pulmonary abnormality, more pronounced in the perihilar right lung has progressed could by virtue of asymmetry be pneumonia rather than pulmonary edema..."No.
There is no mention of pneumonia in the provided clinical notes.Yes.

The patient received antibiotic coverage for aspiration pneumonia.No.
The text does not mention pneumonia at all, as there is no relevant diagnosis, treatment, or condition described that would suggest the presence of pneumonia.No.

The text does not mention pneumonia. There is no reference to pneumonia, its symptoms, or any related medical issues. The discharge instructions focus on medication changes and wound care for the patient's skin damage.
```

```
FINAL OUTPUT
Information for hadm_id 20015730:

Does the patient have pneumonia?: Yes

Explanation: Yes.

The text mentions pneumonia in point 4, which states "Bibasilar consolidative opacity concerning for pneumonia".
```

**Trial 2**

Model Info: llama3, chunk_size=1024, chunk_overlap=256
Time taken: 04 min and 10 secs

Prompt changed:
```
PROMPT
system_prompt = "You are a clinician reviewing clinical notes for patients in an ICU."
user_prompt_template = (
    "Query: Check if there is any mention of pneumonia in the text. If so, does the text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
    "Discharge Text:\n{discharge_text}\n\n"
)
```

```
LLM REASONING
NoYesYes, there is mention of pneumonia in the text. The answer suggests that the patient has pneumonia: Yes.NoNoYesNoNoNoYes, there is a mention of pneumonia in the text. However, it does not suggest that the patient has pneumonia.YesYes, there is mention of pneumonia in the text.NoNo, there is no mention of pneumonia in the text.YesNo, there is no mention of pneumonia in the text.YesNoNoNoYesNoNoYesYesNoNoNoNo.NoNoNoNo
```

```
FINAL OUTPUT
Information for hadm_id 20015730:


Does the patient have pneumonia?: Yes

Explanation: Yes

```


**Trial 3**

Model Info: llama3, chunk_size=4096, chunk_overlap=100
Time taken: 03 min and 36 secs

```
PROMPT
(same as Trial 3)
```

```
LLM REASONING
YesYes, there is mention of pneumonia in the text.

The text suggests that the patient has pneumonia: "A more focal opacity at the left lung base laterally would be better evaluated after hemodynamic status is optimized. It could be a small region of infection or infarction, pleural effusion, or transient atelectasis."Yes, the text suggests that the patient has pneumonia. The CXR report mentions "Diffuse infiltrative pulmonary abnormality, more pronounced on the perihilar right lung has progressed could by virtue of asymmetry be pneumonia rather than pulmonary edema..."YesNoNoNo
```

```
FINAL OUTPUT
Information for hadm_id 20015730:


Does the patient have pneumonia?: Yes

Explanation: Yes
```

At this point of these experiments I have realised some things. Firstly, there are many variables that can be changed within my prompt code:
* Model being used
* Template being used for the model: whether it is the model-specific one found in the "template" section of the Ollama model card page for the model, or just a simple generic one that I was using for all the models in initial exploration
* Prompt itself: there are variations in speed for what you are asking. Are you asking to just see if the text chunk has the key word pneumonia? Are you asking it to tell you whether the text suggests that the patient actually has pneumonia (requires reasoning so might take longer)?
* How many prompts: right now I have only tried one-shot prompting. Maybe doing two shot, with the first being NLP and then the second being the check for whether the patient actually has it?
* Chunk sizes and chunk overlap: typically have an impact on speed rather than accuracy

This brings me to some investigations I could do:
1. Investigate the effect of prompt template on model correctness and speed: Check model-specific prompt template `5-{model_name}-prompt-attempt.py` vs `5-generic-template.py` for that model.
2. Investigate how the llm performs for multiple patient ids: Does its performance (in terms of latency) change over time? Do I need to implement asynchonous llm calls?
3. Investigate effect of prompts on models: This is pretty open-ended because you can then start looking at different prompts, different models and different chunk sizes and chunk overlap for those models. To limit the scope of the search space I will need to stick to one model, stuck to one chunk size and chunk overlap, and then experiment with different prompts.
4. Investigate few shot prompting

Ideas I could also implement:
1. Early stopping: if it sees a "Yes" for pneumonia even once it stops the chunking process and moves on to the next hadm_id.
2. Do some NLP on the code first, that way you get rid of all the text that isn't relevant (from removing stop words, to just extracting sentences that contain the word pneumonia).
3. If things are taking way too long, I could just opt for buying gpt-4 by the tokens and see if that is any faster. 

## Investigating Prompt Template

Llama 3, Model Info: llama3, chunk_size=4096, chunk_overlap=100
```
5-llama3-prompt-attempt.py 
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

system_prompt = "You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible."
user_prompt_template = (
    "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
    "Discharge Text:\n{discharge_text}\n\n"
)
```

```
5-generic-template.py 
prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible.\n"
        "Task: Determine if the patient had pneumonia.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'.'"
    ),
    input_variables=["discharge_text"]
)
```
| Trial | Output | Time Taken |
| --------------- | --------------- | --------------- |
| 5-llama3-prompt-attempt.py, Trial 1 | NoNoYesNoNoNoNo | 02 min and 46 secs |
| 5-llama3-prompt-attempt.py, Trial 2 | YesNoYesNoNoNoNo | 02 min and 41 secs |
| 5-llama3-prompt-attempt.py, Trial 3 | NoNoYesNoNoNoNo | 02 min and 43 secs |
| 5-generic-template.py, Trial 1 | NoYesYesNoNoNo.No | 02 min and 51 secs |
| 5-generic-template.py, Trial 2 | NoYesYesNoNoNoNo | 02 min and 41 secs |
| 5-generic-template.py, Trial 3 | NoYesYesNoNoNoNo. | 02 min and 38 secs |

**CONCLUSION: template type does not seem to have a big impact on output or time taken. Generic template was a bit more consistent with outputs, model-specific template was a bit more consistent with timing.**

Looking at the other (more lightweight) models, it was found that they were not responding as well to the prompts. They were not sticking to the Yes/No outputs and reasoning was more speculative rather than based on exact sentences. For example, we can look at llama2's results.

```
5-llama2-prompt-attempt.py
template = """
        [INST] <<SYS>>{system_prompt}<</SYS>>
        {user_prompt} [/INST]
        """

prompt_template = PromptTemplate(
    input_variables=["system_prompt", "user_prompt"],
    template=template
)
```

```
5-generic-template.py
prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible.\n"
        "Task: Determine if the patient had pneumonia.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'.'"
    ),
    input_variables=["discharge_text"]
)

system_prompt = "You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible."
user_prompt_template = (
    "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
    "Discharge Text:\n{discharge_text}\n\n"
)
```

**5-generic-template.py, llama2, chunk_size=4096, chunk_overlap=100, Time taken: 05 min and 04 secs**
```
LLM REASONING

Yes. The text suggests that the patient has pneumonia. The patient's symptoms, such as hypotension, fever, and altered mental status, are consistent with pneumonia. Additionally, the lab results show an elevated white blood cell count and a low albumin level, which are also indicative of pneumonia.NoYes. The text suggests that the patient may have pneumonia based on the following findings:

1. Diffuse infiltrative pulmonary abnormality more pronounced in the perihilar right lung, which could be due to pneumonia rather than pulmonary edema.
2. Moderate right pleural effusion is stable, which can be a sign of pneumonia.
3. The presence of bilateral multifocal parenchymal opacities, which are also indicative of pneumonia.

While the text does not explicitly mention the word "pneumonia," the findings mentioned above are consistent with this diagnosis.Based on the provided text, I would answer "No" to whether the patient had pneumonia. There is no mention of pneumonia in the text. The patient's respiratory symptoms are described as "aspiration pneumonia," but this does not necessarily mean they have pneumonia. Aspiration refers to the entry of food, liquids, or other foreign substances into the lungs through the nose or mouth, which can lead to inflammation and infection. The text does not provide enough information to determine if the patient had pneumonia specifically.Yes. The text suggests that the patient may have pneumonia. The phrases "ARF: mediated ARF most likely, however prerenal or postrenal etiology also possible" and "kidney injury" suggest that the patient's renal function was affected by a pulmonary infection. Additionally, the mention of "continuous ___ hemodialysis" and "repeated TTE showed no right heart strain" suggests that the patient had severe respiratory failure and required dialysis treatment.Yes. The text suggests that the patient may have pneumonia. There is a mention of "pneumonia" in the discharge diagnosis and conditions section, and also in the medication changes section where it is mentioned that the patient was treated with antibiotics for MRSA and VRE.No. The chunk of text does not provide enough information to suggest that the patient has pneumonia. There is no mention of symptoms such as cough, fever, or difficulty breathing that are commonly associated with pneumonia. Additionally, there is no mention of any diagnostic tests or results that could indicate the presence of pneumonia. Therefore, I answer with a strict 'No' to your query.
```

```
FINAL OUTPUT
Does the patient have pneumonia?: Yes

Explanation: Yes. The text suggests that the patient has pneumonia. The patient's symptoms, such as hypotension, fever, and altered mental status, are consistent with pneumonia. Additionally, the lab results show an elevated white blood cell count and a low albumin level, which are also indicative of pneumonia.
```

**5-generic-template.py, llama2, chunk_size=7000, chunk_overlap=100, Time taken: 03 min and 26 secs**
```
LLM REASONING
No
Based on the text provided, I would answer "Yes" to whether the patient has pneumonia. The following are some reasons why:

1. The patient had a fever, which is a common symptom of pneumonia.
2. A Gram stain was performed on the patient's bronchial lavage, and it revealed the presence of polymorphonuclear leukocytes (PMNs), which are commonly seen in pneumonia.
3. The patient underwent a respiratory culture, which grew commensal respiratory flora, but no pathogenic bacteria were identified.
4. The patient had shock and hypotension, which could be related to sepsis caused by the pneumonia.

Overall, based on the symptoms and test results presented in the text, it seems likely that the patient has pneumonia.Yes. The text suggests that the patient has pneumonia based on the following reasons:

1. The patient was admitted with Atrial fibrillation with rapid ventricular response, which can be a sign of underlying cardiac disease.
2. The patient developed significant skin breakdown, particularly on their fingertips, which can be caused by pressors and immobility.
3. The patient had a CT head scan that showed slight improvement in metastatic disease, which can indicate that the patient has pneumonia.
4. The patient was started on antibiotics (Aldesleukin) for 5 days, which suggests that the medical team suspected or confirmed a bacterial infection.

Therefore, based on the information provided in the text, it can be concluded that the patient has pneumonia.Yes. The text mentions "pneumonia" explicitly in the following sentence:

"Disp:*60 Tablet(s)* Refills:*0* 12. Acetaminophen 650 mg Tablet Sig: One (1) Tablet PO every six (6) hours as needed for pain: do note take more than 4 grams per day."

This suggests that the patient is being treated for pneumonia with acetaminophen.
```

```
FINAL OUTPUT
Does the patient have pneumonia?: Yes

Explanation: Based on the text provided, I would answer "Yes" to whether the patient has pneumonia. The following are some reasons why:

1. The patient had a fever, which is a common symptom of pneumonia.
2. A Gram stain was performed on the patient's bronchial lavage, and it revealed the presence of polymorphonuclear leukocytes (PMNs), which are commonly seen in pneumonia.
3. The patient underwent a respiratory culture, which grew commensal respiratory flora, but no pathogenic bacteria were identified.
4. The patient had shock and hypotension, which could be related to sepsis caused by the pneumonia.

Overall, based on the symptoms and test results presented in the text, it seems likely that the patient has pneumonia.
```

**5-llama2-prompt-attempt.py, llama2, chunk_size=7000, chunk_overlap=100, Time taken: 09 min and 40 secs**
```
LLM REASONING
Patient: [Name], Age: [Age], Gender: [Gender]

Chief Complaint: Tachycardia, tachypnea, and shortness of breath

History of Present Illness: The patient was brought to the emergency department with a chief complaint of tachycardia, tachypnea, and shortness of breath. The patient had been experiencing these symptoms for the past few days, and they have been gradually worsening over time. The patient also reports feeling weak and fatigued.

Review of Systems: The patient's review of systems is normal except for the following abnormalities:

* Mucous membranes are dry
* Neck is supple, and there is no lymphadenopathy or thyromegaly
* Cardiac exam reveals a regular rhythm with tachycardia
* Lungs are clear bilaterally anteriorly, but there is a small pericardial effusion
* Abdominal exam reveals hypoalbuminemia and diffuse erythema on the skin
* There is a 2+ dorsalis pedis and posterior tibial pulse
* Extremities are diffuse and have erythema
* Neurological exam reveals A&Ox3, but the patient has difficulty with word finding
* CN is intact, and there is preserved sensation throughout
* Strength is intact throughout, but gait assessment is deferred

Pertinent Results:

* Blood tests reveal:
        + WBC count: 8.0 x 10^9/L
        + RBC count: 3.21 x 10^9/L (hemoglobin level: 9.5 g/dL)
        + HCT: 29.3%
        + MCV: 91 fL (mild anemia)
        + ALBUMIN: 3.4 g/dL (hypoalbuminemia)
        + CALCIUM: 8.1 mg/dL
        + POTASSIUM: 4.0 mg/dL
        + CHOLESTEROL: 250 mg/dL (mild hypercholesterolemia)
        + TRIGLYCERIDES: 150 mg/dL (mild hypertriglyceridemia)
        + Urea: 7.5 mg/dL (normal)
        + Creatinine: 1.2 mg/dL (normal)
* Urinalysis reveals no abnormalities
* Chest X-ray shows cardiomegaly and pleural effusion
* ECG shows ST segment depression in leads II, III, and aVf, as well as T wave inversion in lead I
* ECHO reveals:
        + Left atrial size: 45 mm (normal)
        + Left ventricular size: 40 mm (mild hypertrophy)
        + Right ventricular size: 30 mm (normal)
        + Pulmonary artery pressure: 30 mmHg (normal)
        + Mitral valve apparatus: normal
        + Aortic root: 25 mm (normal)
* Renal ultrasound reveals no abnormalities

Diagnosis: The patient's symptoms and lab results suggest the following diagnoses:

1. Heart failure: The patient's tachycardia, tachypnea, and shortness of breath are consistent with heart failure. The ECG changes also support this diagnosis.
2. Anemia: The patient's mild anemia and hypoalbuminemia suggest a possible cause of their symptoms.
3. Hypoalbuminemia: The patient's hypoalbuminemia may be related to liver disease or malnutrition.
4. Cardiomegaly: The patient's cardiomegaly on chest X-ray suggests that they have a dilated heart, which is consistent with heart failure.
5. Pleural effusion: The patient's pleural effusion on chest X-ray may be related to their heart failure or another underlying condition.
6. Hypertriglyceridemia: The patient's mild hypertriglyceridemia may contribute to their symptoms.
7. Hypocholesteremia: The patient's mild hypocholesteremia may contribute to their symptoms.

Plan:

1. Start the patient on diuretics to reduce the pleural effusion and improve lung function.
2. Prescribe ACE inhibitors or ARBs to manage heart failure and reduce cardiac output.
3. Monitor the patient's potassium levels closely, as they may need to be adjusted with diuretic therapy.
4. Consider adding beta blockers if the patient's symptoms do not improve with ACE inhibitors or ARBs.
5. Refer the patient to a nephrologist for further evaluation and management of their hypoalbuminemia and hypertriglyceridemia.
6. Monitor the patient's liver function tests closely, as they may be related to their heart failure.
7. Consider referring the patient to a cardiothoracic surgeon if their symptoms do not improve with medical therapy and they have significant cardiac decompensation.
This is a comprehensive report of a patient's medical course, including various laboratory test results and treatments administered. Here are some key points from the report:

1. The patient was admitted to the hospital with fever, shock, and a central line infection.
2. Initially, broad-spectrum antibiotics were prescribed to cover potential bacterial sources, including Gram-positive and Gram-negative organisms.
3. Blood cultures grew MRSA, and subsequent cultures remained negative until the patient was weaned off pressors.
4. A right subclavian triple lumen was removed and replaced with a right internal jugular triple lumen.
5. The patient's pressures stabilized after linezolid replaced vancomycin for VRE bacteremia.
6. The patient's family requested continued aggressive treatment, and goals of care were discussed.
7. The report highlights the importance of proper infection control measures, including proper hand hygiene and use of personal protective equipment (PPE), to prevent the spread of multidrug-resistant bacteria like MRSA.
8. The report also underscores the need for timely and appropriate testing, such as direct influenza antigen testing and fungal culture, to inform treatment decisions and prevent potential complications.
9. The patient's clinical course illustrates the challenges of managing sepsis and multi-drug resistant organisms (MDROs) in a hospital setting, highlighting the importance of interdisciplinary collaboration and effective communication among healthcare providers.The patient was admitted to the hospital with a full code status. The reason for admission is not specified in the given text, but based on the medications listed, it appears that the patient may have been experiencing symptoms related to cancer treatment or other medical conditions.

The patient's medication list includes several medications that are commonly used in cancer treatment, including hydrocerin, hydrOXYzine, and ciprofloxacin. The patient is also receiving medications for pain management, such as morphine sulfate and phenylephrine. Additionally, the patient is receiving medications to manage symptoms related to cancer treatment, such as diphenhydramine and prochlorperazine.

The patient's home medications include several medications that are commonly used to manage cancer-related symptoms, including folic acid, vitamin C, and citrucel. The patient is also taking medications for high blood pressure, such as diltiazem and valsartan.

The discharge medications list includes several medications that the patient will continue to take after being discharged from the hospital, including lipitor, folic acid, and pantoprazole. The patient will also receive a injection of cyanocobalamin once a month.

It is important to note that this list of medications may not be exhaustive, as there may be other medications that the patient is taking that are not listed here. Additionally, the dosages and frequency of administration of these medications may vary based on the patient's individual needs and the recommendations of the patient's healthcare providers.Based on the information provided in the discharge text, there are several potential diagnoses and medications that can be identified:

1. Pneumonia: Yes, the patient has pneumonia, as indicated by the mention of bacteria in their blood and the need for antibiotics.
2. Constipation: Yes, the patient is at risk of constipation, as they have been prescribed senna and colace to prevent constipation, and bisacodyl if needed.
3. Renal failure: Yes, the patient has resolved acute renal failure, as indicated by their creatinine level of 1.2 at discharge.
4. Sepsis: No, the patient does not have sepsis, as there is no mention of this diagnosis in the discharge text.
5. Mental status changes: Yes, the patient had acute mental status changes, which resolved, as indicated by the discharge instructions to see a neurologist if their condition worsens.
6. Nausea and vomiting: Yes, the patient may experience nausea and vomiting, as they have been prescribed lorazepam for these symptoms.
7. Skin damage: Yes, the patient has skin damage to their sacrum (above their buttocks) from an unknown cause, as indicated by the discharge instructions to have plastic surgery services help them change dressings.
8. Dialysis: Yes, the patient had dialysis while in the hospital, as indicated by their creatinine level of 1.2 at discharge.
9. Confusion: Yes, the patient was confused during their hospital stay, as indicated by their intubation and need for neurocognitive evaluation.

Medications:

1. Lipitor: The patient should continue taking this medication at a dosage of 20mg per day.
2. Folate: The patient should continue taking this medication at a dosage of 1mg per day.
3. Protonix: The patient should continue taking this medication at a dosage of 40mg per day.
4. Vitamin C: The patient should continue taking this medication at a dosage of 1g per day.
5. Cyanocobalamin: The patient should continue taking this medication at a dosage of 1g per month.
6. Ferrous gluconate: The patient should continue taking this medication twice a day.
7. Fentanyl patch: The patient should continue taking this medication every 72 hours, as indicated by the discharge instructions.
8. Morphine: The patient should continue taking this medication as needed for pain, as indicated by the discharge instructions.
9. Senna and colace: The patient should take these medications every day to prevent constipation.
10. Miralax and bisacodyl: The patient should take these medications if they become constipated, as indicated by the discharge instructions.

It is important to note that this is a summary of potential diagnoses and medications based on the information provided in the discharge text, and a comprehensive assessment by a healthcare professional is necessary for an accurate diagnosis and treatment plan.

```

```
FINAL OUTPUT
Does the patient have pneumonia?: Yes

Explanation: Based on the information provided in the discharge text, there are several potential diagnoses and medications that can be identified:

1. Pneumonia: Yes, the patient has pneumonia, as indicated by the mention of bacteria in their blood and the need for antibiotics.
2. Constipation: Yes, the patient is at risk of constipation, as they have been prescribed senna and colace to prevent constipation, and bisacodyl if needed.
3. Renal failure: Yes, the patient has resolved acute renal failure, as indicated by their creatinine level of 1.2 at discharge.
4. Sepsis: No, the patient does not have sepsis, as there is no mention of this diagnosis in the discharge text.
5. Mental status changes: Yes, the patient had acute mental status changes, which resolved, as indicated by the discharge instructions to see a neurologist if their condition worsens.
6. Nausea and vomiting: Yes, the patient may experience nausea and vomiting, as they have been prescribed lorazepam for these symptoms.
7. Skin damage: Yes, the patient has skin damage to their sacrum (above their buttocks) from an unknown cause, as indicated by the discharge instructions to have plastic surgery services help them change dressings.
8. Dialysis: Yes, the patient had dialysis while in the hospital, as indicated by their creatinine level of 1.2 at discharge.
9. Confusion: Yes, the patient was confused during their hospital stay, as indicated by their intubation and need for neurocognitive evaluation.

Medications:

1. Lipitor: The patient should continue taking this medication at a dosage of 20mg per day.
2. Folate: The patient should continue taking this medication at a dosage of 1mg per day.
3. Protonix: The patient should continue taking this medication at a dosage of 40mg per day.
4. Vitamin C: The patient should continue taking this medication at a dosage of 1g per day.
5. Cyanocobalamin: The patient should continue taking this medication at a dosage of 1g per month.
6. Ferrous gluconate: The patient should continue taking this medication twice a day.
7. Fentanyl patch: The patient should continue taking this medication every 72 hours, as indicated by the discharge instructions.
8. Morphine: The patient should continue taking this medication as needed for pain, as indicated by the discharge instructions.
9. Senna and colace: The patient should take these medications every day to prevent constipation.
10. Miralax and bisacodyl: The patient should take these medications if they become constipated, as indicated by the discharge instructions.

It is important to note that this is a summary of potential diagnoses and medications based on the information provided in the discharge text, and a comprehensive assessment by a healthcare professional is necessary for an accurate diagnosis and treatment plan.
```

## Investigating Performance on Multiple Patient ID's

For now, llama3 with chunk_size=4096, chunk_overlap=100 is chosen for multiple patient ID's. The code is virtually the same except rather than doing 1 hadm_id it will now do 15. I will stick to the generic template because of its consistency in outputs. 

The results can be found in [`result.ipynb`](https://github.com/anish-narain/final-year-project/blob/main/identifying-ARDS/llm-work/results.ipynb).



## Other
**Templates**


```
LLM REASONING

```

```
FINAL OUTPUT

```
