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
note_data AS (
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
)
SELECT
    COUNT(report_0) AS report_0_count,
    COUNT(report_1) AS report_1_count,
    COUNT(report_2) AS report_2_count,
    COUNT(report_3) AS report_3_count,
    COUNT(report_4) AS report_4_count,
    COUNT(report_5) AS report_5_count,
    COUNT(report_6) AS report_6_count,
    COUNT(report_7) AS report_7_count,
    COUNT(report_8) AS report_8_count,
    COUNT(report_9) AS report_9_count,
    COUNT(report_10) AS report_10_count,
    COUNT(report_11) AS report_11_count,
    COUNT(report_12) AS report_12_count,
    COUNT(report_13) AS report_13_count,
    COUNT(report_14) AS report_14_count,
    COUNT(report_15) AS report_15_count,
    COUNT(report_16) AS report_16_count,
    COUNT(report_17) AS report_17_count
FROM
    note_data;

/*
[
    1,        # report_0_count
    29442,    # report_1_count
    25640,    # report_2_count
    21134,    # report_3_count
    17702,    # report_4_count
    11838,    # report_5_count
    7076,     # report_6_count
    3544,     # report_7_count
    1612,     # report_8_count
    554,      # report_9_count
    190,      # report_10_count
    65,       # report_11_count
    27,       # report_12_count
    9,        # report_13_count
    9,        # report_14_count
    1,        # report_15_count
    1,        # report_16_count
    1,        # report_17_count
    0         # report_18_count
]
*/