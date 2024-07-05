WITH ranked_data AS (
    SELECT
        icd.hadm_id,
        s.cns,
        s.gcs_min,
        s.stay_id,
        s.starttime,
        ards.ARDS,
        RANK() OVER (PARTITION BY icd.hadm_id ORDER BY s.cns DESC, s.starttime) AS rank_cns
    FROM
        `physionet-data.mimiciv_derived.icustay_detail` AS icd
    JOIN
        `physionet-data.mimiciv_derived.sofa` AS s
        ON icd.stay_id = s.stay_id
    JOIN
        `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
        ON icd.hadm_id = ards.hadm_id
    WHERE
        s.cns IS NOT NULL
),

max_cns_data AS (
    SELECT
        hadm_id,
        cns AS max_cns,
        gcs_min AS max_cns_gcs_min,
        ARDS
    FROM
        ranked_data
    WHERE
        rank_cns = 1
)

SELECT
    rd.hadm_id,
    AVG(rd.cns) AS avg_cns,
    AVG(rd.gcs_min) AS avg_gcs_min,
    mrd.max_cns,
    mrd.max_cns_gcs_min,
    mrd.ARDS
FROM
    ranked_data rd
JOIN
    max_cns_data mrd
    ON rd.hadm_id = mrd.hadm_id
GROUP BY
    rd.hadm_id,
    mrd.max_cns,
    mrd.max_cns_gcs_min,
    mrd.ARDS;
