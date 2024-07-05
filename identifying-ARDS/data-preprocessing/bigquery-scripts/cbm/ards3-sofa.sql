WITH ranked_data AS (
    SELECT
        icd.hadm_id,
        s.stay_id,
        s.starttime,
        ards.ARDS,
        s.cns,
        s.gcs_min,
        s.renal,
        s.uo_24hr,
        s.creatinine_max,
        s.respiration,
        s.pao2fio2ratio_novent,
        s.pao2fio2ratio_vent,
        RANK() OVER (PARTITION BY icd.hadm_id ORDER BY s.cns DESC, s.starttime) AS rank_cns,
        RANK() OVER (PARTITION BY icd.hadm_id ORDER BY s.renal DESC, s.starttime) AS rank_renal,
        RANK() OVER (PARTITION BY icd.hadm_id ORDER BY s.respiration DESC, s.starttime) AS rank_respiration
    FROM
        `physionet-data.mimiciv_derived.icustay_detail` AS icd
    JOIN
        `physionet-data.mimiciv_derived.sofa` AS s
        ON icd.stay_id = s.stay_id
    JOIN
        `mimic-big-query.ards_dataset.ards-cohort-cleaned` AS ards
        ON icd.hadm_id = ards.hadm_id
),

max_data AS (
    SELECT
        hadm_id,
        MAX(IF(rank_cns = 1, cns, NULL)) AS max_cns,
        MAX(IF(rank_cns = 1, gcs_min, NULL)) AS max_cns_gcs_min,
        MAX(IF(rank_renal = 1, renal, NULL)) AS max_renal,
        MAX(IF(rank_renal = 1, uo_24hr, NULL)) AS max_renal_uo_24hr,
        MAX(IF(rank_renal = 1, creatinine_max, NULL)) AS max_renal_creatinine_max,
        MAX(IF(rank_respiration = 1, respiration, NULL)) AS max_respiration,
        MAX(IF(rank_respiration = 1, pao2fio2ratio_novent, NULL)) AS max_respiration_pao2fio2ratio_novent,
        MAX(IF(rank_respiration = 1, pao2fio2ratio_vent, NULL)) AS max_respiration_pao2fio2ratio_vent,
        ARDS
    FROM
        ranked_data
    GROUP BY
        hadm_id, ARDS
)

SELECT
    rd.hadm_id,
    md.ARDS,
    AVG(rd.cns) AS avg_cns,
    AVG(rd.gcs_min) AS avg_gcs_min,
    md.max_cns,
    md.max_cns_gcs_min,
    AVG(rd.renal) AS avg_renal,
    AVG(rd.uo_24hr) AS avg_uo_24hr,
    AVG(rd.creatinine_max) AS avg_creatinine_max,
    md.max_renal,
    md.max_renal_uo_24hr,
    md.max_renal_creatinine_max,
    AVG(rd.respiration) AS avg_respiration,
    AVG(rd.pao2fio2ratio_novent) AS avg_pao2fio2ratio_novent,
    AVG(rd.pao2fio2ratio_vent) AS avg_pao2fio2ratio_vent,
    md.max_respiration,
    md.max_respiration_pao2fio2ratio_novent,
    md.max_respiration_pao2fio2ratio_vent,
    CASE WHEN md.max_renal IN (1, 2) THEN 1 ELSE 0 END AS c_max_renf_moderate,
    CASE WHEN md.max_renal IN (3, 4) THEN 1 ELSE 0 END AS c_max_renf_severe,
    CASE WHEN AVG(rd.renal) BETWEEN 1 AND 2 THEN 1 ELSE 0 END AS c_avg_renf_moderate,
    CASE WHEN AVG(rd.renal) > 2 THEN 1 ELSE 0 END AS c_avg_renf_severe,
    CASE WHEN md.max_respiration IN (1, 2) THEN 1 ELSE 0 END AS c_max_respf_moderate,
    CASE WHEN md.max_respiration IN (3, 4) THEN 1 ELSE 0 END AS c_max_respf_severe,
    CASE WHEN AVG(rd.respiration) BETWEEN 1 AND 2 THEN 1 ELSE 0 END AS c_avg_respf_moderate,
    CASE WHEN AVG(rd.respiration) > 2 THEN 1 ELSE 0 END AS c_avg_respf_severe,
    CASE WHEN md.max_cns IN (1, 2) THEN 1 ELSE 0 END AS c_max_cnsf_moderate,
    CASE WHEN md.max_cns IN (3, 4) THEN 1 ELSE 0 END AS c_max_cnsf_severe,
    CASE WHEN AVG(rd.cns) BETWEEN 1 AND 2 THEN 1 ELSE 0 END AS c_avg_cnsf_moderate,
    CASE WHEN AVG(rd.cns) > 2 THEN 1 ELSE 0 END AS c_avg_cnsf_severe
FROM
    ranked_data rd
JOIN
    max_data md
    ON rd.hadm_id = md.hadm_id
GROUP BY
    rd.hadm_id,
    md.max_cns,
    md.max_cns_gcs_min,
    md.max_renal,
    md.max_renal_uo_24hr,
    md.max_renal_creatinine_max,
    md.max_respiration,
    md.max_respiration_pao2fio2ratio_novent,
    md.max_respiration_pao2fio2ratio_vent,
    md.ARDS;
