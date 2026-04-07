SELECT 
    COUNT(DISTINCT e.UIN) as unique_engagement_uins,
    COUNT(DISTINCT CASE WHEN d.UIN IS NOT NULL THEN e.UIN END) as matched_with_doctors,
    COUNT(DISTINCT CASE WHEN d.UIN IS NULL THEN e.UIN END) as unmatched_uins
FROM engagement_data e
LEFT JOIN doctors d ON e.UIN = d.UIN;