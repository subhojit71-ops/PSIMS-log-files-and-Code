CREATE TABLE authority_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL,
    
    -- 5 Core Authority Scores (0-100)
    research_authority_score DECIMAL(5,2) DEFAULT 0.00,
    digital_authority_score DECIMAL(5,2) DEFAULT 0.00,
    professional_network_score DECIMAL(5,2) DEFAULT 0.00,
    data_quality_score DECIMAL(5,2) DEFAULT 0.00,
    overall_influence_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Raw Authority Metrics (for scoring transparency)
    publication_count INT DEFAULT 0,
    award_count INT DEFAULT 0,
    trial_count INT DEFAULT 0,
    association_count INT DEFAULT 0,
    academic_affiliation_count INT DEFAULT 0,
    social_media_platforms INT DEFAULT 0,
    max_social_followers INT DEFAULT 0,
    healthcare_platform_count INT DEFAULT 0,
    years_of_experience INT DEFAULT 0,
    
    -- Scoring Methodology Metadata
    scoring_method_used VARCHAR(100) DEFAULT 'robust_dynamic',
    effective_min_values JSON,
    effective_max_values JSON,
    
    -- Data Quality Assessment
    profile_completeness DECIMAL(5,2) DEFAULT 0.00,
    data_accuracy_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Timestamps
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (UIN) REFERENCES doctors(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_research_authority (research_authority_score),
    INDEX idx_digital_authority (digital_authority_score),
    INDEX idx_overall_influence (overall_influence_score),
    
    UNIQUE KEY unique_uin (UIN)
);