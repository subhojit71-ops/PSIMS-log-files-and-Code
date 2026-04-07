-- SHOW VARIABLES LIKE 'max_allowed_packet';

-- =====================================================
-- CSV Import Commands for Healthcare Analytics Database
-- Place all CSV files in: C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\
-- =====================================================

-- Disable foreign key checks during import
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 1. CLINICS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Clinics.csv'
INTO TABLE clinics
CHARACTER SET latin1
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(UIN, @clinic_no, @clinic_name, @address, @city, @state, @postal_code, @clinic_type, 
 @clinic_department, @clinic_position, @url1, @url2, @url3, @ts1, @ts2, @ts3, @d1, @d2, @d3, @d4, @ts4, @ts5)
SET 
    clinic_name = NULLIF(@clinic_name, ''),
    address = NULLIF(@address, ''),
    postal_code = NULLIF(@postal_code, ''),
    city = NULLIF(@city, ''),
    state = NULLIF(@state, ''),
    country = 'India';  -- Default country

-- =====================================================
-- 2. EDUCATION
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Education.csv'
INTO TABLE education
CHARACTER SET latin1
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    UIN,
    @ed_institution_name, @ed_degree, @ed_passing_year, @ed_city, @ed_state, @dummy1, @dummy2, @dummy3, @dummy4, @dummy5, @dummy6, @dummy7, @dummy8, @dummy9, @dummy10, @dummy11, @dummy12, @dummy13
)
SET
    institution = NULLIF(@ed_institution_name, ''),
    degree = NULLIF(@ed_degree, ''),
    year_of_completion = NULLIF(@ed_passing_year, ''),
    city = NULLIF(@ed_city, ''),
    state = NULLIF(@ed_state, '');
    
-- =====================================================
-- 3. ACADEMIC ASSOCIATIONS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Academic Association.csv'
INTO TABLE academic_associations
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @assoc_name,
    @type,
    @dept,
    @position,
    @city,
    @state,
    @country,
    @postal,
    @from_date,
    @to_date,
    @assoc_type,
    @url1,
    @url2,
    @url3,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5,
    @rest
)
SET
    UIN = LEFT(TRIM(@UIN), 512),
    association_name = NULLIF(@assoc_name, ''),
    role = NULLIF(@position, ''),
    year_started = IFNULL(YEAR(STR_TO_DATE(NULLIF(@from_date, ''), '%Y-%m-%d')), NULL),
    year_ended = IFNULL(YEAR(STR_TO_DATE(NULLIF(@to_date, ''), '%Y-%m-%d')), NULL);



-- =====================================================
-- 4. ASSOCIATIONS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Association.csv'
INTO TABLE associations
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @assoc_name,
    @type,
    @dept,
    @position,
    @city,
    @state,
    @country,
    @postal,
    @from_date,
    @to_date,
    @level,
    @url1,
    @url2,
    @url3,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5,
    @rest
)
SET
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 255),
    association_name = NULLIF(@assoc_name, ''),
    role = NULLIF(@position, ''),
    year_started = IFNULL(YEAR(STR_TO_DATE(NULLIF(@from_date, ''), '%Y-%m-%d')), NULL),
    year_ended = IFNULL(YEAR(STR_TO_DATE(NULLIF(@to_date, ''), '%Y-%m-%d')), NULL);


-- =====================================================
-- 5. AWARDS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Awards.csv'
INTO TABLE awards
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @award_name,
    @awarded_by,
    @year,
    @country,
    @level,
    @url1,
    @url2,
    @url3,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5,
    @rest
)
SET
    -- Remove hidden characters and enforce max length
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 255),
    award_title = NULLIF(@award_name, ''),
    awarded_by = NULLIF(@awarded_by, ''),
    award_year = NULLIF(@year, '');

-- =====================================================
-- 6. DIGITAL PRESENCE
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Digital.csv'
INTO TABLE digital_presence
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @channel,
    @page_url,
    @followers,
    @post_url,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5,
    @rest
)
SET
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 255),
    platform = NULLIF(@channel, ''),
    profile_link = NULLIF(@page_url, ''),
    sm_followers = NULLIF(@followers, '');

-- =====================================================
-- 7. HEALTHCARE PLATFORMS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Healthcare_platforms.csv'
INTO TABLE healthcare_platforms
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @platform,
    @page_url,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5,
    @rest
)
SET
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 255),
    platform_name = NULLIF(@platform, ''),
    profile_link = NULLIF(@page_url, '');


-- =====================================================
-- 8. CLINICAL TRIALS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Trials.csv'
INTO TABLE clinical_trials
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @role,
    @trial_id,
    @public_title,
    @sci_title,
    @phase,
    @status,
    @type,
    @start,
    @end,
    @countries,
    @sponsors,
    @intervention,
    @indication,
    @co_inv,
    @desc,
    @link,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5,
    @rest
)
SET
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 512),
    trial_title = NULLIF(@public_title, ''),
    trial_year = IFNULL(YEAR(STR_TO_DATE(NULLIF(@start, ''), '%Y-%m-%d')), NULL),
    role = NULLIF(@role, '');



