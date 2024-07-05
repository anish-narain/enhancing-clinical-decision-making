WITH ards_cohort AS (
    SELECT
        hadm_id,
        ARDS
    FROM
        `mimic-big-query.ards_dataset.ards-cohort-cleaned`
),

icu_details AS (
    SELECT
        stay_id,
        hadm_id
    FROM
        `physionet-data.mimiciv_derived.icustay_detail`
),

ventilation_status AS (
    SELECT
        stay_id,
        ventilation_status
    FROM
        `physionet-data.mimiciv_derived.ventilation`
),

icu_ventilation AS (
    SELECT
        icu.hadm_id,
        vent.ventilation_status
    FROM
        icu_details icu
    LEFT JOIN
        ventilation_status vent
    ON
        icu.stay_id = vent.stay_id
),

aggregated_ventilation AS (
    SELECT
        hadm_id,
        MAX(CASE WHEN ventilation_status = 'InvasiveVent' THEN 1 ELSE 0 END) AS InvasiveVent,
        MAX(CASE WHEN ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS SupplementalOxygen,
        MAX(CASE WHEN ventilation_status = 'HFNC' THEN 1 ELSE 0 END) AS HFNC,
        MAX(CASE WHEN ventilation_status = 'NonInvasiveVent' THEN 1 ELSE 0 END) AS NonInvasiveVent,
        MAX(CASE WHEN ventilation_status = 'Tracheostomy' THEN 1 ELSE 0 END) AS Tracheostomy,
        MAX(CASE WHEN ventilation_status IS NULL OR ventilation_status = 'None' THEN 1 ELSE 0 END) AS None,
        MAX(CASE WHEN ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS c_vent_low,
        MAX(CASE WHEN ventilation_status IN ('HFNC', 'NonInvasiveVent') THEN 1 ELSE 0 END) AS c_vent_moderate,
        MAX(CASE WHEN ventilation_status IN ('InvasiveVent', 'Tracheostomy') THEN 1 ELSE 0 END) AS c_vent_high
    FROM
        icu_ventilation
    GROUP BY
        hadm_id
)

SELECT
    ards.hadm_id,
    ards.ARDS,
    vent.InvasiveVent,
    vent.SupplementalOxygen,
    vent.HFNC,
    vent.NonInvasiveVent,
    vent.Tracheostomy,
    vent.None,
    vent.c_vent_low,
    vent.c_vent_moderate,
    vent.c_vent_high
FROM
    ards_cohort ards
LEFT JOIN
    aggregated_ventilation vent
ON
    ards.hadm_id = vent.hadm_id;


