SET FOREIGN_KEY_CHECKS = 0;

-- Clear any partial data
TRUNCATE TABLE engagement_data;

-- Import with DD/MM/YYYY date format
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Jan25.csv'
INTO TABLE engagement_data
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(UIN, @campaign_date, @email_open, @wa_read, @email_click, @wa_click, 
 @call_productive, @last_call_date, @call_duration, @extra1, @extra2, @extra3, @extra4)
SET 
    campaign_start_date = STR_TO_DATE(NULLIF(@campaign_date, ''), '%d/%m/%Y'),
    hcp_email_open_rate = NULLIF(@email_open, ''),
    hcp_whatsapp_read_rate = NULLIF(@wa_read, ''),
    hcp_email_click_rate = NULLIF(@email_click, ''),
    hcp_whatsapp_click_rate = NULLIF(@wa_click, ''),
    hcp_call_productive_rate = NULLIF(@call_productive, ''),
    last_call_connected_date = STR_TO_DATE(NULLIF(@last_call_date, ''), '%d/%m/%Y'),
    average_duration_connected_calls = NULLIF(@call_duration, '');

SET FOREIGN_KEY_CHECKS = 1;