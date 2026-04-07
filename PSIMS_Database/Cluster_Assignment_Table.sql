-- Create cluster_assignments table
CREATE TABLE cluster_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UIN VARCHAR(255) NOT NULL,
    
    cluster_id INT NOT NULL,
    cluster_name VARCHAR(200),
    cluster_description TEXT,
    
    distance_to_centroid DECIMAL(8,4),
    assignment_confidence DECIMAL(5,2),
    
    clustering_run_id VARCHAR(100) NOT NULL,
    n_clusters INT NOT NULL,
    
    clustering_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (UIN) REFERENCES doctors(UIN) ON DELETE CASCADE,
    INDEX idx_uin (UIN),
    INDEX idx_cluster_id (cluster_id),
    INDEX idx_clustering_run_id (clustering_run_id)
);

-- Create cluster_profiles table
CREATE TABLE cluster_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clustering_run_id VARCHAR(100) NOT NULL,
    cluster_id INT NOT NULL,
    cluster_name VARCHAR(200),
    cluster_size INT NOT NULL,
    cluster_percentage DECIMAL(5,2) NOT NULL,
    
    business_value_score DECIMAL(5,2) DEFAULT 0.00,
    targeting_strategy TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_clustering_run_id (clustering_run_id),
    INDEX idx_cluster_id (cluster_id),
    
    UNIQUE KEY unique_cluster_run (clustering_run_id, cluster_id)
);