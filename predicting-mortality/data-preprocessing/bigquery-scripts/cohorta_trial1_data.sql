WITH SingleICUStayPatients AS (
    SELECT ie.subject_id
    FROM `physionet-data.mimiciv_icu.icustays` ie
    GROUP BY ie.subject_id
    HAVING COUNT(ie.subject_id) = 1
),


FilteredPatients AS (
    SELECT ie.subject_id, ie.hadm_id, ie.stay_id, pat.dod,
           IF(pat.dod IS NOT NULL, 1, 0) AS mortality_year
    FROM `physionet-data.mimiciv_icu.icustays` ie
    INNER JOIN `physionet-data.mimiciv_hosp.admissions` adm ON ie.hadm_id = adm.hadm_id
    INNER JOIN `physionet-data.mimiciv_hosp.patients` pat ON ie.subject_id = pat.subject_id
    INNER JOIN SingleICUStayPatients s ON ie.subject_id = s.subject_id
    WHERE (pat.anchor_age + DATETIME_DIFF(adm.admittime, DATETIME(pat.anchor_year, 1, 1, 0, 0, 0), YEAR)) BETWEEN 18 AND 90
      AND ROUND(CAST(DATETIME_DIFF(ie.outtime, ie.intime, HOUR) / 24.0 AS NUMERIC), 2) <= 2
),

-- Variables used in SOFA:
--  GCS, MAP, FiO2, Ventilation status (sourced from CHARTEVENTS)
--  Creatinine, Bilirubin, FiO2, PaO2, Platelets (sourced from LABEVENTS)
--  Dopamine, Dobutamine, Epinephrine, Norepinephrine (sourced from INPUTEVENTS)
--  Urine output (sourced from OUTPUTEVENTS)

-- The following views required to run this query:
--  1) first_day_urine_output
--  2) first_day_vitalsign
--  3) first_day_gcs
--  4) first_day_lab
--  5) first_day_bg_art
--  6) ventdurations

-- extract drug rates from derived vasopressor tables
vaso_stg AS (
    SELECT ie.stay_id, 'norepinephrine' AS treatment, vaso_rate AS rate
    FROM `physionet-data.mimiciv_icu.icustays` ie
    INNER JOIN `physionet-data.mimiciv_derived.norepinephrine` mv
        ON ie.stay_id = mv.stay_id
            AND mv.starttime >= DATETIME_SUB(ie.intime, INTERVAL '6' HOUR)
            AND mv.starttime <= DATETIME_ADD(ie.intime, INTERVAL '1' DAY)
    UNION ALL
    SELECT ie.stay_id, 'epinephrine' AS treatment, vaso_rate AS rate
    FROM `physionet-data.mimiciv_icu.icustays` ie
    INNER JOIN `physionet-data.mimiciv_derived.epinephrine` mv
        ON ie.stay_id = mv.stay_id
            AND mv.starttime >= DATETIME_SUB(ie.intime, INTERVAL '6' HOUR)
            AND mv.starttime <= DATETIME_ADD(ie.intime, INTERVAL '1' DAY)
    UNION ALL
    SELECT ie.stay_id, 'dobutamine' AS treatment, vaso_rate AS rate
    FROM `physionet-data.mimiciv_icu.icustays` ie
    INNER JOIN `physionet-data.mimiciv_derived.dobutamine` mv
        ON ie.stay_id = mv.stay_id
            AND mv.starttime >= DATETIME_SUB(ie.intime, INTERVAL '6' HOUR)
            AND mv.starttime <= DATETIME_ADD(ie.intime, INTERVAL '1' DAY)
    UNION ALL
    SELECT ie.stay_id, 'dopamine' AS treatment, vaso_rate AS rate
    FROM `physionet-data.mimiciv_icu.icustays` ie
    INNER JOIN `physionet-data.mimiciv_derived.dopamine` mv
        ON ie.stay_id = mv.stay_id
            AND mv.starttime >= DATETIME_SUB(ie.intime, INTERVAL '6' HOUR)
            AND mv.starttime <= DATETIME_ADD(ie.intime, INTERVAL '1' DAY)
)

