-- Step 1: Extract and Classify Diagnoses for Respiratory Illnesses
WITH s1 AS (
    SELECT 
        soi.subject_id,
        soi.stay_id,
        icd.hadm_id,
        soi.ab_id,
        soi.antibiotic,
        soi.antibiotic_time,
        soi.culture_time,
        soi.suspected_infection,
        soi.suspected_infection_time,
        soi.specimen,
        soi.positive_culture,
        s.sofa_24hours AS sofa_score,
        s.starttime,
        s.endtime,
        s.sofa_24hours >= 2 AND soi.suspected_infection = 1 AS sepsis3,
        ROW_NUMBER() OVER (
            PARTITION BY icd.hadm_id
            ORDER BY s.sofa_24hours DESC, soi.suspected_infection_time, soi.antibiotic_time, soi.culture_time, s.endtime
        ) AS rn_sus
    FROM `physionet-data.mimiciv_derived.suspicion_of_infection` AS soi
    INNER JOIN `physionet-data.mimiciv_derived.sofa` AS s
        ON soi.stay_id = s.stay_id
        AND s.endtime BETWEEN DATETIME_SUB(soi.suspected_infection_time, INTERVAL 48 HOUR) AND DATETIME_ADD(soi.suspected_infection_time, INTERVAL 24 HOUR)
    INNER JOIN `physionet-data.mimiciv_derived.icustay_detail` AS icd
        ON soi.stay_id = icd.stay_id
    WHERE s.sofa_24hours >= 2
),

ards_cohort_cleaned AS (
    SELECT DISTINCT hadm_id
    FROM `mimic-big-query.ards_dataset.ards-cohort-cleaned`
),

diag AS (
    SELECT
        hadm_id,
        CASE WHEN icd_version = 9 THEN icd_code ELSE NULL END AS icd9_code,
        CASE WHEN icd_version = 10 THEN icd_code ELSE NULL END AS icd10_code
    FROM `physionet-data.mimiciv_hosp.diagnoses_icd`
),

