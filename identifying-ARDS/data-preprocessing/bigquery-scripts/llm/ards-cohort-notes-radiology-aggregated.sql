SELECT
    ards.hadm_id,
    STRING_AGG(CAST(radiology.note_id AS STRING), ', ') AS radiology_note_ids,
    STRING_AGG(radiology.text, ' ||| ') AS radiology_texts
FROM 
    `mimic-big-query.ards_dataset.ards-cohort-cleaned` ards
JOIN 
    `physionet-data.mimiciv_note.radiology` radiology
ON 
    ards.hadm_id = radiology.hadm_id
GROUP BY 
    ards.hadm_id
ORDER BY 
    ards.hadm_id;

-- Concatenate all radiology_text values for each hadm_id, separated by ' ||| ', and all radiology_note_id values, separated by a comma and space.