, vaso_mv AS (
    SELECT
        ie.stay_id
        , MAX(
            CASE WHEN treatment = 'norepinephrine' THEN rate ELSE NULL END
        ) AS rate_norepinephrine
        , MAX(
            CASE WHEN treatment = 'epinephrine' THEN rate ELSE NULL END
        ) AS rate_epinephrine
        , MAX(
            CASE WHEN treatment = 'dopamine' THEN rate ELSE NULL END
        ) AS rate_dopamine
        , MAX(
            CASE WHEN treatment = 'dobutamine' THEN rate ELSE NULL END
        ) AS rate_dobutamine
    FROM `physionet-data.mimiciv_icu.icustays` ie
    LEFT JOIN vaso_stg v
        ON ie.stay_id = v.stay_id
    GROUP BY ie.stay_id
)

, pafi1 AS (
    -- join blood gas to ventilation durations to determine if patient was vent
    SELECT ie.stay_id, bg.charttime
        , bg.pao2fio2ratio
        , CASE WHEN vd.stay_id IS NOT NULL THEN 1 ELSE 0 END AS isvent
    FROM `physionet-data.mimiciv_icu.icustays` ie
    LEFT JOIN `physionet-data.mimiciv_derived.bg` bg
        ON ie.subject_id = bg.subject_id
            AND bg.charttime >= DATETIME_SUB(ie.intime, INTERVAL '6' HOUR)
            AND bg.charttime <= DATETIME_ADD(ie.intime, INTERVAL '1' DAY)
    LEFT JOIN `physionet-data.mimiciv_derived.ventilation` vd
        ON ie.stay_id = vd.stay_id
            AND bg.charttime >= vd.starttime
            AND bg.charttime <= vd.endtime
            AND vd.ventilation_status = 'InvasiveVent'
)

, pafi2 AS (
    -- because pafi has an interaction between vent/PaO2:FiO2,
    -- we need two columns for the score
    -- it can happen that the lowest unventilated PaO2/FiO2 is 68, 
    -- but the lowest ventilated PaO2/FiO2 is 120
    -- in this case, the SOFA score is 3, *not* 4.
    SELECT stay_id
        , MIN(
            CASE WHEN isvent = 0 THEN pao2fio2ratio ELSE NULL END
        ) AS pao2fio2_novent_min
        , MIN(
            CASE WHEN isvent = 1 THEN pao2fio2ratio ELSE NULL END
        ) AS pao2fio2_vent_min
    FROM pafi1
    GROUP BY stay_id
)

, chem AS (
    SELECT
        ie.stay_id,
        MAX(aniongap) AS aniongap_max,
        MIN(albumin) AS albumin_min,
        MAX(albumin) AS albumin_max,
    FROM `physionet-data.mimiciv_icu.icustays` ie
    LEFT JOIN `physionet-data.mimiciv_derived.chemistry` le
        ON le.subject_id = ie.subject_id
            AND le.charttime >= DATETIME_SUB(ie.intime, INTERVAL '6' HOUR)
            AND le.charttime <= DATETIME_ADD(ie.intime, INTERVAL '1' DAY)
    GROUP BY ie.stay_id
)

-- Aggregate the components for the score
, scorecomp AS (
    SELECT ie.stay_id
        , v.mbp_min
        , mv.rate_norepinephrine
        , mv.rate_epinephrine
        , mv.rate_dopamine
        , mv.rate_dobutamine

        , l.creatinine_max
        , l.bilirubin_total_max AS bilirubin_max
        , l.platelets_min AS platelet_min

        , pf.pao2fio2_novent_min
        , pf.pao2fio2_vent_min

        , uo.urineoutput

        , gcs.gcs_min

        , ch.aniongap_max
        , ch.albumin_min
        , ch.albumin_max

        , CASE WHEN ch.aniongap_max > 12 THEN 1 ELSE 0 END AS flag_high_aniongap
        , CASE WHEN ch.albumin_min < 3.4 THEN 1 ELSE 0 END AS flag_low_albumin
        , CASE WHEN ch.albumin_max > 5.4 THEN 1 ELSE 0 END AS flag_high_albumin
        , CASE WHEN l.bilirubin_total_max > 1.2 THEN 1 ELSE 0 END AS flag_high_bilirubin
    FROM `physionet-data.mimiciv_icu.icustays` ie
    LEFT JOIN vaso_mv mv
        ON ie.stay_id = mv.stay_id
    LEFT JOIN pafi2 pf
        ON ie.stay_id = pf.stay_id
    LEFT JOIN `physionet-data.mimiciv_derived.first_day_vitalsign` v
        ON ie.stay_id = v.stay_id
    LEFT JOIN `physionet-data.mimiciv_derived.first_day_lab` l
        ON ie.stay_id = l.stay_id
    LEFT JOIN `physionet-data.mimiciv_derived.first_day_urine_output` uo
        ON ie.stay_id = uo.stay_id
    LEFT JOIN `physionet-data.mimiciv_derived.first_day_gcs` gcs
        ON ie.stay_id = gcs.stay_id
    LEFT JOIN chem ch ON ie.stay_id = ch.stay_id
)