respiratory_illnesses AS (
    SELECT
        hadm_id,
        MAX(CASE WHEN SUBSTR(icd9_code, 1, 3) BETWEEN '460' AND '466' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J00' AND 'J06' THEN 1 ELSE 0 END) AS upper_respiratory_infections,
        MAX(CASE WHEN SUBSTR(icd9_code, 1, 3) IN ('480', '481', '482', '483', '484', '485', '486', '487') OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J09' AND 'J18' THEN 1 ELSE 0 END) AS influenza_pneumonia,
        MAX(CASE WHEN SUBSTR(icd9_code, 1, 3) BETWEEN '466' AND '469' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J20' AND 'J22' THEN 1 ELSE 0 END) AS acute_lower_respiratory_infections,
        MAX(CASE WHEN SUBSTR(icd9_code, 1, 3) BETWEEN '490' AND '496' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J40' AND 'J47' THEN 1 ELSE 0 END) AS chronic_lower_respiratory_diseases,
        MAX(CASE WHEN SUBSTR(icd9_code, 1, 3) BETWEEN '500' AND '508' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J60' AND 'J70' THEN 1 ELSE 0 END) AS lung_diseases_due_to_external_agents,
        MAX(CASE WHEN SUBSTR(icd9_code, 1, 3) BETWEEN '510' AND '519' OR SUBSTR(icd10_code, 1, 3) BETWEEN 'J80' AND 'J99' THEN 1 ELSE 0 END) AS other_respiratory_diseases
    FROM diag
    GROUP BY hadm_id
),

-- Step 2: Filter for Cohort-Specific Patients and Extract Ventilation Status
cohort AS (
    SELECT
        a.hadm_id,
        a.ARDS,
        v.ventilation_status
    FROM `mimic-big-query.ards_dataset.ards-cohort-cleaned` a
    LEFT JOIN `physionet-data.mimiciv_derived.icustay_detail` icu ON a.hadm_id = icu.hadm_id
    LEFT JOIN `physionet-data.mimiciv_derived.ventilation` v ON icu.stay_id = v.stay_id
),

-- Step 3: Aggregate Ventilation Status and Join with Respiratory Illnesses
ventilation_status AS (
    SELECT
        c.hadm_id,
        c.ARDS,
        r.upper_respiratory_infections,
        r.influenza_pneumonia,
        r.acute_lower_respiratory_infections,
        r.chronic_lower_respiratory_diseases,
        r.lung_diseases_due_to_external_agents,
        r.other_respiratory_diseases,
        -- Moderate pre-existing conditions (1 or 2 conditions)
        CASE WHEN (r.upper_respiratory_infections + r.influenza_pneumonia + r.acute_lower_respiratory_infections +
                   r.chronic_lower_respiratory_diseases + r.lung_diseases_due_to_external_agents + r.other_respiratory_diseases) IN (1, 2)
             THEN 1 ELSE 0 END AS c_rsp_mod,
        -- Severe pre-existing conditions (3 or more conditions)
        CASE WHEN (r.upper_respiratory_infections + r.influenza_pneumonia + r.acute_lower_respiratory_infections +
                   r.chronic_lower_respiratory_diseases + r.lung_diseases_due_to_external_agents + r.other_respiratory_diseases) >= 3
             THEN 1 ELSE 0 END AS c_rsp_svr,
        MAX(CASE WHEN c.ventilation_status = 'InvasiveVent' THEN 1 ELSE 0 END) AS InvasiveVent,
        MAX(CASE WHEN c.ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS SupplementalOxygen,
        MAX(CASE WHEN c.ventilation_status = 'HFNC' THEN 1 ELSE 0 END) AS HFNC,
        MAX(CASE WHEN c.ventilation_status = 'NonInvasiveVent' THEN 1 ELSE 0 END) AS NonInvasiveVent,
        MAX(CASE WHEN c.ventilation_status = 'Tracheostomy' THEN 1 ELSE 0 END) AS Tracheostomy,
        MAX(CASE WHEN c.ventilation_status IS NULL OR c.ventilation_status = 'None' THEN 1 ELSE 0 END) AS None,
        MAX(CASE WHEN c.ventilation_status = 'SupplementalOxygen' THEN 1 ELSE 0 END) AS c_vent_low,
        MAX(CASE WHEN c.ventilation_status IN ('HFNC', 'NonInvasiveVent') THEN 1 ELSE 0 END) AS c_vent_moderate,
        MAX(CASE WHEN c.ventilation_status IN ('InvasiveVent', 'Tracheostomy') THEN 1 ELSE 0 END) AS c_vent_high
    FROM cohort c
    LEFT JOIN respiratory_illnesses r ON c.hadm_id = r.hadm_id
    GROUP BY
        c.hadm_id,
        c.ARDS,
        r.upper_respiratory_infections,
        r.influenza_pneumonia,
        r.acute_lower_respiratory_infections,
        r.chronic_lower_respiratory_diseases,
        r.lung_diseases_due_to_external_agents,
        r.other_respiratory_diseases
),

-- Step 4: Extract and Rank Data
ranked_data AS (
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
),

-- Step 5: Select and Aggregate Data
final_output AS (
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
        md.ARDS
),

-- Step 6: Join with Sepsis Status
final_with_sepsis AS (
    SELECT 
        fo.*,
        COALESCE(rd.sofa_score, 0) AS sofa_score,
        COALESCE(rd.suspected_infection, 0) AS suspected_infection,
        COALESCE(CAST(rd.sepsis3 AS INT64), 0) AS c_sepsis3
    FROM final_output fo
    LEFT JOIN (
        SELECT hadm_id,
               sofa_score,
               suspected_infection,
               sepsis3
        FROM s1
        WHERE rn_sus = 1
    ) AS rd ON fo.hadm_id = rd.hadm_id
),

-- Step 7: Extract Vasopressor Information
ards_cohort AS (
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
),

vasopressor_info AS (
    SELECT
        ards.hadm_id,
        ards.ARDS,
        meds.Dopamine,
        meds.Epinephrine,
        meds.Norepinephrine,
        meds.Vasopressin,
        meds.Phenylephrine,
        -- Calculate the new columns
        IF((meds.Dopamine + meds.Epinephrine + meds.Norepinephrine + meds.Vasopressin + meds.Phenylephrine) = 1, 1, 0) AS one_vasopressor,
        IF((meds.Dopamine + meds.Epinephrine + meds.Norepinephrine + meds.Vasopressin + meds.Phenylephrine) > 1, 1, 0) AS multi_vasopressor,
        IF((meds.Dopamine + meds.Epinephrine + meds.Norepinephrine + meds.Vasopressin + meds.Phenylephrine) > 0, 1, 0) AS c_shock
    FROM
        ards_cohort ards
    LEFT JOIN
        medications meds
    ON
        ards.hadm_id = meds.hadm_id
)

-- Final Selection of Data
SELECT
    fws.hadm_id,
    fws.ARDS,
    vs.upper_respiratory_infections,
    vs.influenza_pneumonia,
    vs.acute_lower_respiratory_infections,
    vs.chronic_lower_respiratory_diseases,
    vs.lung_diseases_due_to_external_agents,
    vs.other_respiratory_diseases,
    vs.InvasiveVent,
    vs.SupplementalOxygen,
    vs.HFNC,
    vs.NonInvasiveVent,
    vs.Tracheostomy,
    vs.None,
    vs.c_rsp_mod,
    vs.c_rsp_svr,
    vs.c_vent_low,
    vs.c_vent_moderate,
    vs.c_vent_high,
    fws.avg_cns,
    fws.avg_gcs_min,
    fws.max_cns,
    fws.max_cns_gcs_min,
    fws.avg_renal,
    fws.avg_uo_24hr,
    fws.avg_creatinine_max,
    fws.max_renal,
    fws.max_renal_uo_24hr,
    fws.max_renal_creatinine_max,
    fws.avg_respiration,
    fws.avg_pao2fio2ratio_novent,
    fws.avg_pao2fio2ratio_vent,
    fws.max_respiration,
    fws.max_respiration_pao2fio2ratio_novent,
    fws.max_respiration_pao2fio2ratio_vent,
    fws.c_max_renf_moderate,
    fws.c_max_renf_severe,
    fws.c_avg_renf_moderate,
    fws.c_avg_renf_severe,
    fws.c_max_respf_moderate,
    fws.c_max_respf_severe,
    fws.c_avg_respf_moderate,
    fws.c_avg_respf_severe,
    fws.c_max_cnsf_moderate,
    fws.c_max_cnsf_severe,
    fws.c_avg_cnsf_moderate,
    fws.c_avg_cnsf_severe,
    fws.sofa_score,
    fws.suspected_infection,
    fws.c_sepsis3,
    vi.Dopamine,
    vi.Epinephrine,
    vi.Norepinephrine,
    vi.Vasopressin,
    vi.Phenylephrine,
    vi.one_vasopressor,
    vi.multi_vasopressor,
    vi.c_shock
FROM
    final_with_sepsis fws
LEFT JOIN
    vasopressor_info vi
ON
    fws.hadm_id = vi.hadm_id
LEFT JOIN
    ventilation_status vs
ON
    fws.hadm_id = vs.hadm_id
ORDER BY
    fws.hadm_id;
