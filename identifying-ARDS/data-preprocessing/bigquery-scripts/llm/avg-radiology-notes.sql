WITH radiology_counts AS (
    SELECT
        ards.hadm_id,
        COUNT(radiology.note_id) AS radiology_note_count
    FROM 
        `mimic-big-query.ards_dataset.ards-cohort-cleaned` ards
    JOIN 
        `physionet-data.mimiciv_note.radiology` radiology
    ON 
        ards.hadm_id = radiology.hadm_id
    GROUP BY 
        ards.hadm_id
)
SELECT
    AVG(radiology_note_count) AS avg_radiology_notes_per_hadm_id
FROM 
    radiology_counts;
