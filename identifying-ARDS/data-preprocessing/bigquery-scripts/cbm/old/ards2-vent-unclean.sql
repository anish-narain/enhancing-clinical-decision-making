SELECT
    `mimic-big-query.ards_dataset.ards-cohort-cleaned`.hadm_id,
    `mimic-big-query.ards_dataset.ards-cohort-cleaned`.ARDS,
    MAX(CASE WHEN vent.ventilation_status = 'InvasiveVent' THEN 1 ELSE 0 END) AS InvasiveVent,
    MAX(CASE WHEN vent.ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS SupplementalOxygen,
    MAX(CASE WHEN vent.ventilation_status = 'HFNC' THEN 1 ELSE 0 END) AS HFNC,
    MAX(CASE WHEN vent.ventilation_status = 'NonInvasiveVent' THEN 1 ELSE 0 END) AS NonInvasiveVent,
    MAX(CASE WHEN vent.ventilation_status = 'Tracheostomy' THEN 1 ELSE 0 END) AS Tracheostomy,
    MAX(CASE WHEN vent.ventilation_status IS NULL OR vent.ventilation_status = 'None' THEN 1 ELSE 0 END) AS None,
    MAX(CASE WHEN vent.ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS c_vent_low,
    MAX(CASE WHEN vent.ventilation_status IN ('HFNC', 'NonInvasiveVent') THEN 1 ELSE 0 END) AS c_vent_moderate,
    MAX(CASE WHEN vent.ventilation_status IN ('InvasiveVent', 'Tracheostomy') THEN 1 ELSE 0 END) AS c_vent_high
FROM
    `mimic-big-query.ards_dataset.ards-cohort-cleaned`
LEFT JOIN
    `physionet-data.mimiciv_derived.icustay_detail` AS icu
    ON `mimic-big-query.ards_dataset.ards-cohort-cleaned`.hadm_id = icu.hadm_id
LEFT JOIN
    `physionet-data.mimiciv_derived.ventilation` AS vent
    ON icu.stay_id = vent.stay_id
GROUP BY
    `mimic-big-query.ards_dataset.ards-cohort-cleaned`.hadm_id,
    `mimic-big-query.ards_dataset.ards-cohort-cleaned`.ARDS;