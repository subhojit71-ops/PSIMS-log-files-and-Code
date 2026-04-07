-- 1. PI (Doctors) - master table
CREATE TABLE doctors (
    UIN VARCHAR(50) PRIMARY KEY,
    MCI_no VARCHAR(50),
    MCI_state VARCHAR(100),
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    uin_specialty VARCHAR(100),
    specialty VARCHAR(255),
    subspeciality VARCHAR(255),
    qualification VARCHAR(255),
    years_of_exp INT,
    work_phone_1 VARCHAR(20),
    work_phone_2 VARCHAR(20),
    mobile VARCHAR(20),
    whatsapp_phone VARCHAR(20),
    email_id_1 VARCHAR(255),
    email_id_2 VARCHAR(255),
    biography TEXT,
    primary_institution VARCHAR(255),
    primary_department VARCHAR(255),
    primary_position VARCHAR(255),
    clinic_address TEXT,
    clinic_postal_code VARCHAR(20),
    dr_city VARCHAR(100),
    dr_state VARCHAR(100),
    dr_country VARCHAR(100),
    area_of_interest TEXT,
    hobbies TEXT
);

-- 2. Photos
CREATE TABLE photos (
    photo_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(255),
    photo_url text,
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 3. Clinics
CREATE TABLE clinics (
    clinic_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    clinic_name VARCHAR(255),
    address TEXT,
    postal_code VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 4. Education
CREATE TABLE education (
    edu_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    degree TEXT,
    city varchar(255),
    state VARCHAR(255),
    institution Text,
    year_of_completion INT,
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 5. Academic Association
CREATE TABLE academic_associations (
    assoc_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    association_name TEXT,
    role VARCHAR(255),
    year_started INT,
    year_ended INT,
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 6. Association
CREATE TABLE associations (
    assoc_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    association_name VARCHAR(255),
    role VARCHAR(255),
    year_started INT,
    year_ended INT,
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 7. Awards
CREATE TABLE awards (
    award_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    award_title VARCHAR(255),
    awarded_by VARCHAR(255),
    award_year INT,
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 8. Digital Presence
CREATE TABLE digital_presence (
    digital_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    platform VARCHAR(100),
    profile_link VARCHAR(255),
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 9. Healthcare Platforms
CREATE TABLE healthcare_platforms (
    platform_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    platform_name VARCHAR(255),
    profile_link VARCHAR(255),
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 10. Clinical Trials
CREATE TABLE clinical_trials (
    trial_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    trial_title VARCHAR(512),
    trial_year INT,
    role VARCHAR(255),
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 11. Publications
CREATE TABLE publications (
    pub_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    publication_title VARCHAR(255),
    journal_name VARCHAR(255),
    year_of_pub INT,
    doi VARCHAR(100),
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 12. Events
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    event_name VARCHAR(255),
    event_type VARCHAR(100),
    event_role varchar(512),
    event_year INT,
    role VARCHAR(255),
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);

-- 13. Press Mentions
CREATE TABLE press_mentions (
    press_id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(512),
    press_publication VARCHAR(255),
    press_release_title text,
    press_type VARCHAR(255),
    press_date DATE,
    
    FOREIGN KEY (UIN) REFERENCES doctors(UIN)
);




