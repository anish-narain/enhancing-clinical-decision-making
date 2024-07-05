# Pre-processing MIMIC for ARDS Identification - CBM

Firstly, I got all the hospital admissions and the associated ARDS diagnosis from Dominic and put it into one csv file `ards-cohort.csv`, cleaned it a little (`ards-cohort-cleaned.csv`), and uploaded it into BigQuery (`mimic-big-query.ards_dataset.ards-cohort-cleaned`). It can be found in the `csv-files` folder. Note that my BigQuery project is `mimic-big-query`, and I created a Dataset called `ards_dataset` and a table called `ards-cohort-cleaned`. I then gathered the features and concepts associated with this patient cohort.

In the `bigquery-scripts` folder, the following can be found. All of these are based off of the work done in [MIMIC-IV Code Repository](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv).

| BigQuery Script | Description |
|-----------------|-----------------|
| ards1-resp.sql | This identifies any pre-existing respiratory illnesses for the patients. There are 6 different flags for the diagnosis of different categories of respiratory diseases. These are features for the CBM. The concepts are whether the patient has "moderate" or "severe" pre-existing medical conditions. More detail below. |
| <ol><li>ventilation_status.sql</li><li>cohort_ards_ventilation_status.sql</li><li>cohort_ards_ventilation_status_grouped.sql</li><li>ards2-vent.sql</li></ol>  | <ol><li>Identifies all the 6 possible ventilation status types: InvasiveVent, SupplementalOxygen, HFNC, NonInvasiveVent, Tracheostomy, None</li><li>Returns two columns: hadm_id (in the ARDS cohort) and ventilation_status associated with that hadm_id.</li><li>Returns columns hadm_id and InvasiveVent, SupplementalOxygen, HFNC, NonInvasiveVent, Tracheostomy, None (where the ventilation status columns will contain 1 if the patient received that ventilator type and 0 if not).</li><li>Returns everything from the previous query but also the concept columns: c_vent_low (for supplemental oxygen), c_vent_moderate (for HFNC and NonInvasiveVent), c_vent_high (InvasiveVent and Tracheostomy). </li></ol>  |
| <ol><li>cohort_ards_renal.sql</li><li>cohort_ards_respiration.sql</li><li>cohort_ards_cns.sql</li><li>cohort_ards_sofa.sql</li><li>ards3-sofa.sql</li></ol> |<ol><li>Looks at the sofa table from mimiciv_derived. For each hospital admission it returns information about the 24 hr urine output and max creatinine recorded and the corresponding SOFA renal failure score. I chose to return the average of the 3 values and the first instance of the 3 values associated with the maximum failure score recorded for the hadm_id. Avg: avg_renal (average sofa renal failure score), avg_uo_24hr, avg_creatinine_max. Max: max_renal (maximum sofa renal failure score recorded for the hadm_id), max_renal_uo_24hr, max_renal_creatinine_max (These are the measurements corresponding to the first instance that the max_renal score was recorded for the hadm_id).</li><li>Does same as cohort_ards_renal but with avg_respiration, avg_pao2fio2ratio_novent, avg_pao2fio2ratio_vent, max_respiration, max_respiration_pao2fio2ratio_novent, max_respiration_pao2fio2ratio_vent. However, it only returns 2018 values even though there are 2021 hadm_id in the ARDS cohort. Running `missing-respiration-values.sql` reveals which 3 hadm_id have null respiration measurements. Running `ards-sofa-join.sql` shows how many values are available for the ARDS cohort for renal score, respiration score and cns score (respiration has the most null values). </li><li>Does same as cohort_ards_renal but with avg_cns, avg_gcs_min, max_cns, max_cns_gcs_min.</li><li>Combines all the three queries</li><li>Returns features and concepts for renal failure, respiration failure, and cns failure.</li></ol> |
| ards4-sepsis.sql  | Returns the sepsis status for patients in the ARDS cohort. Returns columns: sofa_score (total sofa value from the sofa table), suspected_infection (from suspicion_of_infection) and sepsis3 (calculated based on criteria: s.sofa_24hours >= 2 AND soi.suspected_infection = 1).|
| <ol><li>cohort_ards_shock.sql</li><li>ards5-shock.sql</li></ol> | <ol><li>This query identifies whether each hospital admission (hadm_id) in the ARDS cohort received specific medications (Dopamine, Epinephrine, Norepinephrine, Vasopressin, Phenylephrine) by checking all associated ICU stays (stay_ids) for the presence of these medications.</li><li>It adds 3 new columns to the previous query: one_vasopressor = 1 if exactly one vasopressor is administered, otherwise 0. The multi_vasopressor = 1 if more than one vasopressor is administered. The c_shock column = 1 if at least one vasopressor is administered. </li></ol> |
| ards6-total.sql | Query takes 10 seconds. Returns all the features, concepts (and other variables needed to identify features/concepts) as discussed above. It is the combination of all the ards{number}-{category}.sql files.|

