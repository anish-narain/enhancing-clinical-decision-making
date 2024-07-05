I have a main directory `FYP-Files` which contains two folders:
1. `git` = contains the code for my FYP project
2. `MIMIC-IV` = contains two folders `clinical-notes` (free-text clinical notes) and `files` (mimiciv 2.0)

## Personal notes about MIMIC-IV Clinical Notes from Initial Querying

### My Analysis

There are 4 files in the clinical-notes folder. The are two main types of notes: `discharge` and `radiology`, the other two (discharge detail and radiology detail) provide auxiliary information about the main notes. 

[Source](https://mimic.mit.edu/docs/iv/modules/note/)

`discharge`: narrative which describes the reason for a patient's admission to the hospital, their hospital course and relevant discharge instructions. *COLUMNS: note_id, subject_id, hadm_id, note_type, note_seq, charttime, storetime, text*

`radiology`: free text report associated with radiography imaging. There are two types of notes: RR (radiology report) and AR (radiology report addendum). *COLUMNS: note_id, subject_id, hadm_id, note_type, note_seq, charttime, storetime, text*

The addendum typically includes further observations, clarifications, or additional findings that were not included in the initial report but are deemed relevant or important.

To get an idea of the structure of the clinical notes, there are a few ways of doing it:
1. Go to the [physionet files](https://physionet.org/content/mimic-iv-note/2.2/#files-panel) section and request access to Google BigQuery. You can now scroll through the different files. The problem with this is there are lots of notes so just comparing the adjacent note entries may not be representative of the overall dataset. 
2. Instead, I added functions to return the text column in both radiology (`query-radiology.py`) and discharge (`query-discharge.py`) from 5 random entries. From this, I had following initial observations for the dataset.

Radiology RR Notes
- Based on the examination type (e.g. "CHEST (PA AND LAT)" or "Paracentesis" or "Esophagram"), the subheadings (data captured) about the report is different. For example "CHEST (PA AND LAT)" and "Esophagram" had (5) whereas "LIVER OR GALLBLADDER US (SINGLE ORGAN)" had (11).
- (5) **INDICATION, TECHNIQUE, COMPARISON, FINDINGS, IMPRESSION**. (11) **INDICATION, TECHNIQUE, COMPARISON, FINDINGS, LIVER, BILE DUCTS, GALLBLADDER, PANCREAS, SPLEEN, KIDNEYS, IMPRESSION**.
- There is a range of amounts of data captured.

Radiology AR Notes
- Tends to be shorter. Accompanies corresponding RR text.
- No subheadings, just short additions of notes.

Discharge Notes
- Higher levels of detail than Radiology.
- There are some extra subheadings in the middle which are dependent on the patient (for example Oncological history), but lots of subheading/structure are repeated.
- There is a range of amounts of data captured.

### Other Resources

**EHRNoteQA**

EHRNoteQA is a benchmark dataset designed to assess the performance of LLMs in clinical contexts, utilizing MIMIC-IV discharge summaries and curated by three medical professionals ([paper](https://arxiv.org/pdf/2402.16040.pdf)). Comprising 962 unique questions tied to individual patient EHR notes, it challenges LLMs to accurately process real clinical scenarios. Two distinctive features of this dataset are its use of a multiple-choice question format, enhancing automatic evaluation, and requiring LLMs to analyze multiple clinical notes to answer a single question, mirroring real-world clinical practice where extensive patient histories are reviewed. The dataset can be found on [PhysioNet](https://physionet.org/content/ehr-notes-qa-llms/1.0.0/).

The paper worked on `discharge` to create dataset, and provided the following relevant useful insights:

#1 `discharge`
- encompasses 331,794 discharge summaries for 145,915 unique patients, with an average of 2.3 notes per patient
- these summaries are typically lengthy, with the average length of all discharge summaries for a patient being around 8k tokens
- This presents a challenge for current LLMs, as only a limited number of them can process contexts that exceed 8,000 tokens, making it difficult to handle such extensive clinical notes

#2 Minimizing excess characters: we initially reduced the overall length of the notes without altering their content or structure. By minimizing excessive white spaces, such as removing spaces or tabs around newlines, we achieved an average reduction of 10% in note length.

#3 Dividing pre-processed dataset into two levels: we categorized patients into two levels based on the length of their clinical notes, ensuring compatibility with the processing capabilities of existing LLMs. 
- The first level (Level 1) consists of patients whose cumulative note length in the database does not exceed 3,500 tokens, aligning with models designed to process up to 4k tokens. 
- The second level (Level 2) is for patients whose notes consist of 3,500 tokens to 7,500 tokens, suitable for models that can handle up to 8k tokens.

**LLMs Accelerate Annotation for Medical Information Extraction**

The Akshay Goel team at Google wrote the following [paper](https://arxiv.org/pdf/2312.02296.pdf) which looked into how effective general LLMs can be for extracting information from EHR. TLDR of the paper: they divided the annotation process of Electronic Health Records (EHRs) into two stages: initial base annotations and refined expert annotations. They examined the substitution of humans with a Large Language Model (LLM) for the base annotation stage. Their evaluation demonstrated that Google PaLM 2, conditioned with a few-shot prompting, was effective.

Their work is of interest because they used their LLM Medical Annotation method on [MIMIC-IV-Note](https://physionet.org/content/medication-labels-mimic-note/1.0.0/) and produced labels for the `discharge` notes. The way they labeled the notes was that they captured the starting and ending character in the CSV file of the text they were annotating, they then assigned the annotation for the text (REASON, MEDICATION, MODE, DURATION) and then assigned a group to the annotation entry. The group assigns a unique identifier that links the annotation to its respective medication group entry. For example:

| Start Position | End Position | Annotation | Group    |
|----------------|--------------|------------|----------|
| 384            | 396          | REASON     | 1_ACB013 |
| 1484           | 1505         | MEDICATION | 1_BBB334 |