-- =====================================================
-- 9. PUBLICATIONS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Publications.csv'
INTO TABLE publications
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @h_index,
    @journal,
    @pub_type,
    @pub_name,
    @pub_id,
    @title,
    @date,
    @indication,
    @mesh,
    @coauthors,
    @affiliation,
    @abstract,
    @eigenfactor,
    @indexed,
    @citations,
    @link,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5
)
SET
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 512),
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 512),
    publication_title = LEFT(NULLIF(@title, ''), 255),
    journal_name = LEFT(NULLIF(@journal, ''), 255),
    year_of_pub = IFNULL(YEAR(STR_TO_DATE(NULLIF(@date, ''), '%Y-%m-%d')), NULL),
    doi = NULLIF(@pub_id, '');


-- =====================================================
-- 10. EVENTS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Events.csv'
INTO TABLE events
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
    @UIN,
    @event_name,
    @topic,
    @keywords,
    @type,
    @role,
    @start,
    @end,
    @participants,
    @part_role,
    @sponsor,
    @location,
    @city,
    @country,
    @link,
    @ts1,
    @ts2,
    @ts3,
    @d1,
    @d2,
    @d3,
    @d4,
    @ts4,
    @ts5
)
SET
    UIN = LEFT(TRIM(REPLACE(REPLACE(REPLACE(@UIN, '\r', ''), '\n', ''), '\t', '')), 255),
    event_name = LEFT(NULLIF(@event_name, ''), 255),
    event_type = LEFT(NULLIF(@type, ''), 255),
    event_year = IFNULL(YEAR(STR_TO_DATE(NULLIF(@start, ''), '%Y-%m-%d')), NULL),
    role = LEFT(NULLIF(@role, ''), 255);


-- =====================================================
-- 11. PRESS MENTIONS
-- =====================================================
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Press.csv'
INTO TABLE press_mentions
CHARACTER SET latin1
FIELDS TERMINATED BY '\t'
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(
	@UIN,
    @press_publication,
	@press_release_title,
    @press_type,
	@press_keywords
	
)
SET
    UIN = LEFT(TRIM(@UIN), 512),
    press_release_title= TRIM(@press_release_title),


    
    press_date = CASE
                     WHEN @press_date REGEXP '^[0-9]{2,4}/[0-9]{2}/[0-9]{2,4}$'
                     THEN STR_TO_DATE(@press_date, '%d/%m/%Y')
                     ELSE NULL
                 END;




-- =====================================================
-- VALIDATION QUERIES - Run after import
-- =====================================================

-- Check record counts
SELECT 'clinics' as table_name, COUNT(*) as records FROM clinics
UNION ALL SELECT 'education', COUNT(*) FROM education
UNION ALL SELECT 'academic_associations', COUNT(*) FROM academic_associations
UNION ALL SELECT 'associations', COUNT(*) FROM associations
UNION ALL SELECT 'awards', COUNT(*) FROM awards
UNION ALL SELECT 'digital_presence', COUNT(*) FROM digital_presence
UNION ALL SELECT 'healthcare_platforms', COUNT(*) FROM healthcare_platforms
UNION ALL SELECT 'clinical_trials', COUNT(*) FROM clinical_trials
UNION ALL SELECT 'publications', COUNT(*) FROM publications
UNION ALL SELECT 'events', COUNT(*) FROM events
UNION ALL SELECT 'press_mentions', COUNT(*) FROM press_mentions;

-- Check unique doctors per table
SELECT 'clinics' as table_name, COUNT(DISTINCT UIN) as unique_doctors FROM clinics
UNION ALL SELECT 'education', COUNT(DISTINCT UIN) FROM education
UNION ALL SELECT 'academic_associations', COUNT(DISTINCT UIN) FROM academic_associations
UNION ALL SELECT 'associations', COUNT(DISTINCT UIN) FROM associations
UNION ALL SELECT 'awards', COUNT(DISTINCT UIN) FROM awards
UNION ALL SELECT 'digital_presence', COUNT(DISTINCT UIN) FROM digital_presence
UNION ALL SELECT 'healthcare_platforms', COUNT(DISTINCT UIN) FROM healthcare_platforms
UNION ALL SELECT 'clinical_trials', COUNT(DISTINCT UIN) FROM clinical_trials
UNION ALL SELECT 'publications', COUNT(DISTINCT UIN) FROM publications
UNION ALL SELECT 'events', COUNT(DISTINCT UIN) FROM events
UNION ALL SELECT 'press_mentions', COUNT(DISTINCT UIN) FROM press_mentions;

-- Find sample data for testing
SELECT 
    d.UIN,
    d.full_name,
    (SELECT COUNT(*) FROM publications WHERE UIN = d.UIN) as pubs,
    (SELECT COUNT(*) FROM clinical_trials WHERE UIN = d.UIN) as trials,
    (SELECT COUNT(*) FROM events WHERE UIN = d.UIN) as events,
    (SELECT COUNT(*) FROM awards WHERE UIN = d.UIN) as awards,
    (SELECT COUNT(*) FROM digital_presence WHERE UIN = d.UIN) as digital
FROM doctors d
WHERE d.UIN IN (SELECT DISTINCT UIN FROM engagement_data)
HAVING (pubs + trials + events + awards + digital) > 5
ORDER BY (pubs + trials + events + awards + digital) DESC
LIMIT 20;