## `ards1-resp.sql`

**Features**

| Column Name                   | Description                                                                                                                                                        | ICD Codes                                                      |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| upper_respiratory_infections  | These include infections of the nasal passages, pharynx, larynx, and upper trachea. Common conditions include the common cold, pharyngitis, sinusitis, and laryngitis. | `SUBSTR(icd9_code, 1, 3) BETWEEN '460' AND '466' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J00' AND 'J06'` |
| influenza_pneumonia           | This category encompasses viral infections like influenza and bacterial infections like pneumonia. These conditions affect the lungs and respiratory system, often causing symptoms such as fever, cough, and difficulty breathing. | `SUBSTR(icd9_code, 1, 3) IN ('480', '481', '482', '483', '484', '485', '486', '487') OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J09' AND 'J18'` |
| acute_lower_respiratory_infections | These include infections that affect the lower respiratory tract, such as bronchitis and bronchiolitis. These infections are typically more severe than upper respiratory infections and can lead to significant respiratory distress. | `SUBSTR(icd9_code, 1, 3) BETWEEN '466' AND '469' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J20' AND 'J22'` |
| chronic_lower_respiratory_diseases | Chronic conditions such as chronic obstructive pulmonary disease (COPD), chronic bronchitis, and emphysema fall under this category. These diseases are characterized by long-term respiratory symptoms and airflow limitation. | `SUBSTR(icd9_code, 1, 3) BETWEEN '490' AND '496' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J40' AND 'J47'` |
| lung_diseases_due_to_external_agents | This category includes diseases caused by inhalation of external agents such as smoke, dust, chemicals, and environmental pollutants. Conditions like pneumoconiosis and other occupational lung diseases are included. | `SUBSTR(icd9_code, 1, 3) BETWEEN '500' AND '508' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J60' AND 'J70'` |
| other_respiratory_diseases | This is a broader category that includes various other respiratory conditions not classified under the above categories. Examples include respiratory failure, pulmonary embolism, and pleurisy. | `SUBSTR(icd9_code, 1, 3) BETWEEN '510' AND '519' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J80' AND 'J99'` |

**Concepts**
* `c_rsp_mod`: Moderate pre-existing conditions (1 or 2 conditions)
* `c_rsp_svr`: Severe pre-existing conditions (3 or more conditions)

(if both are 0 then the patient has no pre-existing respiratory conditions)

## `ards3-sofa.sql`

Follows the following format but for renal failure (renf), respiration failure (respf), and cns failure (cnsf).

<ol>
    <li>c_max_renf_moderate: 1 if max_renal = 1 or 2, 0 otherwise</li>
    <li>c_max_renf_severe: 1 if max_renal = 3 or 4, 0 otherwise</li>
    <li>c_avg_renf_moderate: 1 if avg_renal is between 1 and 2, 0 otherwise</li>
    <li>c_avg_renf_severe: 1 if avg_renal > 2, 0 otherwise</li>
</ol>

## `ards5-shock.sql`
The relevant medications typically used to treat shock include:

1. Dopamine - often used as a vasopressor in shock treatment.
2. Epinephrine - another vasopressor used in severe shock.
3. Norepinephrine - the first-line vasopressor for septic shock.
4. Vasopressin - can be used as an adjunct vasopressor in shock.
5. Phenylephrine - another vasopressor option.

If a patient in the ARDS cohort was provided any of these drugs, it was assumed that they suffered from shock.

## Final Feature-Concept table

| Category | Features | Concepts |
|-----------------|-----------------|-----------------|
| Pre-existing respiratory conditions | <ol><li>upper_respiratory_infections</li><li>influenza_pneumonia</li><li>acute_lower_respiratory_infections</li><li>chronic_lower_respiratory_diseases</li><li>lung_diseases_due_to_external_agents</li><li>other_respiratory_diseases</li></ol> | <ol><li>c_rsp_mod</li><li>c_rsp_svr</li></ol>|
| Ventilation status | <ol><li>InvasiveVent</li><li>SupplementalOxygen</li><li>HFNC</li><li>NonInvasiveVent</li><li>Tracheostomy</li><li>None</li></ol> | <ol><li>c_vent_low</li><li>c_vent_moderate</li><li>c_vent_high</li></ol> |
| Renal failure | <ol><li>avg_uo_24hr</li><li>avg_creatinine_max</li><li>max_renal_uo_24hr</li><li>max_renal_creatinine_max</li></ol> | <ol><li>c_max_renf_moderate</li><li>c_max_renf_severe</li><li>c_avg_renf_moderate</li><li>c_avg_renf_severe</li></ol> |
| Respiratory failure | <ol><li>avg_pao2fio2ratio_novent</li><li>avg_pao2fio2ratio_vent</li><li>max_respiration_pao2fio2ratio_novent</li><li>max_respiration_pao2fio2ratio_vent</li></ol> |<ol><li>c_max_respf_moderate</li><li>c_max_respf_severe</li><li>c_avg_respf_moderate</li><li>c_avg_respf_severe</li></ol>|
| Neurological failure | <ol><li>avg_gcs_min</li><li>max_cns_gcs_min</li></ol> | <ol><li>c_max_cnsf_moderate</li><li>c_max_cnsf_severe</li><li>c_avg_cnsf_moderate</li><li>c_avg_cnsf_severe</li></ol> |
| Sepsis | <ol><li>sofa_score</li><li>suspected_infection</li></ol> | c_sepsis3 |
| Shock | <ol><li>one_vasopressor</li><li>multi_vasopressor</li></ol> | c_shock |


