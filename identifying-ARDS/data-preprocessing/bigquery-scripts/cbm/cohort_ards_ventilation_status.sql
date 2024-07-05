SELECT
    ards.hadm_id,
    vent.ventilation_status
FROM
    `physionet-data.mimiciv_derived.icustay_detail` AS icu
JOIN
    `physionet-data.mimiciv_derived.ventilation` AS vent
    ON icu.stay_id = vent.stay_id
JOIN
    `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
    ON icu.hadm_id = ards.hadm_id;
