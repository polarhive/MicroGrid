-- =====================================================
-- Microclimate Sensor Grid Database Schema
-- UE23CS351A Mini Project
-- =====================================================

-- Drop database if exists and create fresh
DROP DATABASE IF EXISTS microclimate_grid;
CREATE DATABASE microclimate_grid;
USE microclimate_grid;

-- =====================================================
-- TABLE DEFINITIONS
-- =====================================================

-- Table: User (for authentication)
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Table: SensorType
CREATE TABLE SensorType (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Location
CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    area_name VARCHAR(100),
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    elevation DECIMAL(6,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(latitude, longitude)
);

-- Table: Sensor
CREATE TABLE Sensor (
    sensor_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    install_date DATE NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'MAINTENANCE') DEFAULT 'ACTIVE',
    type_id INT NOT NULL,
    location_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES SensorType(type_id) ON DELETE RESTRICT,
    FOREIGN KEY (location_id) REFERENCES Location(location_id) ON DELETE RESTRICT
);

-- Table: Reading
CREATE TABLE Reading (
    reading_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    reading_value DECIMAL(10,4) NOT NULL,
    reading_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES Sensor(sensor_id) ON DELETE CASCADE,
    INDEX idx_sensor_timestamp (sensor_id, reading_timestamp)
);