, scorecalc AS (
    -- Calculate the final score
    -- note that if the underlying data is missing, the component is 0
    SELECT stay_id
        -- Respiration
        , CASE
            WHEN pao2fio2_vent_min < 100 THEN 4
            WHEN pao2fio2_vent_min < 200 THEN 3
            WHEN pao2fio2_novent_min < 300 THEN 2
            WHEN pao2fio2_novent_min < 400 THEN 1
            WHEN
                COALESCE(
                    pao2fio2_vent_min, pao2fio2_novent_min
                ) IS NULL THEN 0
            ELSE 0
        END AS respiration

        -- Coagulation
        , CASE
            WHEN platelet_min < 20 THEN 4
            WHEN platelet_min < 50 THEN 3
            WHEN platelet_min < 100 THEN 2
            WHEN platelet_min < 150 THEN 1
            WHEN platelet_min IS NULL THEN 0
            ELSE 0
        END AS coagulation

        -- Liver
        , CASE
            -- Bilirubin checks in mg/dL
            WHEN bilirubin_max >= 12.0 THEN 4
            WHEN bilirubin_max >= 6.0 THEN 3
            WHEN bilirubin_max >= 2.0 THEN 2
            WHEN bilirubin_max >= 1.2 THEN 1
            WHEN bilirubin_max IS NULL THEN 0
            ELSE 0
        END AS liver

        -- Cardiovascular
        , CASE
            WHEN rate_dopamine > 15
                OR rate_epinephrine > 0.1
                OR rate_norepinephrine > 0.1
                THEN 4
            WHEN rate_dopamine > 5
                OR rate_epinephrine <= 0.1
                OR rate_norepinephrine <= 0.1
                THEN 3
            WHEN rate_dopamine > 0 OR rate_dobutamine > 0 THEN 2
            WHEN mbp_min < 70 THEN 1
            WHEN
                COALESCE(
                    mbp_min
                    , rate_dopamine
                    , rate_dobutamine
                    , rate_epinephrine
                    , rate_norepinephrine
                ) IS NULL THEN 0
            ELSE 0
        END AS cardiovascular

        -- Neurological failure (GCS)
        , CASE
            WHEN (gcs_min >= 13 AND gcs_min <= 14) THEN 1
            WHEN (gcs_min >= 10 AND gcs_min <= 12) THEN 2
            WHEN (gcs_min >= 6 AND gcs_min <= 9) THEN 3
            WHEN gcs_min < 6 THEN 4
            WHEN gcs_min IS NULL THEN 0
            ELSE 0 END
        AS cns

        -- Renal failure - high creatinine or low urine output
        , CASE
            WHEN (creatinine_max >= 5.0) THEN 4
            WHEN urineoutput < 200 THEN 4
            WHEN (creatinine_max >= 3.5 AND creatinine_max < 5.0) THEN 3
            WHEN urineoutput < 500 THEN 3
            WHEN (creatinine_max >= 2.0 AND creatinine_max < 3.5) THEN 2
            WHEN (creatinine_max >= 1.2 AND creatinine_max < 2.0) THEN 1
            WHEN COALESCE(urineoutput, creatinine_max) IS NULL THEN 0
            ELSE 0 END
        AS renal
    FROM scorecomp
)

