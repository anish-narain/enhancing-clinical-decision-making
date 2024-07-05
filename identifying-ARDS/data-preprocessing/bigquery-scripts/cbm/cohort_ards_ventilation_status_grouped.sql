SELECT
    ards.hadm_id,
    MAX(CASE WHEN vent.ventilation_status = 'InvasiveVent' THEN 1 ELSE 0 END) AS InvasiveVent,
    MAX(CASE WHEN vent.ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS SupplementalOxygen,
    MAX(CASE WHEN vent.ventilation_status = 'HFNC' THEN 1 ELSE 0 END) AS HFNC,
    MAX(CASE WHEN vent.ventilation_status = 'NonInvasiveVent' THEN 1 ELSE 0 END) AS NonInvasiveVent,
    MAX(CASE WHEN vent.ventilation_status = 'Tracheostomy' THEN 1 ELSE 0 END) AS Tracheostomy,
    MAX(CASE WHEN vent.ventilation_status IS NULL OR vent.ventilation_status = 'None' THEN 1 ELSE 0 END) AS None
FROM
    `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
LEFT JOIN
    `physionet-data.mimiciv_derived.icustay_detail` AS icu
    ON ards.hadm_id = icu.hadm_id
LEFT JOIN
    `physionet-data.mimiciv_derived.ventilation` AS vent
    ON icu.stay_id = vent.stay_id
GROUP BY
    ards.hadm_id;