-- Table: Technician
CREATE TABLE Technician (
    tech_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_no VARCHAR(15),
    specialization VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: MaintenanceEvent
CREATE TABLE MaintenanceEvent (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    tech_id INT NOT NULL,
    event_type ENUM('CALIBRATION', 'REPAIR', 'REPLACEMENT') NOT NULL,
    event_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES Sensor(sensor_id) ON DELETE CASCADE,
    FOREIGN KEY (tech_id) REFERENCES Technician(tech_id) ON DELETE RESTRICT
);

-- Table: SensorStatusLog (for trigger logging)
CREATE TABLE SensorStatusLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    old_status ENUM('ACTIVE', 'INACTIVE', 'MAINTENANCE'),
    new_status ENUM('ACTIVE', 'INACTIVE', 'MAINTENANCE'),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES Sensor(sensor_id) ON DELETE CASCADE
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Log sensor status changes
DELIMITER //
CREATE TRIGGER before_sensor_update
BEFORE UPDATE ON Sensor
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO SensorStatusLog (sensor_id, old_status, new_status)
        VALUES (OLD.sensor_id, OLD.status, NEW.status);
    END IF;
END//
DELIMITER ;

-- Trigger: Update sensor status after maintenance
DELIMITER //
CREATE TRIGGER after_maintenance_insert
AFTER INSERT ON MaintenanceEvent
FOR EACH ROW
BEGIN
    -- If maintenance type is REPAIR or REPLACEMENT, set sensor to MAINTENANCE
    IF NEW.event_type IN ('REPAIR', 'REPLACEMENT') THEN
        UPDATE Sensor 
        SET status = 'MAINTENANCE', updated_at = CURRENT_TIMESTAMP
        WHERE sensor_id = NEW.sensor_id;
    END IF;
END//
DELIMITER ;

-- Trigger: Validate reading values
DELIMITER //
CREATE TRIGGER before_reading_insert
BEFORE INSERT ON Reading
FOR EACH ROW
BEGIN
    -- Ensure reading timestamp is not in the future
    IF NEW.reading_timestamp > CURRENT_TIMESTAMP THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Reading timestamp cannot be in the future';
    END IF;
END//
DELIMITER ;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Procedure: Get all readings for a specific sensor
DELIMITER //
CREATE PROCEDURE GetSensorReadings(IN p_sensor_id INT)
BEGIN
    SELECT 
        r.reading_id,
        r.sensor_id,
        s.model,
        st.name AS sensor_type,
        r.reading_value,
        r.reading_timestamp
    FROM Reading r
    JOIN Sensor s ON r.sensor_id = s.sensor_id
    JOIN SensorType st ON s.type_id = st.type_id
    WHERE r.sensor_id = p_sensor_id
    ORDER BY r.reading_timestamp DESC;
END//
DELIMITER ;

-- Procedure: Get maintenance summary by event type
DELIMITER //
CREATE PROCEDURE GetMaintenanceSummary()
BEGIN
    SELECT 
        event_type,
        COUNT(*) AS event_count,
        COUNT(DISTINCT sensor_id) AS sensors_affected,
        COUNT(DISTINCT tech_id) AS technicians_involved
    FROM MaintenanceEvent
    GROUP BY event_type
    ORDER BY event_count DESC;
END//
DELIMITER ;

-- Procedure: Get sensor statistics by location
DELIMITER //
CREATE PROCEDURE GetLocationStatistics(IN p_location_id INT)
BEGIN
    SELECT 
        l.area_name,
        l.latitude,
        l.longitude,
        COUNT(DISTINCT s.sensor_id) AS total_sensors,
        SUM(CASE WHEN s.status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_sensors,
        COUNT(r.reading_id) AS total_readings,
        AVG(r.reading_value) AS avg_reading
    FROM Location l
    LEFT JOIN Sensor s ON l.location_id = s.location_id
    LEFT JOIN Reading r ON s.sensor_id = r.sensor_id
    WHERE l.location_id = p_location_id
    GROUP BY l.location_id;
END//
DELIMITER ;

-- Procedure: Get top technicians by maintenance count
DELIMITER //
CREATE PROCEDURE GetTopTechnicians(IN p_limit INT)
BEGIN
    SELECT 
        t.tech_id,
        t.name,
        t.specialization,
        COUNT(m.maintenance_id) AS maintenance_count,
        GROUP_CONCAT(DISTINCT m.event_type ORDER BY m.event_type) AS event_types
    FROM Technician t
    LEFT JOIN MaintenanceEvent m ON t.tech_id = m.tech_id
    GROUP BY t.tech_id
    ORDER BY maintenance_count DESC
    LIMIT p_limit;
END//
DELIMITER ;

-- Procedure: Get average readings per sensor type
DELIMITER //
CREATE PROCEDURE GetAvgReadingsBySensorType()
BEGIN
    SELECT 
        st.type_id,
        st.name AS sensor_type,
        st.description,
        COUNT(DISTINCT s.sensor_id) AS sensor_count,
        COUNT(r.reading_id) AS total_readings,
        ROUND(AVG(r.reading_value), 2) AS avg_reading,
        ROUND(MIN(r.reading_value), 2) AS min_reading,
        ROUND(MAX(r.reading_value), 2) AS max_reading
    FROM SensorType st
    LEFT JOIN Sensor s ON st.type_id = s.type_id
    LEFT JOIN Reading r ON s.sensor_id = r.sensor_id
    GROUP BY st.type_id
    ORDER BY sensor_count DESC;
END//
DELIMITER ;

-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- Insert Users (password is 'admin123' hashed with werkzeug)
-- Password hash generated using: werkzeug.security.generate_password_hash('admin123')
INSERT INTO User (username, email, password_hash, full_name, is_active) VALUES
('admin', 'admin@microclimate.com', 'scrypt:32768:8:1$RDhqhekc2l0UI32I$0f1bc8c5a56e0d6b03078b937cc108e691809b313e15a091784487752f04b822c4b7bf25e8d7020bcf33af75160d43d92174de99521da9b61247c70a65863f09', 'System Administrator', TRUE),
('demo', 'demo@microclimate.com', 'scrypt:32768:8:1$RDhqhekc2l0UI32I$0f1bc8c5a56e0d6b03078b937cc108e691809b313e15a091784487752f04b822c4b7bf25e8d7020bcf33af75160d43d92174de99521da9b61247c70a65863f09', 'Demo User', TRUE);

-- Insert Sensor Types
INSERT INTO SensorType (name, description) VALUES
('Temperature', 'Measures ambient temperature in Celsius'),
('Humidity', 'Measures relative humidity percentage'),
('Pressure', 'Measures atmospheric pressure in hPa'),
('Wind Speed', 'Measures wind speed in km/h'),
('Rainfall', 'Measures precipitation in mm'),
('Solar Radiation', 'Measures solar radiation in W/m²');

-- Insert Locations
INSERT INTO Location (area_name, latitude, longitude, elevation) VALUES
('PESU Campus North', 13.024700, 77.566700, 920.50),
('PESU Campus South', 13.023500, 77.567200, 918.20),
('Electronic City Phase 1', 12.845600, 77.663800, 905.00),
('Whitefield Tech Park', 12.970100, 77.750000, 915.75),
('Koramangala Block 4', 12.935000, 77.626900, 910.30),
('HSR Layout Sector 1', 12.912000, 77.638700, 912.00),
('Indiranagar Metro', 12.971600, 77.640800, 920.00),
('Jayanagar 4th Block', 12.925700, 77.583900, 908.50);

-- Insert Technicians
INSERT INTO Technician (name, contact_no, specialization) VALUES
('Rajesh Kumar', '9876543210', 'Temperature Sensors'),
('Priya Sharma', '9876543211', 'Humidity Sensors'),
('Amit Patel', '9876543212', 'Pressure Sensors'),
('Sneha Reddy', '9876543213', 'General Maintenance'),
('Vikram Singh', '9876543214', 'Electronics'),
('Anita Desai', '9876543215', 'Calibration Specialist');

-- Insert Sensors
INSERT INTO Sensor (model, install_date, status, type_id, location_id) VALUES
('DHT22-001', '2023-01-15', 'ACTIVE', 1, 1),
('DHT22-002', '2023-01-15', 'ACTIVE', 2, 1),
('BMP280-001', '2023-02-20', 'ACTIVE', 3, 2),
('ANEM-001', '2023-03-10', 'ACTIVE', 4, 3),
('RAIN-001', '2023-03-15', 'ACTIVE', 5, 3),
('SOLAR-001', '2023-04-01', 'ACTIVE', 6, 4),
('DHT22-003', '2023-04-15', 'ACTIVE', 1, 5),
('DHT22-004', '2023-04-15', 'ACTIVE', 2, 5),
('BMP280-002', '2023-05-01', 'MAINTENANCE', 3, 6),
('ANEM-002', '2023-05-10', 'ACTIVE', 4, 7),
('RAIN-002', '2023-05-15', 'ACTIVE', 5, 8),
('DHT22-005', '2023-06-01', 'INACTIVE', 1, 6),
('SOLAR-002', '2023-06-10', 'ACTIVE', 6, 7),
('DHT22-006', '2023-07-01', 'ACTIVE', 2, 8),
('BMP280-003', '2023-07-15', 'ACTIVE', 3, 1);

-- Insert Readings (Temperature sensors - Celsius)
INSERT INTO Reading (sensor_id, reading_value, reading_timestamp) VALUES
-- Sensor 1 (Temperature)
(1, 24.5, '2024-10-20 08:00:00'),
(1, 25.2, '2024-10-20 09:00:00'),
(1, 26.8, '2024-10-20 10:00:00'),
(1, 28.3, '2024-10-20 11:00:00'),
(1, 29.5, '2024-10-20 12:00:00'),
(1, 30.2, '2024-10-20 13:00:00'),
(1, 29.8, '2024-10-20 14:00:00'),
(1, 28.4, '2024-10-20 15:00:00'),
(1, 26.9, '2024-10-20 16:00:00'),
(1, 25.3, '2024-10-20 17:00:00'),

-- Sensor 2 (Humidity)
(2, 65.5, '2024-10-20 08:00:00'),
(2, 63.2, '2024-10-20 09:00:00'),
(2, 61.8, '2024-10-20 10:00:00'),
(2, 58.3, '2024-10-20 11:00:00'),
(2, 55.5, '2024-10-20 12:00:00'),
(2, 54.2, '2024-10-20 13:00:00'),
(2, 56.8, '2024-10-20 14:00:00'),
(2, 59.4, '2024-10-20 15:00:00'),
(2, 62.9, '2024-10-20 16:00:00'),
(2, 64.3, '2024-10-20 17:00:00'),

-- Sensor 3 (Pressure)
(3, 1013.2, '2024-10-20 08:00:00'),
(3, 1013.5, '2024-10-20 09:00:00'),
(3, 1013.8, '2024-10-20 10:00:00'),
(3, 1014.1, '2024-10-20 11:00:00'),
(3, 1014.3, '2024-10-20 12:00:00'),

-- Sensor 4 (Wind Speed)
(4, 12.5, '2024-10-20 08:00:00'),
(4, 15.3, '2024-10-20 09:00:00'),
(4, 18.7, '2024-10-20 10:00:00'),
(4, 20.2, '2024-10-20 11:00:00'),
(4, 16.8, '2024-10-20 12:00:00'),

-- Sensor 5 (Rainfall)
(5, 0.0, '2024-10-20 08:00:00'),
(5, 0.0, '2024-10-20 09:00:00'),
(5, 2.5, '2024-10-20 10:00:00'),
(5, 5.3, '2024-10-20 11:00:00'),
(5, 3.2, '2024-10-20 12:00:00'),

-- Sensor 6 (Solar Radiation)
(6, 250.5, '2024-10-20 08:00:00'),
(6, 450.3, '2024-10-20 09:00:00'),
(6, 680.7, '2024-10-20 10:00:00'),
(6, 850.2, '2024-10-20 11:00:00'),
(6, 920.5, '2024-10-20 12:00:00'),

-- Sensor 7 (Temperature)
(7, 23.5, '2024-10-20 08:00:00'),
(7, 24.8, '2024-10-20 09:00:00'),
(7, 26.2, '2024-10-20 10:00:00'),

-- Sensor 8 (Humidity)
(8, 68.5, '2024-10-20 08:00:00'),
(8, 66.2, '2024-10-20 09:00:00'),
(8, 64.8, '2024-10-20 10:00:00'),

-- Sensor 10 (Wind Speed)
(10, 14.2, '2024-10-20 08:00:00'),
(10, 16.5, '2024-10-20 09:00:00'),
(10, 19.3, '2024-10-20 10:00:00'),

-- Sensor 11 (Rainfall)
(11, 0.5, '2024-10-20 08:00:00'),
(11, 1.2, '2024-10-20 09:00:00'),
(11, 0.8, '2024-10-20 10:00:00'),

-- Sensor 13 (Solar Radiation)
(13, 280.5, '2024-10-20 08:00:00'),
(13, 470.3, '2024-10-20 09:00:00'),
(13, 720.7, '2024-10-20 10:00:00'),

-- Sensor 14 (Humidity)
(14, 67.5, '2024-10-20 08:00:00'),
(14, 65.2, '2024-10-20 09:00:00'),
(14, 63.8, '2024-10-20 10:00:00'),

-- Sensor 15 (Pressure)
(15, 1012.8, '2024-10-20 08:00:00'),
(15, 1013.2, '2024-10-20 09:00:00'),
(15, 1013.6, '2024-10-20 10:00:00');

-- Insert Maintenance Events
INSERT INTO MaintenanceEvent (sensor_id, tech_id, event_type, event_date, notes) VALUES
(1, 1, 'CALIBRATION', '2024-09-15 10:00:00', 'Regular calibration check'),
(2, 2, 'CALIBRATION', '2024-09-15 11:00:00', 'Humidity sensor calibration'),
(3, 3, 'REPAIR', '2024-09-20 14:30:00', 'Pressure reading anomaly fixed'),
(9, 3, 'REPAIR', '2024-10-01 09:00:00', 'Sensor malfunction - replaced circuit board'),
(12, 1, 'REPLACEMENT', '2024-10-05 10:30:00', 'Complete sensor replacement due to damage'),
(4, 4, 'CALIBRATION', '2024-10-10 15:00:00', 'Wind speed sensor recalibration'),
(5, 4, 'CALIBRATION', '2024-10-10 16:00:00', 'Rainfall sensor check'),
(6, 5, 'REPAIR', '2024-10-12 11:00:00', 'Solar panel cleaning and wiring fix'),
(7, 1, 'CALIBRATION', '2024-10-15 09:30:00', 'Temperature sensor calibration'),
(8, 2, 'CALIBRATION', '2024-10-15 10:30:00', 'Humidity sensor maintenance');

-- =====================================================
-- VIEWS FOR COMPLEX QUERIES
-- =====================================================

-- View: Active Sensors with Details
CREATE VIEW ActiveSensorsView AS
SELECT 
    s.sensor_id,
    s.model,
    st.name AS sensor_type,
    l.area_name,
    l.latitude,
    l.longitude,
    s.install_date,
    s.status
FROM Sensor s
JOIN SensorType st ON s.type_id = st.type_id
JOIN Location l ON s.location_id = l.location_id
WHERE s.status = 'ACTIVE';

-- View: Latest Readings per Sensor
CREATE VIEW LatestReadingsView AS
SELECT 
    s.sensor_id,
    s.model,
    st.name AS sensor_type,
    l.area_name,
    r.reading_value,
    r.reading_timestamp
FROM Sensor s
JOIN SensorType st ON s.type_id = st.type_id
JOIN Location l ON s.location_id = l.location_id
LEFT JOIN Reading r ON s.sensor_id = r.sensor_id
WHERE r.reading_timestamp = (
    SELECT MAX(reading_timestamp)
    FROM Reading
    WHERE sensor_id = s.sensor_id
)
OR r.reading_id IS NULL;

-- View: Maintenance Statistics
CREATE VIEW MaintenanceStatsView AS
SELECT 
    s.sensor_id,
    s.model,
    st.name AS sensor_type,
    COUNT(m.maintenance_id) AS maintenance_count,
    MAX(m.event_date) AS last_maintenance,
    GROUP_CONCAT(DISTINCT m.event_type) AS event_types
FROM Sensor s
JOIN SensorType st ON s.type_id = st.type_id
LEFT JOIN MaintenanceEvent m ON s.sensor_id = m.sensor_id
GROUP BY s.sensor_id;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_sensor_status ON Sensor(status);
CREATE INDEX idx_sensor_type ON Sensor(type_id);
CREATE INDEX idx_sensor_location ON Sensor(location_id);
CREATE INDEX idx_reading_sensor ON Reading(sensor_id);
CREATE INDEX idx_maintenance_sensor ON MaintenanceEvent(sensor_id);
CREATE INDEX idx_maintenance_tech ON MaintenanceEvent(tech_id);
CREATE INDEX idx_maintenance_date ON MaintenanceEvent(event_date);

-- =====================================================
-- GRANT PERMISSIONS (Optional - adjust as needed)
-- =====================================================

-- GRANT ALL PRIVILEGES ON microclimate_grid.* TO 'flask_user'@'localhost';
-- FLUSH PRIVILEGES;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify data insertion
SELECT 'User Count:', COUNT(*) FROM User;
SELECT 'SensorType Count:', COUNT(*) FROM SensorType;
SELECT 'Location Count:', COUNT(*) FROM Location;
SELECT 'Sensor Count:', COUNT(*) FROM Sensor;
SELECT 'Reading Count:', COUNT(*) FROM Reading;
SELECT 'Technician Count:', COUNT(*) FROM Technician;
SELECT 'MaintenanceEvent Count:', COUNT(*) FROM MaintenanceEvent;

-- Display summary
SELECT 'Database setup completed successfully!' AS Status;
