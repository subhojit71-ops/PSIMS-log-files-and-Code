-- =====================================================
-- Healthcare Professional Analytics Database Schema
-- 3-Tier Scoring System with K-Means Clustering
-- =====================================================

-- =====================================================
-- TIER 1: PERSONA SCORES TABLE
-- =====================================================
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
    
    -- Indexes
    FOREIGN KEY (UIN) REFERENCES doctors_pi(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_primary_persona (primary_persona),
    INDEX idx_academic_score (academic_research_score),
    INDEX idx_patient_score (patient_focused_score),
    INDEX idx_technology_score (technology_focused_score),
    INDEX idx_calculation_date (calculation_date),
    
    -- Ensure one record per UIN
    UNIQUE KEY unique_uin (UIN)
);

-- =====================================================
-- TIER 2: ENGAGEMENT SCORES TABLE  
-- =====================================================
CREATE TABLE engagement_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL,
    
    -- 4 Core Engagement Scores (0-100)
    email_engagement_score DECIMAL(5,2) DEFAULT 0.00,
    whatsapp_engagement_score DECIMAL(5,2) DEFAULT 0.00,
    call_performance_score DECIMAL(5,2) DEFAULT 0.00,
    overall_responsiveness_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Engagement Insights
    preferred_channel ENUM('email', 'whatsapp', 'call', 'mixed', 'none') DEFAULT 'none',
    engagement_consistency_score DECIMAL(5,2) DEFAULT 0.00,
    engagement_trend ENUM('improving', 'stable', 'declining', 'new') DEFAULT 'new',
    
    -- Raw Engagement Metrics (for transparency)
    avg_email_open_rate DECIMAL(5,2),
    avg_email_click_rate DECIMAL(5,2),
    avg_whatsapp_read_rate DECIMAL(5,2),
    avg_whatsapp_click_rate DECIMAL(5,2),
    avg_call_productive_rate DECIMAL(5,2),
    avg_call_duration_minutes DECIMAL(8,2),
    
    -- Campaign Analysis Period
    campaign_period_start DATE,
    campaign_period_end DATE,
    total_campaigns_analyzed INT DEFAULT 0,
    active_campaigns_count INT DEFAULT 0,
    
    -- Calculation Metadata
    engagement_data_quality DECIMAL(5,2) DEFAULT 0.00,
    missing_data_flags JSON, -- Store which engagement metrics are missing
    
    -- Timestamps
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    FOREIGN KEY (UIN) REFERENCES doctors_pi(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_preferred_channel (preferred_channel),
    INDEX idx_overall_responsiveness (overall_responsiveness_score),
    INDEX idx_email_engagement (email_engagement_score),
    INDEX idx_whatsapp_engagement (whatsapp_engagement_score),
    INDEX idx_call_performance (call_performance_score),
    INDEX idx_campaign_period (campaign_period_start, campaign_period_end),
    
    -- Ensure one record per UIN
    UNIQUE KEY unique_uin (UIN)
);

-- =====================================================
-- TIER 3: AUTHORITY & QUALITY SCORES TABLE
-- =====================================================
CREATE TABLE authority_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL,
    
    -- 5 Core Authority Scores (0-100)
    research_authority_score DECIMAL(5,2) DEFAULT 0.00,
    digital_authority_score DECIMAL(5,2) DEFAULT 0.00,
    professional_network_score DECIMAL(5,2) DEFAULT 0.00,
    data_quality_score DECIMAL(5,2) DEFAULT 0.00,
    overall_influence_score DECIMAL(5,2) DEFAULT 0.00,
    
    -- Detailed Authority Indicators (JSON for flexibility)
    research_indicators JSON, -- {has_publications: true, publication_count: 5, has_trials: true, h_index: 12}
    digital_indicators JSON,  -- {has_social_media: true, platforms_count: 3, max_followers: 1500}
    network_indicators JSON,  -- {association_count: 2, academic_roles: 1, years_experience: 15}
    quality_indicators JSON,  -- {completeness: 85, accuracy_flags: [], freshness_score: 90}
    
    -- Raw Authority Metrics (for scoring transparency)
    publication_count INT DEFAULT 0,
    award_count INT DEFAULT 0,
    trial_count INT DEFAULT 0,
    h_index_value INT DEFAULT 0,
    association_count INT DEFAULT 0,
    academic_affiliation_count INT DEFAULT 0,
    social_media_platforms INT DEFAULT 0,
    max_social_followers INT DEFAULT 0,
    healthcare_platform_count INT DEFAULT 0,
    years_of_experience INT DEFAULT 0,
    
    -- Scoring Methodology Metadata
    scoring_method_used VARCHAR(100) DEFAULT 'robust_dynamic',
    effective_min_values JSON, -- Store effective min/max used for scoring
    effective_max_values JSON,
    outlier_count INT DEFAULT 0,
    
    -- Data Quality Assessment
    profile_completeness DECIMAL(5,2) DEFAULT 0.00,
    data_accuracy_score DECIMAL(5,2) DEFAULT 0.00,
    data_freshness_score DECIMAL(5,2) DEFAULT 0.00,
    quality_flags JSON, -- Store any data quality issues found
    
    -- Timestamps
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    FOREIGN KEY (UIN) REFERENCES doctors_pi(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_research_authority (research_authority_score),
    INDEX idx_digital_authority (digital_authority_score),
    INDEX idx_professional_network (professional_network_score),
    INDEX idx_overall_influence (overall_influence_score),
    INDEX idx_data_quality (data_quality_score),
    INDEX idx_years_experience (years_of_experience),
    INDEX idx_publication_count (publication_count),
    
    -- Ensure one record per UIN
    UNIQUE KEY unique_uin (UIN)
);

