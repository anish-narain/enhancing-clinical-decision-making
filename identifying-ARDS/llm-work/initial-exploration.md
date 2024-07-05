# LLM for producing ARDS Labels

## Initial Summarising Attempt

**`ollama_summarising.py`**

| Model | Summarisation time |
| --------------- | --------------- |
| llama2, chunk_size=512, chunk_overlap=0  | 03 min and 32 secs |
| llama2, chunk_size=1024, chunk_overlap=0  | 03 min 47 secs |
| llama2, chunk_size=2048, chunk_overlap=0  | 05 min and 04 secs |
| phi3:mini, chunk_size=512, chunk_overlap=0  | 02 min and 41 secs |
| phi3:mini, chunk_size=1024, chunk_overlap=0  | 02 min and 33 secs |
| phi3:mini, chunk_size=2048, chunk_overlap=0  | 02 min and 18 secs |
| stablelm-zephyr:3b, chunk_size=512, chunk_overlap=0  | 02 min and 29 secs |
| stablelm-zephyr:3b, chunk_size=1024, chunk_overlap=0  | 01 min and 36 secs |
| stablelm-zephyr:3b, chunk_size=2048, chunk_overlap=0  | 01 min and 38 secs |


| Model | Summary |
| --------------- | --------------- |
| llama2, chunk_size=512, chunk_overlap=0  | Discharge Summary: Patient was admitted to the hospital for renal cell carcinoma treatment and developed complications such as bacteremia, urinary tract infection, acute mental status changes, peripheral necrosis of digits, and acute renal failure. The patient required dialysis and had a complicated hospital course. Medications were changed during the patient's stay, and discharge instructions include continuing some medications, stopping others, and starting new ones as needed for itching, nausea, vomiting, anxiety, constipation, and pain management. The patient was discharged home with service and follow-up appointments were scheduled with their primary care physician. Radiology Summary: The patient is a male with renal cell carcinoma who has been intubated for hypercapnea. A portable chest AP view was obtained for evaluation of possible aspiration pneumonia. The study shows no acute hemorrhage, edema, mass effect, or large vascular territorial infarct. Multiple supratentorial and periventricular white matter hypodense foci are seen, consistent with chronic microvascular disease. Atherosclerotic vascular calcification is present in the cavernous carotid segments on both sides. Mild opacification is seen in the bilateral sphenoid sinuses, and there is a new peripheral atelectasis in the mid-left lung field. The heart size is unchanged, and no pneumothorax is present. The patient's history of IL-2 therapy and hypotension is noted. The study shows no evidence of acute new infiltrate, but there is marked improvement of previously existing pulmonary congestion. The patient's left kidney is surgically absent, and a cortical cyst is seen at the lower pole of the right kidney, consistent with findings on CT scan. No hydronephrosis of the right kidney is noted. The study is compared to a previous examination performed 3 hours earlier, showing no evidence of pneumothorax. ECD Summary: The patient has an abnormal ECG with several features, including: 1. Sinus tachycardia with frequent multifocal PVCs (atrial arrhythmia) 2. Short PR interval 3. Possible septal infarct (age undetermined) 4. Low QRS voltages in limb leads 5. Atrial fibrillation with rapid ventricular response (premature ventricular contractions or aberrant ventricular conduction) 6. Probable anteroseptal infarct (age undetermined) 7. Inferior/lateral ST-T changes may be due to myocardial ischemia (partially due to rate/rhythm) 8. Generalized low QRS voltages. The report does not provide the patient's sex or age, but based on the ECG findings, it is likely that the patient has an underlying cardiac condition, such as coronary artery disease or myocardial infarction (heart attack). The patient may require further testing and evaluation to determine the cause of their symptoms and develop an appropriate treatment plan. |
| llama2, chunk_size=1024, chunk_overlap=0  | Discharge Summary: Patient was admitted to the hospital for renal cell carcinoma treatment and had a complicated course. They developed bacterial infections, acute renal failure, and peripheral necrosis of digits. They were intubated and had neurocognitive changes. They also had skin damage to their sacrum. Medications were changed during their stay, and they were discharged with instructions to continue some medications, stop others, and start new ones as needed. They should take Benadryl, hydroxyzine, camphor-methol, petrolatum-mineral oil, lorazepam, ferrous gluconate, and oral care products as needed. They were also instructed to take senna and colace every day to prevent constipation and take miralax and bisacodyl if they become constipated. They should notify their nurse at a specific phone number for any fever, chills, shortness of breath, or inability to take oral fluids. Follow-up instructions were provided. Radiology Summary: The patient is a male with a history of renal cell carcinoma who is currently intubated for hypercapnea. The chest AP portable view shows no acute hemorrhage, edema, mass effect, or large vascular territorial infarct. However, there are multiple supratentorial and periventricular white matter hypodense foci, consistent with chronic microvascular disease. Additionally, atherosclerotic vascular calcification is seen in the cavernous carotid segments on both sides. Mild opacification is noted in the bilateral sphenoid sinuses, and there is no evidence of acute intracranial hemorrhage or mass effect. The impression is that there is no acute intracranial hemorrhage or mass effect, but mild opacification in the sphenoid sinus is noted. The chest AP portable view compared to the previous examination shows a new central venous access line inserted over the left anterior jugular vein, with no evidence of complication, such as pneumothorax. The other monitoring and support devices are unchanged. The size of the cardiac silhouette and the bilateral multifocal parenchymal opacities are also unchanged. The patient's history includes renal cell carcinoma on IL-2 therapy and intubation for hypercapnea, and the impression is that there is no acute intracranial hemorrhage or mass effect, but mild opacification in the sphenoid sinus is noted. The patient's condition has stabilized compared to the previous examination. ECD Summary: The patient's ECG shows several abnormalities, including: Sinus tachycardia Left axis deviation Possible extensive infarct (age undetermined) Generalized low QRS voltages Abnormal ECG The report does not provide the patient's sex or age. The possible infarcts are located in different areas of the heart, including the anteroseptal and lateral regions. The T wave changes may be due to myocardial ischemia, either due to rate/rhythm or infarction. The QRS voltages are low in several leads, indicating possible conduction abnormalities. The ECG shows a sinus rhythm with frequent premature ventricular contractions (PVCs). The report concludes that the patient has an abnormal ECG, but does not provide a definitive diagnosis without additional information. |
| llama2, chunk_size=2048, chunk_overlap=0  | Discharge Summary: Patient was admitted to the hospital for renal cell carcinoma treatment and developed various complications during their stay. They required dialysis, antibiotics for MRSA and VRE, and were intubated in the ICU due to confusion. The patient also experienced necrosis to their fingertips and skin damage to their sacrum. Upon discharge, the patient is instructed to continue certain medications and stop others. They are also prescribed new medications for itching and constipation prevention, and are advised to follow-up with their primary care physician. Medications: Lipitor (20mg) Folate (1mg) Protonix (40mg) Vitamin C (1g) Cyanocobalamin (1g) Benadryl (as needed for itching) Hydroxyzine (as needed for itching) Camphor-methol (as needed for itching) Petrolatum-mineral oil (as needed for skin care) Lorazepam (as needed for nausea, vomiting, or anxiety) Ferrous gluconate (twice a day) Fentanyl patch (every 72 hours) Morphine (as needed for pain) Senna and colace (every day for constipation prevention) Miralax (if constipated) Bisacodyl (if constipated) Instructions: Continue taking Lipitor, folate, Protonix, vitamin C, cyanocobalamin, and Benadryl as instructed. Stop taking citrucel, diltiazem, triamterene/hydrochlorothiazide, and valsartan. Start taking hydroxyzine, camphor-methol, petrolatum-mineral oil, Lorazepam, ferrous gluconate, Fentanyl patch, morphine, senna, colace, Miralax, and bisacodyl as instructed. Notify the primary care physician for follow-up appointments. Follow-up with  RN for any concerns or issues. Radiology Summary: The patient is a 65-year-old male with a history of renal cell carcinoma who is currently intubated for hypercapnea. A chest AP portable view was performed to evaluate for possible aspiration pneumonia. The findings showed mild opacification in the sphenoid sinus, which is new compared to prior studies. There is no acute hemorrhage, edema, mass effect, or large vascular territorial infarct. The ventricles and sulci are prominent, consistent with volume loss. Multiple supratentorial and periventricular white matter hypodense foci reflect chronic microvascular disease. Atherosclerotic vascular calcification is present in the cavernous carotid segments on both sides. The examination was compared to a previous study performed 3 hours earlier, and there was no evidence of pneumothorax. A single AP portable view chest was also performed to evaluate for ureteral obstruction, and the findings showed no hydronephrosis of the right kidney, but a 1.5 cm x 1.5 cm x 1.5 cm cortical cyst is seen at the lower pole of the right kidney, consistent with findings on CT ___. The urinary bladder is empty with a Foley catheter in situ. Finally, a chest radiograph was performed to evaluate for pneumothorax, and no evidence of complication was found. The other monitoring and support devices are in unchanged position, and the size of the cardiac silhouette and the bilateral multifocal parenchymal opacities are also unchanged. In conclusion, the patient's condition has stabilized compared to prior studies, but there is evidence of volume overload given the large hila bilaterally and engorgement of the vessels. The findings suggest chronic microvascular disease and atherosclerotic vascular calcification in the cavernous carotid segments on both sides. No pneumothorax was found, but there is a new central venous access line inserted over the left anterior jugular vein. ECD Summary: The patient has an abnormal ECG reading, which suggests possible infarctions in the heart. The ECG shows low QRS voltages, irregular rhythm, and abnormal tracings. The report does not provide the patient's age or sex, but it mentions that the patient may have a septal or anterior infarct, as well as possible anteroseptal or lateral T wave changes due to myocardial ischemia. Additionally, there are multiple leads that are unsuitable for analysis, including V1. The report concludes that the patient has sinus tachycardia and may have a history of previous infarction. |
| phi3:mini, chunk_size=512, chunk_overlap=0  | Discharge Summary: Patient discharged home with service after staying hospitalized for renal cell carcinoma (RCC) treatment. Secondary complications included VRE/MRSA sepsis, UTI, acute renal failure, supracondylar fractures of digits (finger necrosis), and mental status changes. Discharged with medications: Lipitor, Folate, Protonix, Vitamin C, Cyanocobalamin. Stopped using Citrucel, Diltiazem, Triamterene/Hydrochlorothiazide, Valsartan. New prescriptions include Benadryl (as needed), Hydroxyzine (as needed), Camphor-Methol ointment (as needed), Lyrica (for nausea, vomiting or anxiety - caution driving/alcohol use). Continue with ferrous gluconate, Morphine for pain (caution driving/alcohol use), Senna, and Colace daily. Follow-up instructions: Call RN at discharge if fever, chills, shortness of breath or unable to take oral fluids occur. Neurocognitive evaluation recommended by Dr. ___. Plastic surgery consulted for fingertip necrosis repair and wound care services provided for sacral burn site. Radiology Summary: The chest CT shows severe worsening pulmonary abnormality, volume overload, and possible progression of underlying renal cell carcinoma metastasis. There is evidence of bilateral hila enlargement, mediastinal vessel engorgement, and a small right pleural effusion. The heart size remains normal. The patient has received intermittent intubation due to respiratory failure caused by renal cell carcinoma. Lung opacities are stable with no new pneumothorax or acute infiltrates, but there is a focal opacity at the left lung base requiring further evaluation after optimizing hemodynamic status. The heart size has increased since yesterday's imaging. A central venous access line was placed without complications, and monitoring devices remain unchanged. There are bilateral multifocal parenchymal opacities with a potential increase in retrocardiac opacity over time. ECD Summary: The provided ECG reports indicate a pattern of sinus tachycardia with multifocal premature ventricular contractions (PVCs) and rapid atrial fibrillation, suggesting possible septal or anteroseptal infarcts. There are consistent findings of generalized low QRS voltages across various leads, indicative of extensive myocardial ischemia or infarction. The presence of lateral T wave changes in some reports further supports this pattern. Notably, the reports lack patient demographic details (sex and age), which could be crucial for interpreting these findings in context. Abnormal ECG results also mention possible right axis deviation and a left atrial abnormality without specific demographics provided. These ECG patterns warrant further clinical evaluation to determine the extent of myocardial damage, potential infarctions, and appropriate management strategies for suspected coronary artery disease or cardiomyopathy. |
| phi3:mini, chunk_size=1024, chunk_overlap=0  | Discharge Summary: Patient admitted with metastatic renal cell carcinoma undergoing therapy. Complications included VRE/MRSA sepsis and acute kidney injury, which have since resolved. Medications were adjusted during hospitalization; continue Lipitor, Folate, Protonix, Vit C, cyanocobalamin (starting from day 1); stop Citrucel, Diltiazem, Triamterene/Hydrochlorothiazide, and Valsartan. Initiate Benadryl, hydroxyzine, camphor-methol as needed for itching; Lorazepam (caution driving and alcohol consumption); oral care products; Tylenol for pain; ferrous gluconate twice daily; Fentanyl patch every 72 hours (no operating vehicles or drinking while on this medication). Continue senna, colace, Miralax, Bisacodyl as needed. Notify RN at hospital if experiencing fever, chills, shortness of breath, or inability to take oral fluids. Follow-up instructions pending further consultation with renal doctor and neurocognitive evaluation. Radiology Summary: The patient, a male with renal cell carcinoma on IL-2 therapy and intubated for hypoxic respiratory failure, presents with progressive worsening of underlying pulmonary abnormalities and possible volume overload as evidenced by large hila bilaterally and engorgement of vessels. Chest CT reveals severe infiltrative changes stabilizing from a previous progression. Heart size remains normal. Mediastinal vasculature shows mild engorgement, with potential small right pleural effusion noted on ET tube placement. The patient is also showing new mental status changes and vomiting, indicating possible metastatic disease or complications from the cancer therapy. Despite a recent CT comparison demonstrating clearing of previously present pulmonary congestion, bilateral supratentorial white matter hypodensities suggest chronic microvascular disease. Slight opacification in sphenoid sinuses and new findings may require further evaluation through MR imaging if contraindications are absent. The patient's condition necessitates close monitoring for signs of volume overload, respiratory compromise, and potential complications from intubation or cancer therapy. Repeat chest CT exams should be considered to track disease progression and response to treatment while evaluating the need for interventions such as managing pleural effusion and addressing metastatic disease concerns. ECD Summary: The provided abnormal electrocardiogram (ECG) reports consistently indicate sinus tachycardia or various irregularities such as atrial fibrillation with rapid ventricular response, potential infarcts (anterior and possibly old anteroseptal), intraventricular conduction defects, multifocal premature ventricular contractions (PVCs), low QRS voltages in multiple leads, and lateral T wave changes suggestive of myocardial ischemia. These ECG patterns are undetermined regarding patient sex or age but may point to significant cardiac issues requiring further investigation. |
| phi3:mini, chunk_size=2048, chunk_overlap=0  | Discharge Summary: Patient discharged home with services. Admitted for Renal Cell Carcinoma therapy; had VRE/MRSA sepsis, acute renal failure (resolved), SBO, peripheral necrosis of digits, and mental status changes (resolved). Discharge instructions include continued medications, discontinued drugs, new prescriptions for itching, nausea/vomiting, pain management, constipation prevention & relief. Follow up with RN if symptoms like fever, chills, shortness of breath or difficulty in taking fluids occur. Radiology Summary: Chest CT findings suggest worsening underlying pulmonary process, possibly related to renal cell carcinoma (RCC) metastasis and volume overload indicated by bilateral hila engorgement. The patient is intubated for hypoxic respiratory failure on IL-2 therapy with evidence of a small right pleural effusion. CT comparison demonstrates stabilized severe infiltrative abnormality, unchanged heart size, and mild vascular engorgement without new pneumothorax or acute changes. However, the presence of bilateral multifocal parenchymal opacities may indicate progression of underlying disease process and potential volume overload. A new central venous access line is in place with no evidence of complications. The patient's clinical status includes confusion and shortness of breath, requiring evaluation for possible aspiration pneumonia or metastatic disease/stroke. ECD Summary: The summary presents various abnormal findings from multiple electrocardiograms (ECGs), including sinus tachycardia, atrial fibrillation with rapid ventricular response, and possible myocardial infarcts of anteroseptal or inferior nature. Common patterns observed are left atrial abnormalities, right axis deviation, low QRS voltages in precordial leads, and generalized T wave changes indicating ischemia. Notably, the reports lack patient sex and age data. Some ECGs show borderline findings with short PR intervals and lateral ST-T changes potentially related to infarcts or myocardial ischemia. In a subset of cases, certain leads are unsuitable for analysis, indicating challenges in obtaining conclusive diagnostic information without patient demographics. |
|  stablelm-zephyr:3b, chunk_size=512, chunk_overlap=0 | Discharge Summary: The patient was admitted for renal cell carcinoma therapy and experienced several complications during their stay. They were treated for MRSA, VRE, and UTI; required dialysis; and had improvements in kidney function. The patient underwent hospitalization in the intensive care unit due to confusion and developed skin damage on their sacrum. Some medications were changed, including stopping citrucel, diltiazem, triamterene/hydrochlorothiazide, and valsand starting lorazepam, Benadryl, hydroxyzine, camphor-methol, petrolatum-mineral oil, oral care, and wound care products. The patient should continue taking lipitor, folate, protonix, vitamin C, and cyanocobalamin, while stopping citrucel, diltiazem, and valsand starting lorazepam use. Additional medications include senna and colace for constipation management, and the patient must notify a nurse if they experience fever, chills, shortness of breath, or inability to take oral fluids. The facility is instructed to follow up with the patient through "___." Radiology Summary: In this clinical impression, a patient with renal cell carcinoma (RCC) after interleukin (IL-2) therapy and hypertension undergoes various medical examinations. Findings of portable AP chest radiographs are described, showing diffuse gaseous dilation of small bowel loops and stomach, measuring up to 3.8 cm, while the large bowel appears relatively decompressed without significant air within it. These findings suggest a possible small-bowel obstruction. The patient's history includes RCC and hypoxic respiratory failure due to intubation. A comparison is made between a portable AP chest radiograph obtained at 6:32 A.M. and a chest CT from an unknown source. Both show the right subclavian line tip at the level of the cavoatrial junction, with stable cardiomaxillary silhouette; however, there's interval progression of multifocal parenchymal opacities potentially representing worsening of the underlying process on the chest CT as well as progression of infection. There's also evidence of volume overload given the large hila bilaterally and engorgement of the vessels. Another AP chest radiograph is described at 2:40 A.M., showing marked improvement in previously existing pulmonary congestion, with lower lung volumes, less pulmonary vasculature congestion, and no evidence of acute infiltrates. There's a focal opacity at the left lung base laterally that requires further evaluation due to potential complications such as small region of infection or infarction, pleural effusion, or transient atelectasis. The heart size is within normal limits, but increased since yesterday. In another case, comparison is made between an AP chest radiograph taken in a patient with metastatic RCC and findings on CT scan. The left kidney is surgically absent, with no hydronephrosis of the right kidney; however, there's a 1.5 cm x 1.5 cm x 1.5 cm cortical cyst at the lower pole of the right kidney, consistent with these findings on CT. Finally, an AP chest radiograph is compared to a prior study taken 3 hours earlier in a patient who underwent IL-2 therapy and hypotension due to renal cell carcinoma. Both images show extensive bilateral opacities stable, with no evident pneumothorax. A new central venous access line has been inserted over the left anterior jugular vein without any complications such as pneumothorax. In summary, this clinical impression highlights various diagnostic procedures and observations in patients with RCC and different accompanying medical conditions, emphasizing the importance of thorough examinations to accurately assess their condition. ECD Summary: This is about a summary of different possible heart conditions based on an ECG, or electrocardiogram. It talks about various types of heart rhythms and the chances of having certain issues like abnormal heartbeats, damaged heart tissue, or problems with how the heart works. The report also mentions some things that are hard to understand without knowing the person's age and gender. All these information helps doctors figure out what might be wrong with a person's heart.|
| stablelm-zephyr:3b, chunk_size=1024, chunk_overlap=0| Discharge Summary:The patient was admitted for renal cell carcinoma treatment and experienced various complications during their hospital course. They were treated with antibiotics for MRSA and VRE/MRSA sepsis, required dialysis, and were eventually discharged from the ICU. The patient should continue taking certain medications and follow discharge instructions regarding food choices, medications to stop taking, and new medications to start. Discharge instructions also include using oral care and wound care products, as well as following a schedule for fever, chills, shortness of breath, or inability to take oral fluids. They are instructed to notify a nurse named "___" in case of certain symptoms or issues. The patient should attend follow-up appointments as advised. A patient with metastatic renal cell carcinoma underwent AP chest radiographs and a comparison was made with previous studies. The findings showed improvement in lung volumes, less pulmonary congestion, and no new infiltrates. The heart size was stable but slightly increased. There was one focal opacity at the left lung base that needed further evaluation for possible infection, infarction, pleural effusion, or transient atelectasis. A comparison of AP chest radiographs taken 3 hours apart showed marked improvement in bilateral opacities and no evidence of pneumothorax.This is about a summary of different heart rhythms and possible issues they might have. It talks about sinustycardia, left atrial abnormalities, and other heartbeats like atrial fibrillation with rapid ventricular response. It also mentions various signs like short PR interval, inferior infarct, and lateral/anterior T wave changes that could be due to problems in the heart. The report doesn't know the person's age or sex but tries to explain these heart conditions and their possible causes. |
| stablelm-zephyr:3b, chunk_size=2048, chunk_overlap=0| Discharge Summary: You were admitted to the hospital for renal cell carcinoma treatment. While you were here, you developed infections (MRA and VRE), UTI with E.coli, and needed dialysis. Your kidney function has improved, and you should see a renal doctor if there are any further improvements. You were in the ICU and had some skin damage; plastic surgery helped improve your finger tips and skin around your sacrum. Your medications include: Lipitor 20mg Folate 1mg qday Protonix 40mg qday Vitamin C 1g qday Cyanocobalamin 1g sc monthly (Keep taking) Medications to stop: Citrucel 1g bid Diltiazem 240mg bid Triamterene/Hydrochlorothiazide 75/50mg qday (Start taking) Notify a nurse at ___ for fever, chills, shortness of breath, or inability to take oral fluids. Follow up instructions will be given after discharge. Radiology Summary: In this clinical impression, a patient with renal cell carcinoma (RCC) after interleukin therapy and hypertension is discussed. The patient experienced improvement in their pulmonary congestion after treatment, as seen on AP chest radiographs. In another case, a man with metastatic RCC had his kidney removed and no hydronephrosis was observed on the right kidney. Additionally, there are references to portable AP chest radiographs compared to chest CT and various time points throughout the day, focusing on changes in lung volumes, pulmonary vasculature, and possible indications for further evaluation or procedures like MR imaging. ECD Summary:This is a summary of various ECG findings including sinus tachycardia, left atrial abnormalities, right axis deviation, extensive infarcts, generalized low QRS voltages, and abnormal ECGs. It mentions different possible interpretations for lateral T wave changes, borderlines, and specific patterns like anteroseptal and inferior infarcts. The report is made without knowing the patient's sex or age. Leads unsuitable for analysis are also mentioned.|

