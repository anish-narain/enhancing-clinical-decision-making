WITH ards_subjects AS (
    SELECT
        ards.hadm_id,
        icu.subject_id
    FROM
        `mimic-big-query.ards_dataset.ards-cohort-cleaned` ards
    JOIN
        `physionet-data.mimiciv_derived.icustay_detail` icu
    ON
        ards.hadm_id = icu.hadm_id
),
study_count_per_hadm AS (
    SELECT
        ards_subjects.hadm_id,
        COUNT(DISTINCT machine.study_id) AS study_count
    FROM
        ards_subjects
    JOIN
        `physionet-data.mimiciv_ecg.machine_measurements` machine
    ON
        ards_subjects.subject_id = machine.subject_id
    GROUP BY
        ards_subjects.hadm_id
),
non_null_reports_per_study AS (
    SELECT
        machine.study_id,
        (
            CASE WHEN machine.report_0 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_1 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_2 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_3 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_4 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_5 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_6 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_7 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_8 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_9 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_10 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_11 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_12 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_13 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_14 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_15 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_16 IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN machine.report_17 IS NOT NULL THEN 1 ELSE 0 END
        ) AS non_null_report_count
    FROM
        `physionet-data.mimiciv_ecg.machine_measurements` machine
)
SELECT
    AVG(study_count_per_hadm.study_count) AS avg_study_count_per_hadm_id,
    AVG(non_null_reports_per_study.non_null_report_count) AS avg_non_null_reports_per_study_id
FROM
    study_count_per_hadm,
    non_null_reports_per_study;