, condition_flags AS (
    SELECT stay_id
        , CASE WHEN cardiovascular >= 3 AND (respiration >= 2 OR coagulation >= 2 OR liver >= 2 OR cns >= 2 OR renal >= 2) THEN 1 ELSE 0 END AS SSH
        , CASE WHEN respiration >= 3 AND cardiovascular >= 1 AND cns >= 2 THEN 1 ELSE 0 END AS ARD
        , CASE WHEN liver >= 2 AND renal >= 2 THEN 1 ELSE 0 END AS HES
        , CASE WHEN coagulation >= 3 AND liver >= 2 THEN 1 ELSE 0 END AS COD
        , CASE WHEN (respiration >= 2 AND cardiovascular >= 2 AND cns >= 2) OR (respiration >= 2 AND liver >= 2 AND renal >= 2) OR (cardiovascular >= 2 AND liver >= 2 AND coagulation >= 2) THEN 1 ELSE 0 END AS MOD
        , CASE WHEN cns >= 3 AND renal >= 2 THEN 1 ELSE 0 END AS CRF
        , CASE WHEN liver >= 3 AND coagulation >= 3 THEN 1 ELSE 0 END AS LCF
        -- Moderate and severe flags for each organ system
        , CASE WHEN respiration BETWEEN 1 AND 3 THEN 1 ELSE 0 END AS rsp_fail_moderate,
        CASE WHEN respiration = 4 THEN 1 ELSE 0 END AS rsp_fail_severe,
        CASE WHEN coagulation BETWEEN 1 AND 3 THEN 1 ELSE 0 END AS cgn_fail_moderate,
        CASE WHEN coagulation = 4 THEN 1 ELSE 0 END AS cgn_fail_severe,
        CASE WHEN liver BETWEEN 1 AND 3 THEN 1 ELSE 0 END AS lvr_fail_moderate,
        CASE WHEN liver = 4 THEN 1 ELSE 0 END AS lvr_fail_severe,
        CASE WHEN cardiovascular BETWEEN 1 AND 3 THEN 1 ELSE 0 END AS cdv_fail_moderate,
        CASE WHEN cardiovascular = 4 THEN 1 ELSE 0 END AS cdv_fail_severe,
        CASE WHEN cns BETWEEN 1 AND 3 THEN 1 ELSE 0 END AS gcs_fail_moderate,
        CASE WHEN cns = 4 THEN 1 ELSE 0 END AS gcs_fail_severe,
        CASE WHEN renal BETWEEN 1 AND 3 THEN 1 ELSE 0 END AS rfl_fail_moderate,
        CASE WHEN renal = 4 THEN 1 ELSE 0 END AS rfl_fail_severe
    FROM scorecalc
)



SELECT 
    fp.subject_id, 
    fp.hadm_id, 
    fp.stay_id, 
    fp.dod, 
    fp.mortality_year,
    sc.aniongap_max,
    sc.albumin_min,
    sc.albumin_max,
    sc.pao2fio2_vent_min AS rsp_pao2fio2_vent_min,
    sc.pao2fio2_novent_min AS rsp_pao2fio2_novent_min,
    sc.platelet_min AS cgn_platelet_min,
    sc.bilirubin_max AS lvr_bilirubin_max,
    sc.mbp_min AS cdv_mbp_min,
    sc.rate_dopamine AS cdv_rate_dopamine,
    sc.rate_dobutamine AS cdv_rate_dobutamine,
    sc.rate_epinephrine AS cdv_rate_epinephrine,
    sc.rate_norepinephrine AS cdv_rate_norepinephrine,
    sc.gcs_min AS gcs_min,
    sc.urineoutput AS rfl_urineoutput,
    sc.creatinine_max AS rfl_creatinine_max,
    COALESCE(respiration, 0) + COALESCE(coagulation, 0) + COALESCE(liver, 0) + COALESCE(cardiovascular, 0) + COALESCE(cns, 0) + COALESCE(renal, 0) AS sofa,
    respiration, 
    coagulation, 
    liver, 
    cardiovascular, 
    cns, 
    renal,
    -- Include moderate and severe failure flags
    cf.rsp_fail_moderate,
    cf.rsp_fail_severe,
    cf.cgn_fail_moderate,
    cf.cgn_fail_severe,
    cf.lvr_fail_moderate,
    cf.lvr_fail_severe,
    cf.cdv_fail_moderate,
    cf.cdv_fail_severe,
    cf.gcs_fail_moderate,
    cf.gcs_fail_severe,
    cf.rfl_fail_moderate,
    cf.rfl_fail_severe,
    cf.SSH, 
    cf.ARD, 
    cf.HES, 
    cf.COD, 
    cf.MOD, 
    cf.CRF, 
    cf.LCF,
    sc.flag_high_aniongap,
    sc.flag_low_albumin,
    sc.flag_high_albumin,
    sc.flag_high_bilirubin
FROM 
    FilteredPatients fp
LEFT JOIN 
    scorecalc s ON fp.stay_id = s.stay_id
LEFT JOIN 
    condition_flags cf ON s.stay_id = cf.stay_id
LEFT JOIN 
    scorecomp sc ON s.stay_id = sc.stay_id;