## (Incorrect) Prompt attempts:

> After documenting the experiments from most of this section I realised don't even implement chunking  in the check_for_pneumonia() function so any mention of (chunk_size, chunk_overlap_val) can be ignored. Furthermore, it means the text being provided to the llama model was too big for its context size and made it difficult for it to do any processing.

**`1-prompt-attempt.py`**

This was not giving the straight yes or no response. It would instead extract certain parts of the text and provide that as its answer. 

```
pneumonia_prompt_template = PromptTemplate(
    template=(
        "You are a clinician looking through a discharge summary from clinical notes for patients in an ICU. "
        "Answer strictly in yes or no whether the summary suggests that the patient had pneumonia. "
        "If there is not enough information, just say 'No'.\n\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Answer:"
    ),
    input_variables=["discharge_text"]
)
```

Answers:

```
EXAMPLE 1
Does the patient have pneumonia?: 
Sig: One (1) Tablet, Delayed Release (E.C.) PO Q24H (every 24 hours).
4. Cyanocobalamin 1,000 mcg/mL Solution Sig: One (1) Injection once a month: next due ___.
5. Vitamin C 1,000 mg Tablet Sig: One (1) Tablet PO once a day.
6. Diphenhydramine HCl 25 mg Capsule Sig: ___ Capsules PO Q6H (every 6 hours) as needed for pruritis.
7. Lorazepam 0.5 mg Tablet Sig: ___ Tablets PO Q4H (every 4 hours) as needed for nausea/vomiting, insomnia or anxiety.
8. White Petrolatum-Mineral Oil Cream Sig: One (1) Appl Topical QID (4 times a day) as needed for dry skin.
9. Oral Wound Care Products Gel Sig: Fifteen (15) ML Mucous membrane TID (3 times a day) as needed for mucositis.
10. Hydroxyzine HCl 25 mg Tablet Sig: One (1) Tablet PO Q6H (every 6 hours) as needed for pruritis.
11. Camphor-Menthol 0.5-0.5 % Lotion Sig: One (1) Appl Topical QID (4 times a day) as needed for pruritus.
12. Acetaminophen 325mg Tablet Sig: Take 1 tablet every 8 hours or as directed by a healthcare provider. Do not take more than 3 tablets in 24 hours, including the last dose.
13. Nutritional Evaluation and Counseling
14. Dressing Changes Performed by Plastic Surgery Services for skin damage at sacrum (above buttocks).
15. Fever, Chills, or Shortness of Breath Follow-up: Contact ___, RN, at ___ for further assessment.
16. Pain Management Plan: Use the pain medications as instructed and follow up with an analgesic management plan if needed.
17. Monitoring Your Kidneys: Continue to monitor your kidney function through regular doctor visits and laboratory tests. Notify your healthcare provider if you experience any worsening of kidney function or new symptoms such as fever, chills, or shortness of breath.

Model Info: stablelm-zephyr:3b, chunk_size=1024, chunk_overlap=0
Time taken: 00 min and 42 secs


EXAMPLE 2
Does the patient have pneumonia?: 
Based on the discharge instructions provided, here is a summary of the medications and dosages that the patient should continue taking, stop taking, and start taking:

Medications to Continue Taking:

1. Lipitor 20mg - daily
2. Folate 1mg - daily
3. Protonix 40mg - daily
4. Vitamin C 1g - daily (monthly)
5. Cyanocobalamin 1g - monthly (on the date listed)

Medications to Stop Taking:

1. Citrucel 1g - bid (twice a day)
2. Diltiazem 240mg - qday (every day)
3. Triamterene/Hydrochlorothiazide 75/50mg - qday (every day)
4. Valsartan 320mg - qday (every day)

Medications to Start Taking:

1. Benadryl - as needed for itching
2. Hydroxyzine - as needed for itching
3. Camphor-methol - as needed for itching
4. Petrolatum-mineral oil - as needed for skin care
5. Lorazepam - as needed for nausea, vomiting, or anxiety (do not drive or drink alcohol while taking this)
6. Morphine - as needed for pain (do not drive or drink alcohol while taking this)
7. Senna and colace - daily to prevent constipation
8. Miralax and bisacodyl - if you become constipated

It is important to note that the patient should notify their nurse, [Name], at [Phone Number] for any fever, chills, shortness of breath, or inability to take oral fluids.

Model Info: llama2, chunk_size=1024, chunk_overlap=0
Time taken: 01 min and 02 secs
```

