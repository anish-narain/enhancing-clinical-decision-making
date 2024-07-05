# Augmenting Concept Set with LLM

## Files in this Folder
| Files | Contents | 
| --------------- | --------------- | 
| `initial-trials` folder | Contains the code I was writing to get an LLM up and running to summarise a discharge summary. Most of it is failed attempts to do so. | 
| `initial-exploration` folder | Context behind the files can be found in [`initial-exploration.md`](https://github.com/anish-narain/final-year-project/blob/main/identifying-ARDS/llm-work/initial-exploration.md). | 
| `further-exploration` folder | Context behind the files can be found in [`further-exploration.md`](https://github.com/anish-narain/final-year-project/blob/main/identifying-ARDS/llm-work/further-exploration.md) | 
| `helper` folder | Contains code to help process some results. |
| `deploy-scripts` folder | Contains code that will be deployed on machines to produce LLM labels for large amounts of text. |
| [`results.ipynb`](https://github.com/anish-narain/final-year-project/blob/main/identifying-ARDS/llm-work/results.ipynb)| Contains some visualisations for the work done from `further-exploration` onwards.|
| `final-exploration` folder | Contains the code I used to test my prompts for labelling the 8 concepts: Mention of ARDS, Aspiration, Bilateral Infiltrates, Cardiac Arrest, Cardiac Failure, Pancreatitis, Pneumonia, and TRALI. Each of the 8 concepts have a folder that contains their Python script, output from 15 random patients, and the validation results for those patients. It also has a `helper` folder which contains `helper.py` that was used to process the results from running the concept code.|
| `scaling-up-trials` folder | Contains my (failed) attempts to scale up the LLM labelling from 15 patients to 2021. Might be a useful starting point for someone else who wants to run this code on Imperial HPC.|
| `colabs` folder | Contains the Colab notebooks I ran (using a pro account) and the CSV files produced are in the `results` folder. |