-- =====================================================
-- CLUSTERING RESULTS TABLE
-- =====================================================
CREATE TABLE cluster_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL,
    
    -- Cluster Assignment
    cluster_id INT NOT NULL,
    cluster_name VARCHAR(200),
    cluster_description TEXT,
    
    -- Cluster Quality Metrics
    distance_to_centroid DECIMAL(8,4),
    assignment_confidence DECIMAL(5,2), -- How confident are we in this assignment
    silhouette_score DECIMAL(6,4), -- Individual silhouette score
    second_closest_cluster_id INT, -- Which cluster was second choice
    
    -- Feature Vector (for transparency and debugging)
    feature_vector JSON, -- Store the 14-dimension feature vector used
    
    -- Clustering Run Metadata
    clustering_run_id VARCHAR(100) NOT NULL, -- Unique ID for each clustering execution
    clustering_algorithm VARCHAR(50) DEFAULT 'kmeans',
    n_clusters INT NOT NULL,
    clustering_parameters JSON, -- Store algorithm parameters used
    
    -- Business Metrics
    business_value_score DECIMAL(5,2) DEFAULT 0.00,
    targeting_priority ENUM('High', 'Medium', 'Low', 'Ignore') DEFAULT 'Medium',
    
    -- Timestamps
    clustering_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    FOREIGN KEY (UIN) REFERENCES doctors_pi(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_cluster_id (cluster_id),
    INDEX idx_clustering_run_id (clustering_run_id),
    INDEX idx_clustering_date (clustering_date),
    INDEX idx_business_value (business_value_score),
    INDEX idx_targeting_priority (targeting_priority),
    INDEX idx_assignment_confidence (assignment_confidence)
);

-- =====================================================
-- CLUSTER PROFILES TABLE (Cluster Characteristics)
-- =====================================================
CREATE TABLE cluster_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Cluster Identification
    clustering_run_id VARCHAR(100) NOT NULL,
    cluster_id INT NOT NULL,
    cluster_name VARCHAR(200),
    cluster_suggested_name VARCHAR(200), -- Auto-generated business-friendly name
    
    -- Cluster Size & Distribution
    cluster_size INT NOT NULL,
    cluster_percentage DECIMAL(5,2) NOT NULL,
    
    -- Cluster Characteristics (JSON for flexibility)
    defining_characteristics JSON, -- Key features that define this cluster
    feature_averages JSON, -- Average values for all 14 features
    feature_deviations JSON, -- How much each feature deviates from global average
    
    -- Business Intelligence
    business_value_score DECIMAL(5,2) DEFAULT 0.00,
    targeting_strategy TEXT,
    recommended_channels TEXT, -- email, whatsapp, call preferences
    key_personas TEXT, -- dominant persona types in cluster
    
    -- Engagement Profile
    avg_email_engagement DECIMAL(5,2),
    avg_whatsapp_engagement DECIMAL(5,2),
    avg_call_performance DECIMAL(5,2),
    avg_overall_responsiveness DECIMAL(5,2),
    
    -- Authority Profile  
    avg_research_authority DECIMAL(5,2),
    avg_digital_authority DECIMAL(5,2),
    avg_professional_network DECIMAL(5,2),
    avg_overall_influence DECIMAL(5,2),
    
    -- Geographic & Specialty Distribution
    top_specialties JSON, -- Most common specialties in cluster
    top_cities JSON, -- Most common cities in cluster
    top_states JSON, -- Most common states in cluster
    
    -- Cluster Quality Metrics
    avg_silhouette_score DECIMAL(6,4),
    cluster_cohesion DECIMAL(5,2), -- How similar are members to each other
    cluster_separation DECIMAL(5,2), -- How different from other clusters
    
    -- Priority & Classification
    priority_level ENUM('Critical', 'High', 'Medium', 'Low') DEFAULT 'Medium',
    cluster_stability ENUM('Stable', 'Moderate', 'Volatile') DEFAULT 'Moderate',
    actionability_score DECIMAL(5,2) DEFAULT 0.00, -- How actionable is this cluster
    
    -- Sample Members (for validation)
    sample_member_uins JSON, -- Store 5-10 sample UINs for manual review
    
    -- Clustering Context
    clustering_algorithm VARCHAR(50) DEFAULT 'kmeans',
    n_total_clusters INT,
    total_doctors_clustered INT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_clustering_run_id (clustering_run_id),
    INDEX idx_cluster_id (cluster_id),
    INDEX idx_business_value (business_value_score),
    INDEX idx_priority_level (priority_level),
    INDEX idx_cluster_size (cluster_size),
    
    -- Ensure unique cluster per run
    UNIQUE KEY unique_cluster_run (clustering_run_id, cluster_id)
);