**`2-prompt-attempt.py`**

Then I defined the prompt more strictly, specifying different sections in the prompt template.

>NOTE: The model does not remember its responses from previous runs of the same code. Each time the code is executed, a new instance of the model is created, and it processes the input text independently without any memory of past interactions. 

```
# Define the structured PromptTemplate for checking pneumonia
pneumonia_prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician reviewing a discharge summary from clinical notes for patients in an ICU.\n"
        "Task: Determine if the patient had pneumonia.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the patient have pneumonia? Answer strictly in 'Yes' or 'No':"
    ),
    input_variables=["discharge_text"]
)
```

There was inconsistency with the answers:

| Model |  Output |
| --------------- | --------------- |
| stablelm-zephyr:3b, chunk_size=1024, chunk_overlap=0 | <ol><li>No, 00 min and 16 secs</li><li>No, the discharge does not mention pneumonia. The primary and secondary diagnoses mentioned are metastatic RCCA (Renal Cell Carcinoma), VRE/MRSA sepsis, acute renal failure, SBO (shortness of breath due to exertion), peripheral necrosis of digits, acute mental status changes, and skin damage issues. 00 min and 44 secs</li><li>No, the patient does not have pneumonia. They had a UTI with e-coli and were treated with antibiotics, and their urine cultures have since been normal. 00 min and 03 secs</li><li>No, 00 min and 00 secs</li><li>No, 00 min and 00 secs</li></ol> |
| llama2, chunk_size=512, chunk_overlap=0 | <ol><li>Yes, 00 min and 00 secs</li><li>Yes, 00 min and 00 secs</li><li>Yes, 00 min and 00 secs</li><li>No, 00 min and 00 secs</li><li>Yes, 00 min and 00 secs</li></ol>|
| llama2, chunk_size=1024, chunk_overlap=0 | <ol><li>Yes, 00 min and 54 secs</li><li>Yes, 00 min and 55 secs</li><li>TO DO</li><li>TO DO</li><li>TO DO</li></ol> |
| llama2, chunk_size=500, chunk_overlap=100 | <ol><li>Yes, 00 min and 00 secs</li><li>TO DO</li><li>TO DO</li><li>TO DO</li><li>TO DO</li></ol>|
| llama3, chunk_size=512, chunk_overlap=0 |<ol><li>No, 00 min and 52 secs</li><li>No, 00 min and 59 secs</li><li>No, 00 min and 00 secs</li><li>No, 00 min and 00 secs</li><li>No, 00 min and 00 secs</li></ol>|
| llama3, chunk_size=1024, chunk_overlap=0 | <ol><li>No, 00 min and 50 secs</li><li>No, 00 min and 00 secs</li><li>No, 00 min and 46 secs</li><li>No, 00 min and 00 secs</li><li>No, 00 min and 00 secs</li></ol>|