**Features**

26 features:

['upper_respiratory_infections', 'influenza_pneumonia', 'acute_lower_respiratory_infections', 'chronic_lower_respiratory_diseases', 'lung_diseases_due_to_external_agents', 'other_respiratory_diseases', 'InvasiveVent', 'SupplementalOxygen', 'HFNC', 'NonInvasiveVent', 'Tracheostomy', 'None', 'avg_uo_24hr', 'avg_creatinine_max', 'max_renal_uo_24hr', 'max_renal_creatinine_max', 'avg_pao2fio2ratio_novent', 'avg_pao2fio2ratio_vent', 'max_respiration_pao2fio2ratio_novent', 'max_respiration_pao2fio2ratio_vent', 'avg_gcs_min', 'max_cns_gcs_min', 'sofa_score', 'suspected_infection', 'one_vasopressor', 'multi_vasopressor']

**Concepts**

19 concepts:

['c_rsp_mod', 'c_rsp_svr', 'c_vent_low', 'c_vent_moderate', 'c_vent_high', 'c_max_renf_moderate', 'c_max_renf_severe', 'c_avg_renf_moderate', 'c_avg_renf_severe', 'c_max_respf_moderate', 'c_max_respf_severe', 'c_avg_respf_moderate', 'c_avg_respf_severe', 'c_max_cnsf_moderate', 'c_max_cnsf_severe', 'c_avg_cnsf_moderate', 'c_avg_cnsf_severe', 'c_sepsis3', 'c_shock']


# Pre-processing MIMIC for ARDS Identification - LLM

| BigQuery Script | Description |
|-----------------|-----------------|
| ards-cohort-notes-all-discharge.sql | Returns 2021 results, one summary for each of the hadm_id |
| <ol><li>ards-cohort-notes-all-radiology.sql</li><li>ards-cohort-notes-radiology-aggregated</li></ol> | <ol><li>Returns all the possible radiology reports for the ARDS cohort. 2020 of the hadm_id have radiology notes. Most of them have multiple notes, with 25 notes per hadm_id on average (found using `avg-radiology-notes.sql`). There are 50597 radiology notes for the 2020 hadm_id's.</li><li>Combines the data to only return 2020 rows for the distinct hadm_id's. The query concatenates all radiology_text values for each hadm_id, separated by ` \|\|\| `, and all radiology_note_id values, separated by a comma and space. </li></ol> |
| <ol><li>ards-cohort-notes-all-ecg.sql</li><li>count-ecg-notes.sql</li><li>avg-ecg-notes.sql</li><li>ards-cohort-notes-ecg-aggregated.sql</li></ol> | <ol><li>The ECG notes are identified by study_id. Each study_id can have up to 18 reports. For the ards cohort, there are 29,442 studies, which are all returned by this query.</li><li>Returns the number of study id's in the ARDS cohort that actually have values for the 18 different report columns. The numbers can be found below.</li><li>This query reveals the following info: The average number of reports per study_id is 3.45 and the average number of studies per hadm_id for the ards cohort is 11.79. In the end only 1881 patients have ecg reports recorded for them.</li><li>This query returns the aggregated and concatenated (separated by ` \|\|\| `) ECG reports for patients from the ARDS cohort, grouped by hospital admission IDs (hadm_id), with study IDs combined into a single string for each admission.</li></ol> |
| ards-cohort-notes.sql | Returns all the discharge, radiology and ecg reports for the ARDS cohort, grouped by hadm_id.|


Number of non-null ECG report columns for the ARDS cohort:

- **Report 0 Count:** 1
- **Report 1 Count:** 29,442
- **Report 2 Count:** 25,640
- **Report 3 Count:** 21,134
- **Report 4 Count:** 17,702
- **Report 5 Count:** 11,838
- **Report 6 Count:** 7,076
- **Report 7 Count:** 3,544
- **Report 8 Count:** 1,612
- **Report 9 Count:** 554
- **Report 10 Count:** 190
- **Report 11 Count:** 65
- **Report 12 Count:** 27
- **Report 13 Count:** 9
- **Report 14 Count:** 9
- **Report 15 Count:** 1
- **Report 16 Count:** 1
- **Report 17 Count:** 1
- **Report 18 Count:** 0