-- =====================================================
-- COMPREHENSIVE DOCTOR ANALYTICS SUMMARY VIEW
-- =====================================================
CREATE TABLE doctor_analytics_summary (
    UIN VARCHAR(50) PRIMARY KEY,
    
    -- Basic Doctor Information
    full_name VARCHAR(200),
    specialty VARCHAR(200),
    subspeciality VARCHAR(200),
    dr_city VARCHAR(100),
    dr_state VARCHAR(100),
    dr_country VARCHAR(100) DEFAULT 'India',
    years_of_experience INT,
    primary_institution VARCHAR(300),
    
    -- Tier 1: Persona Scores (5 scores)
    academic_score DECIMAL(5,2) DEFAULT 0.00,
    patient_score DECIMAL(5,2) DEFAULT 0.00,
    technology_score DECIMAL(5,2) DEFAULT 0.00,
    recognition_score DECIMAL(5,2) DEFAULT 0.00,
    community_score DECIMAL(5,2) DEFAULT 0.00,
    primary_persona VARCHAR(50),
    secondary_persona VARCHAR(50),
    persona_confidence ENUM('High', 'Medium', 'Low'),
    
    -- Tier 2: Engagement Scores (4 scores)  
    email_engagement DECIMAL(5,2) DEFAULT 0.00,
    whatsapp_engagement DECIMAL(5,2) DEFAULT 0.00,
    call_performance DECIMAL(5,2) DEFAULT 0.00,
    overall_responsiveness DECIMAL(5,2) DEFAULT 0.00,
    preferred_channel VARCHAR(20),
    engagement_consistency DECIMAL(5,2) DEFAULT 0.00,
    
    -- Tier 3: Authority Scores (5 scores)
    research_authority DECIMAL(5,2) DEFAULT 0.00,
    digital_authority DECIMAL(5,2) DEFAULT 0.00,
    professional_network DECIMAL(5,2) DEFAULT 0.00,
    data_quality DECIMAL(5,2) DEFAULT 0.00,
    overall_influence DECIMAL(5,2) DEFAULT 0.00,
    
    -- Current Cluster Assignment
    current_cluster_id INT,
    current_cluster_name VARCHAR(200),
    current_clustering_run_id VARCHAR(100),
    cluster_assignment_confidence DECIMAL(5,2),
    
    -- Business Metrics
    business_value_score DECIMAL(5,2) DEFAULT 0.00,
    targeting_priority ENUM('Critical', 'High', 'Medium', 'Low', 'Ignore') DEFAULT 'Medium',
    
    -- Contact & Accessibility
    has_email BOOLEAN DEFAULT FALSE,
    has_mobile BOOLEAN DEFAULT FALSE,
    has_whatsapp BOOLEAN DEFAULT FALSE,
    clinic_count INT DEFAULT 0,
    
    -- Data Quality Indicators
    profile_completeness DECIMAL(5,2) DEFAULT 0.00,
    last_activity_date DATE,
    data_freshness_days INT,
    
    -- Update Tracking
    scores_last_calculated TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for fast filtering and sorting
    INDEX idx_specialty (specialty),
    INDEX idx_location (dr_city, dr_state),
    INDEX idx_primary_persona (primary_persona),
    INDEX idx_preferred_channel (preferred_channel),
    INDEX idx_current_cluster (current_cluster_id),
    INDEX idx_business_value (business_value_score),
    INDEX idx_targeting_priority (targeting_priority),
    INDEX idx_overall_responsiveness (overall_responsiveness),
    INDEX idx_overall_influence (overall_influence),
    INDEX idx_academic_score (academic_score),
    INDEX idx_patient_score (patient_score),
    INDEX idx_technology_score (technology_score),
    INDEX idx_profile_completeness (profile_completeness),
    INDEX idx_years_experience (years_of_experience),
    
    -- Composite indexes for common filter combinations
    INDEX idx_specialty_location (specialty, dr_city, dr_state),
    INDEX idx_persona_engagement (primary_persona, overall_responsiveness),
    INDEX idx_authority_responsiveness (overall_influence, overall_responsiveness),
    
    FOREIGN KEY (UIN) REFERENCES doctors_pi(UIN) ON DELETE CASCADE
);

