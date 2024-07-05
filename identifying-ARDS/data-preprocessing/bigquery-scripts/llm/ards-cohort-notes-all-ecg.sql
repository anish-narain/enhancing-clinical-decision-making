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
)
SELECT
    ards_subjects.hadm_id,
    machine.study_id,
    machine.report_0,
    machine.report_1,
    machine.report_2,
    machine.report_3,
    machine.report_4,
    machine.report_5,
    machine.report_6,
    machine.report_7,
    machine.report_8,
    machine.report_9,
    machine.report_10,
    machine.report_11,
    machine.report_12,
    machine.report_13,
    machine.report_14,
    machine.report_15,
    machine.report_16,
    machine.report_17
FROM
    ards_subjects
JOIN
    `physionet-data.mimiciv_ecg.machine_measurements` machine
ON
    ards_subjects.subject_id = machine.subject_id
ORDER BY
    ards_subjects.hadm_id;


-- The ECG notes are identified by study_id. Each study_id can have up to 18 reports. For the ards cohort, there are 29,442 studies. The average number of reports per study_id is 3.45 and the average number of studies per hadm_id for the ards cohort is 11.79. In the end only 1881 patients have ecg reports recorded for them. 