Then I asked the prompt to explain its reasoning.

```
pneumonia_prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician reviewing a discharge summary from clinical notes for patients in an ICU.\n"
        "Task: Determine if the patient had pneumonia.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the patient have pneumonia? Answer strictly in 'Yes' or 'No'. If 'Yes', give a sentence explaining why:"
    ),
    input_variables=["discharge_text"]
)
```

This gave me the following results for llama2:

```
Model Info: llama2, chunk_size=500, chunk_overlap=100

TRIAL 1, Time taken: 00 min and 07 secs
Does the patient have pneumonia?: No, the patient does not have pneumonia. The discharge summary does not mention any symptoms or findings that would indicate pneumonia, such as cough, fever, or difficulty breathing.

TRIAL 2, Time taken: 00 min and 11 secs
Does the patient have pneumonia?: Yes, the patient has pneumonia. The discharge diagnosis includes "VRE/MRSA sepsis" and "acute respiratory failure," which are indicative of pneumonia. Additionally, the patient's vital signs and laboratory results suggest the presence of pneumonia.

TRIAL 3, Time taken: 00 min and 58 secs
Does the patient have pneumonia?: Yes, the patient has pneumonia. The discharge summary mentions that the patient developed bacteremia (bacteria in the blood) during their stay, which can lead to pneumonia. Additionally, the patient's chest X-ray showed infiltrates, which is a common symptom of pneumonia.

TRIAL 4, Time taken: 00 min and 56 secs
Does the patient have pneumonia?: Yes, the patient has pneumonia. The discharge summary mentions that the patient developed bacteria in their blood and was treated with antibiotics for MRSA and VRE. This suggests that the patient had an infection in their lungs, which is a common complication of cancer treatment.

```

