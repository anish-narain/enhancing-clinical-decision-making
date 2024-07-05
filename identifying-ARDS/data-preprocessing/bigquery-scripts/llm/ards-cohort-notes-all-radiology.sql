SELECT
    ards.hadm_id,
    radiology.note_id AS radiology_note_id,
    radiology.text AS radiology_text
FROM 
    `mimic-big-query.ards_dataset.ards-cohort-cleaned` ards
JOIN 
    `physionet-data.mimiciv_note.radiology` radiology
ON 
    ards.hadm_id = radiology.hadm_id
ORDER BY 
    ards.hadm_id;

-- 2020 of the hadm_id have radiology notes. Most of them have multiple notes, with 25 notes per hadm_id on average. There are 50597 radiology notes for the 2020 hadm_id's.