-- =====================================================
-- SCORING METADATA TABLE (For Transparency & Debugging)
-- =====================================================
CREATE TABLE scoring_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Scoring Run Information
    scoring_run_id VARCHAR(100) NOT NULL,
    scoring_tier ENUM('tier1_persona', 'tier2_engagement', 'tier3_authority') NOT NULL,
    scoring_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Data Statistics
    total_records_processed INT,
    successful_calculations INT,
    failed_calculations INT,
    
    -- For Tier 1 (Persona Scoring)
    keywords_used JSON, -- Store keyword dictionary used
    avg_keywords_matched DECIMAL(5,2),
    
    -- For Tier 2 (Engagement Scoring)  
    engagement_data_period_start DATE,
    engagement_data_period_end DATE,
    campaigns_analyzed INT,
    
    -- For Tier 3 (Authority Scoring)
    scoring_method VARCHAR(100),
    field_effective_ranges JSON, -- Store effective min/max for each numeric field
    outlier_counts JSON,
    
    -- Quality Indicators
    data_completeness_avg DECIMAL(5,2),
    calculation_confidence_avg DECIMAL(5,2),
    
    -- Performance Metrics
    processing_time_seconds INT,
    memory_usage_mb DECIMAL(8,2),
    
    -- Error Tracking
    error_log JSON, -- Store any errors encountered
    warning_count INT,
    
    -- Indexes
    INDEX idx_scoring_run_id (scoring_run_id),
    INDEX idx_scoring_tier (scoring_tier),
    INDEX idx_scoring_date (scoring_date),
    
    UNIQUE KEY unique_run_tier (scoring_run_id, scoring_tier)
);

-- =====================================================
-- PnC TRAIT ANALYSIS TABLE (Persona Combinations)
-- =====================================================
CREATE TABLE trait_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL,
    
    -- Trait Combination Definition
    trait_combination VARCHAR(200) NOT NULL, -- e.g., "Academic + Patient Focused"
    persona_combination JSON NOT NULL, -- ["academic_research", "patient_focused"]
    combination_size INT NOT NULL, -- 2 for dual, 3 for triple combinations
    
    -- Trait Score (calculated from constituent personas)
    trait_score DECIMAL(5,2) NOT NULL,
    trait_strength ENUM('Very Strong', 'Strong', 'Moderate', 'Weak') DEFAULT 'Moderate',
    
    -- Constituent Persona Scores
    constituent_scores JSON, -- Store individual scores that make up this trait
    scoring_method ENUM('weighted_average', 'minimum_threshold', 'geometric_mean') DEFAULT 'weighted_average',
    
    -- Business Value
    trait_business_value DECIMAL(5,2) DEFAULT 0.00,
    trait_rarity_score DECIMAL(5,2) DEFAULT 50.00, -- How rare is this combination
    
    -- Qualification Criteria
    meets_minimum_threshold BOOLEAN DEFAULT TRUE,
    minimum_threshold_used DECIMAL(5,2) DEFAULT 30.00,
    
    -- Analysis Run Context
    analysis_run_id VARCHAR(100) NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    FOREIGN KEY (UIN) REFERENCES doctors_pi(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_trait_combination (trait_combination),
    INDEX idx_combination_size (combination_size),
    INDEX idx_trait_score (trait_score),
    INDEX idx_trait_strength (trait_strength),
    INDEX idx_analysis_run_id (analysis_run_id),
    INDEX idx_business_value (trait_business_value),
    INDEX idx_rarity_score (trait_rarity_score)
);

