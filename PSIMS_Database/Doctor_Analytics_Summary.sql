CREATE TABLE doctor_analytics_summary (
    UIN VARCHAR(255) PRIMARY KEY,
    
    -- Basic Doctor Information
    full_name VARCHAR(200),
    specialty VARCHAR(200),
    subspeciality VARCHAR(200),
    dr_city VARCHAR(100),
    dr_state VARCHAR(100),
    years_of_experience INT,
    
    -- Tier 1: Persona Scores (5 scores)
    academic_score DECIMAL(5,2) DEFAULT 0.00,
    patient_score DECIMAL(5,2) DEFAULT 0.00,
    technology_score DECIMAL(5,2) DEFAULT 0.00,
    recognition_score DECIMAL(5,2) DEFAULT 0.00,
    community_score DECIMAL(5,2) DEFAULT 0.00,
    primary_persona VARCHAR(50),
    secondary_persona VARCHAR(50),
    
    -- Tier 2: Engagement Scores (4 scores)  
    email_engagement DECIMAL(5,2) DEFAULT 0.00,
    whatsapp_engagement DECIMAL(5,2) DEFAULT 0.00,
    call_performance DECIMAL(5,2) DEFAULT 0.00,
    overall_responsiveness DECIMAL(5,2) DEFAULT 0.00,
    preferred_channel VARCHAR(20),
    
    -- Tier 3: Authority Scores (5 scores)
    research_authority DECIMAL(5,2) DEFAULT 0.00,
    digital_authority DECIMAL(5,2) DEFAULT 0.00,
    professional_network DECIMAL(5,2) DEFAULT 0.00,
    data_quality DECIMAL(5,2) DEFAULT 0.00,
    overall_influence DECIMAL(5,2) DEFAULT 0.00,
    
    -- Current Cluster Assignment
    current_cluster_id INT,
    current_cluster_name VARCHAR(200),
    
    -- Timestamps
    scores_last_calculated TIMESTAMP NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_specialty (specialty),
    INDEX idx_location (dr_city, dr_state),
    INDEX idx_primary_persona (primary_persona),
    INDEX idx_overall_responsiveness (overall_responsiveness),
    INDEX idx_overall_influence (overall_influence),
    
    FOREIGN KEY (UIN) REFERENCES doctors(UIN) ON DELETE CASCADE
);