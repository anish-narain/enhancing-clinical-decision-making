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
aggregated_reports AS (
    SELECT
        ards_subjects.hadm_id,
        machine.study_id,
        CONCAT(
            IFNULL(machine.report_0, ''), ' ',
            IFNULL(machine.report_1, ''), ' ',
            IFNULL(machine.report_2, ''), ' ',
            IFNULL(machine.report_3, ''), ' ',
            IFNULL(machine.report_4, ''), ' ',
            IFNULL(machine.report_5, ''), ' ',
            IFNULL(machine.report_6, ''), ' ',
            IFNULL(machine.report_7, ''), ' ',
            IFNULL(machine.report_8, ''), ' ',
            IFNULL(machine.report_9, ''), ' ',
            IFNULL(machine.report_10, ''), ' ',
            IFNULL(machine.report_11, ''), ' ',
            IFNULL(machine.report_12, ''), ' ',
            IFNULL(machine.report_13, ''), ' ',
            IFNULL(machine.report_14, ''), ' ',
            IFNULL(machine.report_15, ''), ' ',
            IFNULL(machine.report_16, ''), ' ',
            IFNULL(machine.report_17, '')
        ) AS report_text
    FROM
        ards_subjects
    JOIN
        `physionet-data.mimiciv_ecg.machine_measurements` machine
    ON
        ards_subjects.subject_id = machine.subject_id
)
SELECT
    hadm_id,
    STRING_AGG(DISTINCT CAST(study_id AS STRING), ', ') AS study_ids,
    STRING_AGG(report_text, ' ||| ') AS combined_reports
FROM
    aggregated_reports
GROUP BY
    hadm_id
ORDER BY
    hadm_id;
