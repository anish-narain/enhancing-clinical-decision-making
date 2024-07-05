WITH all_hadm_ids_2021 AS (
    SELECT DISTINCT icd.hadm_id
    FROM `physionet-data.mimiciv_derived.icustay_detail` AS icd
    JOIN `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
    ON icd.hadm_id = ards.hadm_id
),

ranked_data AS (
    SELECT
        icd.hadm_id,
        s.respiration,
        s.pao2fio2ratio_novent,
        s.pao2fio2ratio_vent,
        s.stay_id,
        s.starttime,
        ards.ARDS,
        RANK() OVER (PARTITION BY icd.hadm_id ORDER BY s.respiration DESC, s.starttime) AS rank_respiration
    FROM
        `physionet-data.mimiciv_derived.icustay_detail` AS icd
    JOIN
        `physionet-data.mimiciv_derived.sofa` AS s
        ON icd.stay_id = s.stay_id
    JOIN
        `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
        ON icd.hadm_id = ards.hadm_id
    WHERE
        s.respiration IS NOT NULL
),

max_respiration_data AS (
    SELECT
        hadm_id,
        respiration AS max_respiration,
        pao2fio2ratio_novent AS max_respiration_pao2fio2ratio_novent,
        pao2fio2ratio_vent AS max_respiration_pao2fio2ratio_vent,
        ARDS
    FROM
        ranked_data
    WHERE
        rank_respiration = 1
),

final_data AS (
    SELECT
        rd.hadm_id,
        AVG(rd.respiration) AS avg_respiration,
        AVG(rd.pao2fio2ratio_novent) AS avg_pao2fio2ratio_novent,
        AVG(rd.pao2fio2ratio_vent) AS avg_pao2fio2ratio_vent,
        mrd.max_respiration,
        mrd.max_respiration_pao2fio2ratio_novent,
        mrd.max_respiration_pao2fio2ratio_vent,
        mrd.ARDS
    FROM
        ranked_data rd
    JOIN
        max_respiration_data mrd
        ON rd.hadm_id = mrd.hadm_id
    GROUP BY
        rd.hadm_id,
        mrd.max_respiration,
        mrd.max_respiration_pao2fio2ratio_novent,
        mrd.max_respiration_pao2fio2ratio_vent,
        mrd.ARDS
)

SELECT
    all_hadm_ids_2021.hadm_id
FROM
    all_hadm_ids_2021
LEFT JOIN
    final_data
    ON all_hadm_ids_2021.hadm_id = final_data.hadm_id
WHERE
    final_data.hadm_id IS NULL;