And llama3:

```
PROMPT (slightly changed because I wanted reasoning regardless of yes or no. Llama2 was giving reasoning for no's even though I had only told it to give reasoning if the answer was a yes. Llama3 is more obedient)

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

```
Model Info: llama3, chunk_size=500, chunk_overlap=100

TRIAL 1, Time taken: 00 min and 10 secs
Does the patient have pneumonia?: No. There is no mention of pneumonia in the discharge summary or clinical notes. The diagnoses mentioned include metastatic RCCA, VRE/MRSA sepsis, acute renal failure, SBO, and peripheral necrosis of digits, but not pneumonia.

TRIAL 2, Time taken: 00 min and 05 secs
Does the patient have pneumonia?: No. There is no mention of pneumonia in the discharge summary or clinical notes.

TRIAL 3, Time taken: 00 min and 04 secs
Does the patient have pneumonia?: No. There is no mention of pneumonia in the discharge summary notes.

TRIAL 4, Time taken: 00 min and 30 secs
Does the patient have pneumonia?: No. There is no mention of pneumonia in the discharge summary, and none of the diagnoses listed (Metastatic RCCA - s/p C1W2 HD therapy, VRE/MRSA sepsis, acute renal failure, SBO, peripheral necrosis of digits, acute mental status changes) suggest that the patient had pneumonia.
```

I also tried using a medically fine-tuned LLM (meditron) and gave it the same prompt structure. I was very unimpressed with the results, it was producing gibberish.

*ChatGPT-4o said the following for the data:*

TRIAL 1

Yes, the patient had pneumonia. The relevant information indicating pneumonia is found in the imaging results and brief hospital course. Specifically: 
1. CT abd/pelvis mentioned "Bibasilar consolidative opacity concerning for pneumonia." 
2. CXR mentioned, "Diffuse infiltrative pulmonary abnormality...could by virtue of asymmetry be pneumonia rather than pulmonary edema."
3. In the brief hospital course, it was noted, "Patient received antibiotic coverage for aspiration pneumonia."

These findings and treatments confirm the presence of pneumonia during the patient's ICU stay.


TRIAL 2

Based on the information provided in the discharge summary, the patient had findings concerning for pneumonia. The specific indications are as follows:

1. CT Abdomen/Pelvis: "Bibasilar consolidative opacity concerning for pneumonia."
2. CXR: "A more focal opacity at the left lung base laterally would be better evaluated after hemodynamic status is optimized. It could be a small region of infection or infarction, pleural effusion, or transient atelectasis."
3. Brief Hospital Course: The patient received antibiotic coverage for aspiration pneumonia.
While there is no definitive positive culture or conclusive diagnosis of pneumonia in the respiratory cultures, the imaging findings and the clinical decision to provide antibiotic coverage for pneumonia suggest that the patient did have pneumonia during their ICU stay.

*ChatGPT 3.5 said the following for the data:*

TRIAL 1

It seems like there are several indications of respiratory issues in the clinical notes:
1. Bibasilar consolidative opacity on CT scan, which is concerning for pneumonia.
2. Extensive new ground-glass opacities on chest CT, suggestive of drug-induced toxicity or infection, which could include pneumonia.
3. Diffuse infiltrative pulmonary abnormality on chest X-ray, potentially indicating pneumonia.

Although these findings strongly suggest the possibility of pneumonia, it's important to note that a definitive diagnosis of pneumonia is not explicitly mentioned in the discharge summary.

TRIAL 2

Based on the clinical notes, the patient's discharge summary does not mention pneumonia as a diagnosis. The patient had a complicated hospital course with various issues including sepsis, renal failure, gastrointestinal problems, thrombocytopenia, and respiratory failure among others, but pneumonia is not listed as one of the conditions.

**`3-prompt-attempt.py`**

```
llama3, chunk_size=500, chunk_overlap=100

