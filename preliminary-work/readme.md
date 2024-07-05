# Getting Familiar With CBMs, LLMs and MIMIC-IV Notes

A lot of this work is quite basic; it contains my first attempts at writing code for this project. The most useful resource is the work I did setting up a basic CBM. The only thing is, I confused validation and testing in this code, so please refer to the work I did in `identifying-ARDS/cbm-work` and `predicting-mortality/cbm-work` for corrections.

## Files In This Folder
| Folder | Description |
| --------------- | --------------- |
| `basic-cbms`| <ol><li>`colabs`: Contains basic CBM training code (run on Google Colab) that was used as a starting point for the other CBMs in this project.</li><li>`old`: Contains intial attempts at setting up a CBM.</li><li>`py-scripts`: Contains corresponding python files to run the same code from `colabs` locally.</li></ol> |
| `basic-llms` | In the `colabs` folder there are some Colab notebooks that followed tutorials for doing LLM fine-tuning. These tutorials provide a good initial overview. |
| `mimic-querying`| Contains the work I did trying to understand the MIMIC-IV clinical notes before I started using BigQuery. I wrote some insights I got, but I highly recommend not doing this and just [using BigQuery](https://github.com/anish-narain/final-year-project/tree/main/resources#2-mimic-resources) instead. |

