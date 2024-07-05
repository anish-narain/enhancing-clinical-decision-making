# Predicting Mortality With CBM

## Files In This Folder
| Folder | Description |
| --------------- | --------------- |
| `cbm-work`| `models` contains the original CBMs trained on the mortality prediction dataset and `model-trials` contains the fine-tuned CBMs.|
| `data-preprocessing`| <ol><li>`bigquery-scripts`: Contains the BigQuery SQL files which helped process the data used for mortality prediction. Upon following the [set-up instructions](https://mimic.mit.edu/docs/gettingstarted/cloud/bigquery/) these scripts can be copied and pasted directly into BigQuery.</li><li>`readme.md`: Describes the BigQuery SQL files and the reasoning behind why they were used.</li></ol>|
| `report-experiments`|<ol><li>`mortality-experiments.ipynb`: Contains code for regression baselines.</li><li>`creating-images.ipynb`: Contains code for the loss plots presented in the final thesis.</li><li>The other files are the L2 regularised CBMs. Their heatmaps were used in the final thesis and poster.</li></ol>|