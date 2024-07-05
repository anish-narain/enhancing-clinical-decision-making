WITH ranked_data AS (
    SELECT
        icd.hadm_id,
        s.renal,
        s.uo_24hr,
        s.creatinine_max,
        s.stay_id,
        s.starttime,
        ards.ARDS,
        RANK() OVER (PARTITION BY icd.hadm_id ORDER BY s.renal DESC, s.starttime) AS rank_renal
    FROM
        `physionet-data.mimiciv_derived.icustay_detail` AS icd
    JOIN
        `physionet-data.mimiciv_derived.sofa` AS s
        ON icd.stay_id = s.stay_id
    JOIN
        `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
        ON icd.hadm_id = ards.hadm_id
    WHERE
        s.renal IS NOT NULL
),

max_renal_data AS (
    SELECT
        hadm_id,
        renal AS max_renal,
        uo_24hr AS max_renal_uo_24hr,
        creatinine_max AS max_renal_creatinine_max,
        ARDS
    FROM
        ranked_data
    WHERE
        rank_renal = 1
)

SELECT
    rd.hadm_id,
    AVG(rd.renal) AS avg_renal,
    AVG(rd.uo_24hr) AS avg_uo_24hr,
    AVG(rd.creatinine_max) AS avg_creatinine_max,
    mrd.max_renal,
    mrd.max_renal_uo_24hr,
    mrd.max_renal_creatinine_max,
    mrd.ARDS
FROM
    ranked_data rd
JOIN
    max_renal_data mrd
    ON rd.hadm_id = mrd.hadm_id
GROUP BY
    rd.hadm_id,
    mrd.max_renal,
    mrd.max_renal_uo_24hr,
    mrd.max_renal_creatinine_max,
    mrd.ARDS;
