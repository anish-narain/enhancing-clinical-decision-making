WITH ards_cohort AS (
    SELECT
        hadm_id,
        ARDS
    FROM
        `mimic-big-query.ards_dataset.ards-cohort-cleaned`
),

icu_details AS (
    SELECT
        hadm_id,
        ARRAY_AGG(stay_id) AS stay_ids
    FROM
        `physionet-data.mimiciv_derived.icustay_detail`
    GROUP BY
        hadm_id
),

medications AS (
    SELECT
        hadm_id,
        MAX(CASE WHEN stay_id IN (SELECT stay_id FROM `physionet-data.mimiciv_derived.dopamine`) THEN 1 ELSE 0 END) AS Dopamine,
        MAX(CASE WHEN stay_id IN (SELECT stay_id FROM `physionet-data.mimiciv_derived.epinephrine`) THEN 1 ELSE 0 END) AS Epinephrine,
        MAX(CASE WHEN stay_id IN (SELECT stay_id FROM `physionet-data.mimiciv_derived.norepinephrine`) THEN 1 ELSE 0 END) AS Norepinephrine,
        MAX(CASE WHEN stay_id IN (SELECT stay_id FROM `physionet-data.mimiciv_derived.vasopressin`) THEN 1 ELSE 0 END) AS Vasopressin,
        MAX(CASE WHEN stay_id IN (SELECT stay_id FROM `physionet-data.mimiciv_derived.phenylephrine`) THEN 1 ELSE 0 END) AS Phenylephrine
    FROM
        icu_details,
        UNNEST(stay_ids) AS stay_id
    GROUP BY
        hadm_id
)

SELECT
    ards.hadm_id,
    ards.ARDS,
    meds.Dopamine,
    meds.Epinephrine,
    meds.Norepinephrine,
    meds.Vasopressin,
    meds.Phenylephrine
FROM
    ards_cohort ards
LEFT JOIN
    medications meds
ON
    ards.hadm_id = meds.hadm_id;
