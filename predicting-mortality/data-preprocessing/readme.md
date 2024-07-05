# Pre-processing MIMIC for Mortality Prediction

In the `bigquery-scripts` folder, the following can be found. All of these are based off of the work done in [MIMIC-IV Code Repository](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv).

| BigQuery Script | Description |
|-----------------|-----------------|
| icustay_detail | Gives information about the icu stays of a patient |
| icustay_exclude_multinst | Returns same stuff as icustay_detail but only for patients with **one ICU admission**. |
| icustay_exclude_multinst_age *(cohortb)* | Returns same stuff as icustay_detail but only for patients with **one ICU admission** AND **18 <= age <= 90**. |
| icustay_exclude_multinst_age_los *(cohorta)* | Returns same stuff as icustay_detail but only for patients with **one ICU admission** AND **18 <= age <= 90**. los_icu provides number of days the patient was in the ICU. This contains code for including patients that were **only in the ICU for 48 hours (2 days)** or less. |
| cohorta_sfd | Reduced number of columns being returned. This query provides 6 individual SOFA scores and the total SOFA score for patients in cohorta. |
| cohorta_trial1_data | Constructured using cohorta. More detail below. |


## cohorta_trial1_data

This script returns the features, concepts and labels associated with patients from cohorta. Using the work done in [Predicting In-Hospital Mortality of Lung Cancer Patients](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9879439/) in the ICU paper as inspiration, the SOFA score, Aniongap, Albumin, and Total Bilirubin values were chosen for the mortality prediction task. 

**Features**

Since we are only looking at patients who were admitted to the ICU once for less than 48 hours, the lab measurements were from the patient's first day in the ICU. The measurements chosen were the ones that help evaluate the SOFA score, Aniongap, Albumin, and Total Bilirubin.

<u>*SOFA Related*</u>
1. rsp_pao2fio2_vent_min
2. rsp_pao2fio2_novent_min
3. cgn_platelet_min
4. lvr_bilirubin_max
5. cdv_mbp_min
6. cdv_rate_dopamine
7. cdv_rate_dobutamine
8. cdv_rate_epinephrine
9. cdv_rate_norepinephrine
10. gcs_min
11. rfl_urineoutput
12. rfl_creatinine_max

The first 3 letters reflect which individual component's calculation of the SOFA score the lab measurement contributes to: respiratory, coagulation, liver (hepatic), cardiovascular, neurological (Glasgow coma scale), renal.

<u>*Other lab values*</u>
1. albumin
2. anion_gap
3. total_bilirubin = lvr_bilirubin_max

**Concepts**

All the concepts are binary flags (1 represents that it has occurred, 0 means not occurred).

<u>*Individual Component SOFA Failure*</u>

* Organ failure moderate (name_moderate): Organ SOFA score 1-3 
* Organ failure severe (name_severe): Organ SOFA score 4

12 concepts: rsp_fail_moderate, rsp_fail_severe, cgn_fail_moderate, cgn_fail_severe, lvr_fail_moderate, lvr_fail_severe, cdv_fail_moderate, cdv_fail_severe, gcs_fail_moderate, gcs_fail_severe, rfl_fail_moderate, rfl_fail_severe

<u>*Combining the Individual SOFA Components*</u>
| Potential Condition                  | Code | Criteria                                                  |
|--------------------------------------|------|-----------------------------------------------------------|
| Septic Shock                         | SSH  | Cardiovascular Score ≥ 3 and any other organ score ≥ 2    |
| ARDS                                 | ARD  | Respiratory score ≥ 3 and Cardiovascular score ≥ 1 and CNS score ≥ 2 |
| Hepatorenal Syndrome                 | HES  | Liver score ≥ 2 and renal score ≥ 2                       |
| Coagulopathy-Related Organ Dysfunction | COD  | Coagulation score ≥ 3 and liver score ≥ 2                 |
| Multiple Organ Dysfunction Syndrome  | MOD  | Failure scores ≥ 2 in three or more organ systems         |
| CNS and Renal Failure                | CRF  | CNS score ≥ 3 and renal score ≥ 2                         |
| Liver and Coagulation Failure        | LCF  | Liver score ≥ 3 and coagulation score ≥ 3                 |

<u>*Other Concepts*</u>
1. High Aniongap: aniongap > 12 mEq/L
2. Low Albumin: < 3.4 g/dL
3. High Albumin: > 5.4 g/dL
4. High bilirubin: > 1.2 md/dL

**Label**

For now, the label is mortality within the year. Since MIMIC contains the date of death for patients that died within a year, if the dod column for the patient is populated, `mortality_year` is 1 otherwise, it is 0.


## Resources
1. Reference BigQuery scripts: https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv/concepts
2. Tutorial for setting up BigQuery for MIMIC: https://mimic.mit.edu/docs/gettingstarted/cloud/bigquery/
