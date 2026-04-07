-- 1. Check total records imported
SELECT COUNT(*) as total_records FROM engagement_data;

-- 2. See sample data
SELECT * FROM engagement_data LIMIT 10;

-- 3. Check UIN matching with doctors table
SELECT 
    COUNT(DISTINCT e.UIN) as unique_engagement_uins,
    COUNT(DISTINCT CASE WHEN d.UIN IS NOT NULL THEN e.UIN END) as matched_with_doctors,
    COUNT(DISTINCT CASE WHEN d.UIN IS NULL THEN e.UIN END) as unmatched_uins
FROM engagement_data e
LEFT JOIN doctors d ON e.UIN = d.UIN;

-- 4. See examples of unmatched UINs (if any)
SELECT DISTINCT e.UIN 
FROM engagement_data e
LEFT JOIN doctors d ON e.UIN = d.UIN
WHERE d.UIN IS NULL
LIMIT 20;

-- 5. Check data quality - engagement metrics
SELECT 
    COUNT(*) as total_records,
    AVG(hcp_email_open_rate) as avg_email_open,
    AVG(hcp_whatsapp_read_rate) as avg_whatsapp_read,
    AVG(hcp_call_productive_rate) as avg_call_productive,
    COUNT(DISTINCT UIN) as unique_doctors,
    MIN(campaign_start_date) as earliest_campaign,
    MAX(campaign_start_date) as latest_campaign
FROM engagement_data;