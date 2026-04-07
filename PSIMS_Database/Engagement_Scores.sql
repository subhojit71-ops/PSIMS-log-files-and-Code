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
    
    -- Timestamps
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (UIN) REFERENCES doctors(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_preferred_channel (preferred_channel),
    INDEX idx_overall_responsiveness (overall_responsiveness_score),
    
    UNIQUE KEY unique_uin (UIN)
);