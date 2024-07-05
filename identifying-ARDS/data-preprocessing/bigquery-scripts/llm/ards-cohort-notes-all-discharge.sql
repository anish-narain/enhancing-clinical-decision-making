SELECT
    ards.hadm_id,
    discharge.note_id AS discharge_note_id,
    discharge.text AS discharge_text
FROM 
    `mimic-big-query.ards_dataset.ards-cohort-cleaned` ards
JOIN 
    `physionet-data.mimiciv_note.discharge` discharge
ON 
    ards.hadm_id = discharge.hadm_id
ORDER BY 
    ards.hadm_id;

-- returns 2021 results, one summary for each of the hadm_id