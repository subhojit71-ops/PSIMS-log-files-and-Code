-- Create engagement data table (since it's missing)
CREATE TABLE engagement_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(50) NOT NULL, -- or client_doctor_code - whatever maps to doctors.UIN
    campaign_start_date DATE,
    hcp_email_open_rate DECIMAL(5,2) DEFAULT 0.00,
    hcp_whatsapp_read_rate DECIMAL(5,2) DEFAULT 0.00,
    hcp_email_click_rate DECIMAL(5,2) DEFAULT 0.00,
    hcp_whatsapp_click_rate DECIMAL(5,2) DEFAULT 0.00,
    hcp_call_productive_rate DECIMAL(5,2) DEFAULT 0.00,
    last_call_connected_date DATE,
    average_duration_connected_calls DECIMAL(8,2) DEFAULT 0.00,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (UIN) REFERENCES doctors(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_campaign_date (campaign_start_date)
);