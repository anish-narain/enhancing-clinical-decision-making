# Identifying ARDS Using CBM & LLM

## Files In This Folder
| Folder | Description |
| --------------- | --------------- |
| `cbm-work`| The CBMs trained on the original concept set can be found in `vanilla-models` and `vanilla-model-trials`. The CBMs trained on the augmented concept set with LLM concepts can be found in `enhanced-models` and `enhanced-model-trials`. The model-trials folders contain fine-tuned CBMs.|
| `data-preprocessing`| <ol><li>`bigquery-scripts`: Contains the BigQuery SQL files which helped process the data for ARDS identification. Upon following the [set-up instructions](https://mimic.mit.edu/docs/gettingstarted/cloud/bigquery/) (and uploading `ards-cohort-cleaned.csv` into `mimic-big-query.ards_dataset.ards-cohort-cleaned`) these scripts can be copied and pasted directly into BigQuery.</li><li>`readme.md`: Describes the BigQuery SQL files and the reasoning behind why they were used.</li></ol> |
| `llm-work` | Contents of this folder have been described in its [`readme.md`](https://github.com/anish-narain/final-year-project/tree/main/identifying-ARDS/llm-work#readme).|
|`report-experiments`| <ol><li>`ards-experiments.ipynb`: Contains code for regression baselines.</li><li>`creating-images.ipynb`: Contains code for the loss plots presented in the final thesis.</li><li>`for-cbm-enhanced`: Contains enhanced CBM code with completeness score and for comparing against vanilla evaluation metrics.</li><li>`for-cbm-vanilla`: Contains vanilla CBM code with completeness score and heatmaps.</li><li>`for-llm`: Contains LLM code for some of the evaluation described in final thesis.</li></ol>|



