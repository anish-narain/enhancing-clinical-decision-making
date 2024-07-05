SELECT 
    COUNT(*) AS total_records,
    COUNT(s.renal) AS non_null_renal,
    COUNT(s.respiration) AS non_null_respiration,
    COUNT(s.cns) AS non_null_cns
FROM
    `physionet-data.mimiciv_derived.icustay_detail` AS icd
JOIN
    `physionet-data.mimiciv_derived.sofa` AS s
    ON icd.stay_id = s.stay_id
JOIN
    `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
    ON icd.hadm_id = ards.hadm_id;