-- =====================================================
-- DATA PIPELINE STATUS TABLE (For Monitoring)
-- =====================================================
CREATE TABLE pipeline_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Pipeline Run Information
    pipeline_run_id VARCHAR(100) NOT NULL UNIQUE,
    pipeline_type ENUM('full_refresh', 'incremental_update', 'clustering_only', 'trait_analysis') NOT NULL,
    
    -- Execution Status
    status ENUM('running', 'completed', 'failed', 'cancelled') DEFAULT 'running',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    -- Progress Tracking
    total_steps INT DEFAULT 6, -- tier1, tier2, tier3, clustering, traits, summary_update
    current_step INT DEFAULT 0,
    current_step_name VARCHAR(100),
    
    -- Data Processing Stats
    total_doctors_processed INT DEFAULT 0,
    successful_calculations INT DEFAULT 0,
    failed_calculations INT DEFAULT 0,
    
    -- Results Summary
    clusters_generated INT DEFAULT 0,
    traits_analyzed INT DEFAULT 0,
    avg_data_quality DECIMAL(5,2) DEFAULT 0.00,
    
    -- Error Handling
    error_message TEXT,
    warning_count INT DEFAULT 0,
    
    -- Performance Metrics
    total_runtime_seconds INT,
    peak_memory_usage_mb DECIMAL(8,2),
    
    -- Configuration Used
    configuration_snapshot JSON, -- Store key parameters used
    
    -- Indexes
    INDEX idx_pipeline_run_id (pipeline_run_id),
    INDEX idx_status (status),
    INDEX idx_pipeline_type (pipeline_type),
    INDEX idx_started_at (started_at),
    INDEX idx_completed_at (completed_at)
);

-- =====================================================
-- INDEXES FOR CROSS-TABLE ANALYTICS
-- =====================================================

-- Create composite indexes for common analytical queries
ALTER TABLE doctor_analytics_summary ADD INDEX idx_high_value_doctors (
    business_value_score, overall_influence, overall_responsiveness
);

ALTER TABLE doctor_analytics_summary ADD INDEX idx_persona_authority (
    primary_persona, research_authority, digital_authority
);

ALTER TABLE doctor_analytics_summary ADD INDEX idx_engagement_channel_specialty (
    preferred_channel, specialty, overall_responsiveness
);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- High-Value Target Doctors View
CREATE VIEW high_value_doctors AS
SELECT 
    das.*,
    ca.cluster_name,
    cp.targeting_strategy,
    cp.recommended_channels
FROM doctor_analytics_summary das
LEFT JOIN cluster_assignments ca ON das.UIN = ca.UIN 
    AND ca.clustering_run_id = das.current_clustering_run_id
LEFT JOIN cluster_profiles cp ON ca.clustering_run_id = cp.clustering_run_id 
    AND ca.cluster_id = cp.cluster_id
WHERE das.business_value_score > 60
    AND das.overall_responsiveness > 40
    AND das.profile_completeness > 70
ORDER BY das.business_value_score DESC;

-- Persona Distribution Summary View  
CREATE VIEW persona_distribution AS
SELECT 
    primary_persona,
    COUNT(*) as doctor_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM doctor_analytics_summary), 2) as percentage,
    AVG(academic_score) as avg_academic_score,
    AVG(patient_score) as avg_patient_score,
    AVG(technology_score) as avg_technology_score,
    AVG(recognition_score) as avg_recognition_score,
    AVG(community_score) as avg_community_score,
    AVG(overall_responsiveness) as avg_responsiveness,
    AVG(overall_influence) as avg_influence
FROM doctor_analytics_summary 
WHERE primary_persona IS NOT NULL
GROUP BY primary_persona
ORDER BY doctor_count DESC;

-- Cluster Performance Summary View
CREATE VIEW cluster_performance AS
SELECT 
    cp.cluster_id,
    cp.cluster_name,
    cp.cluster_size,
    cp.business_value_score,
    cp.avg_overall_responsiveness,
    cp.avg_overall_influence,
    cp.targeting_strategy,
    cp.priority_level,
    COUNT(das.UIN) as active_members,
    AVG(das.profile_completeness) as avg_profile_quality
FROM cluster_profiles cp
LEFT JOIN doctor_analytics_summary das ON cp.cluster_id = das.current_cluster_id
WHERE cp.clustering_run_id = (
    SELECT clustering_run_id 
    FROM cluster_profiles 
    ORDER BY created_at DESC 
    LIMIT 1
)
GROUP BY cp.cluster_id
ORDER BY cp.business_value_score DESC;