pneumonia_prompt_template = PromptTemplate(
    template=(
        "Context: You are a clinician reviewing a discharge text from clinical notes for patients in an ICU.\n"
        "Task: Check if there is any mention of pneumonia, in the text.\n"
        "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
        "Discharge Text:\n{discharge_text}\n\n"
        "Query: Does the patient have pneumonia? Answer strictly in 'Yes' or 'No'. Give a sentence explaining why:"
    ),
    input_variables=["discharge_text"]
)

TRIAL 1: Time taken: 00 min and 05 secs
Does the patient have pneumonia?: No. There is no mention of pneumonia in the discharge text or clinical notes. The secondary diagnoses listed include VRE/MRSA sepsis, acute renal failure, and SBO, but not pneumonia.

TRIAL 2: Time taken: 00 min and 25 secs
Does the patient have pneumonia?: No. 

The query is asking about pneumonia, but there is no mention of it in the discharge text. The patient has metastatic renal cell carcinoma, VRE/MRSA sepsis, acute renal failure, small bowel obstruction, peripheral necrosis of digits, and acute mental status changes, but pneumonia is not one of the listed diagnoses or conditions.
```

**Realised, I wasn't chunking properly. This is what was causing the problem. Let me now go through this whole process again and try and come up with a new strategy.** [[Link]](https://github.com/anish-narain/final-year-project/blob/main/identifying-ARDS/llm-work/further-exploration.md)
