CREATE TABLE persona_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL,
    
    -- 5 Core Persona Scores (0-100)
    academic_research_score DECIMAL(5,2) DEFAULT 0.00,
    patient_focused_score DECIMAL(5,2) DEFAULT 0.00,
    technology_focused_score DECIMAL(5,2) DEFAULT 0.00,
    recognition_focused_score DECIMAL(5,2) DEFAULT 0.00,
    community_focused_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Derived Persona Insights
    primary_persona VARCHAR(50),
    secondary_persona VARCHAR(50),
    persona_confidence_level ENUM('High', 'Medium', 'Low') DEFAULT 'Low',
    persona_clarity_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Calculation Metadata
    keyword_matches_found INT DEFAULT 0,
    text_fields_analyzed INT DEFAULT 0,
    data_quality_impact DECIMAL(5,2) DEFAULT 0.00,
    
    -- Timestamps
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key to your existing doctors table
    FOREIGN KEY (UIN) REFERENCES doctors(UIN) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_uin (UIN),
    INDEX idx_primary_persona (primary_persona),
    INDEX idx_academic_score (academic_research_score),
    INDEX idx_patient_score (patient_focused_score),
    INDEX idx_technology_score (technology_focused_score),
    INDEX idx_calculation_date (calculation_date),
    
    -- Ensure one record per UIN
    UNIQUE KEY unique_uin (UIN)
);