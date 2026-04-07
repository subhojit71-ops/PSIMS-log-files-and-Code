SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN (
        'clinics', 'education', 'academic_associations', 'associations',
        'awards', 'digital_presence', 'healthcare_platforms', 'clinical_trials',
        'publications', 'events', 'press_mentions'
    )
ORDER BY TABLE_NAME, ORDINAL_POSITION;