WITH sofa AS (
    SELECT stay_id,
           starttime,
           endtime,
           respiration_24hours AS respiration,
           coagulation_24hours AS coagulation,
           liver_24hours AS liver,
           cardiovascular_24hours AS cardiovascular,
           cns_24hours AS cns,
           renal_24hours AS renal,
           sofa_24hours AS sofa_score
    FROM `physionet-data.mimiciv_derived.sofa`
    WHERE sofa_24hours >= 2
),

s1 AS (
    SELECT soi.subject_id,
           soi.stay_id,
           soi.ab_id,
           soi.antibiotic,
           soi.antibiotic_time,
           soi.culture_time,
           soi.suspected_infection,
           soi.suspected_infection_time,
           soi.specimen,
           soi.positive_culture,
           starttime,
           endtime,
           respiration,
           coagulation,
           liver,
           cardiovascular,
           cns,
           renal,
           sofa_score,
           sofa_score >= 2 AND suspected_infection = 1 AS sepsis3,
           ROW_NUMBER() OVER (
               PARTITION BY soi.stay_id
               ORDER BY
                   suspected_infection_time,
                   antibiotic_time,
                   culture_time,
                   endtime
           ) AS rn_sus
    FROM `physionet-data.mimiciv_derived.suspicion_of_infection` AS soi
    INNER JOIN sofa ON soi.stay_id = sofa.stay_id
        AND sofa.endtime >= DATETIME_SUB(soi.suspected_infection_time, INTERVAL 48 HOUR)
        AND sofa.endtime <= DATETIME_ADD(soi.suspected_infection_time, INTERVAL 24 HOUR)
    WHERE soi.stay_id IS NOT NULL
),

icustay_detail AS (
    SELECT subject_id,
           hadm_id,
           stay_id
    FROM `physionet-data.mimiciv_derived.icustay_detail`
),

ards_cohort_cleaned AS (
    SELECT DISTINCT hadm_id
    FROM `mimic-big-query.ards_dataset.ards-cohort-cleaned`
),

ranked_data AS (
    SELECT icd.hadm_id,
           s1.sofa_score,
           s1.suspected_infection,
           s1.sepsis3,
           ROW_NUMBER() OVER (
               PARTITION BY icd.hadm_id
               ORDER BY s1.sofa_score DESC, s1.suspected_infection_time, s1.antibiotic_time, s1.culture_time, s1.endtime
           ) AS rn
    FROM ards_cohort_cleaned AS acc
    JOIN icustay_detail AS icd ON acc.hadm_id = icd.hadm_id
    JOIN s1 ON icd.stay_id = s1.stay_id
    WHERE s1.rn_sus = 1
)

SELECT hadm_id,
       sofa_score,
       suspected_infection,
       sepsis3
FROM ranked_data
WHERE rn = 1
ORDER BY hadm_id;
