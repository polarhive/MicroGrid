# Setup and Testing Guide

## Quick Start Guide

Follow these steps to set up and run the Microclimate Sensor Grid Management System.

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python3 --version
   ```

2. **MySQL 8.0+** installed and running
   ```bash
   mysql --version
   ```

3. **pip** package manager
   ```bash
   pip3 --version
   ```

4. **Git** (optional, for cloning)
   ```bash
   git --version
   ```

---

## Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd /Users/polarhive/.local/repos/pesu/MicroGrid
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed Flask-3.0.0 Flask-SQLAlchemy-3.1.1 PyMySQL-1.1.0 ...
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

Update the following in `.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=microclimate_grid
SECRET_KEY=your_secret_key_here
```

**Important**: Replace `your_mysql_password_here` with your actual MySQL password!

### Step 5: Create Database and Import Schema

#### Option A: Using MySQL Command Line

```bash
# Login to MySQL
mysql -u root -p

# In MySQL prompt:
CREATE DATABASE microclimate_grid;
exit;

# Import schema with sample data
mysql -u root -p microclimate_grid < database/schema.sql
```

#### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Go to File → Run SQL Script
4. Select `database/schema.sql`
5. Execute the script

### Step 6: Verify Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Switch to database
USE microclimate_grid;

# Verify tables
SHOW TABLES;

# Should show:
# Location
# MaintenanceEvent
# Reading
# Sensor
# SensorStatusLog
# SensorType
# Technician

# Check sample data
SELECT COUNT(*) FROM Sensor;
# Should return 15

SELECT COUNT(*) FROM Reading;
# Should return multiple readings

exit;
```

### Step 7: Run the Application

```bash
# Make sure virtual environment is activated
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://0.0.0.0:5000
```

### Step 8: Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the dashboard with statistics!

---

## Testing CRUD Operations

### Test 1: Sensor Types

1. Navigate to **Sensor Types** from menu
2. Click **Add New Type**
3. Enter:
   - Name: `Air Quality`
   - Description: `Measures PM2.5 and PM10 levels`
4. Click **Save**
5. Verify it appears in the list
6. Click **Edit** icon
7. Update description
8. Click **Save**
9. Verify changes

### Test 2: Locations

1. Navigate to **Locations**
2. Click **Add New Location**
3. Enter:
   - Area Name: `Test Location`
   - Latitude: `12.9716`
   - Longitude: `77.5946`
   - Elevation: `920.00`
4. Click **Save**
5. Verify it appears in the list

### Test 3: Sensors

1. Navigate to **Sensors**
2. Click **Add New Sensor**
3. Fill in all fields
4. Click **Save**
5. Use filters to search by:
   - Status: Active
   - Type: Temperature
   - Location: PESU Campus North
6. Click on sensor to view readings

### Test 4: Readings

1. Navigate to **Readings**
2. Click **Record New Reading**
3. Select a sensor
4. Enter reading value
5. Select timestamp
6. Click **Save**
7. Verify it appears in the list
8. Filter by sensor

### Test 5: Technicians

1. Navigate to **Technicians**
2. Click **Add New Technician**
3. Enter:
   - Name: `Test Technician`
   - Contact: `9876543210`
   - Specialization: `General`
4. Click **Save**
5. Verify maintenance count shows 0

### Test 6: Maintenance

1. Navigate to **Maintenance**
2. Click **Log New Event**
3. Select a sensor
4. Select a technician
5. Choose event type: **CALIBRATION**
6. Select date
7. Add notes
8. Click **Save**
9. Verify sensor status changes if REPAIR/REPLACEMENT

### Test 7: Reports

1. Navigate to **Reports**
2. Verify all sections load:
   - Sensor Status Distribution
   - Maintenance Summary (Stored Procedure)
   - Average Readings by Area (Complex JOIN)
   - Top Technicians (Stored Procedure)
   - Recent Status Changes (Trigger Log)

---

## Testing Database Features

### Test Stored Procedures

```sql
-- In MySQL:
USE microclimate_grid;

-- Test GetSensorReadings
CALL GetSensorReadings(1);

-- Test GetMaintenanceSummary
CALL GetMaintenanceSummary();

-- Test GetTopTechnicians
CALL GetTopTechnicians(5);

-- Test GetAvgReadingsBySensorType
CALL GetAvgReadingsBySensorType();
```

### Test Triggers

```sql
-- Test before_sensor_update trigger
UPDATE Sensor SET status = 'MAINTENANCE' WHERE sensor_id = 1;

-- Check log
SELECT * FROM SensorStatusLog ORDER BY change_timestamp DESC LIMIT 5;

-- Test after_maintenance_insert trigger
INSERT INTO MaintenanceEvent (sensor_id, tech_id, event_type, event_date, notes)
VALUES (2, 1, 'REPAIR', NOW(), 'Test repair event');

-- Check sensor status changed
SELECT sensor_id, model, status FROM Sensor WHERE sensor_id = 2;
```

### Test Views

```sql
-- Test ActiveSensorsView
SELECT * FROM ActiveSensorsView LIMIT 10;

-- Test LatestReadingsView
SELECT * FROM LatestReadingsView LIMIT 10;

-- Test MaintenanceStatsView
SELECT * FROM MaintenanceStatsView LIMIT 10;
```

---

## Troubleshooting

### Issue: "Access denied for user"

**Solution**: Check MySQL credentials in `.env` file

```bash
# Test MySQL connection
mysql -u root -p
```

### Issue: "No module named 'flask'"

**Solution**: Activate virtual environment and install dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Can't connect to MySQL server"

**Solution**: Ensure MySQL is running

```bash
# macOS
brew services start mysql

# Linux
sudo systemctl start mysql

# Windows
net start MySQL80
```

### Issue: "Database doesn't exist"

**Solution**: Create database first

```bash
mysql -u root -p -e "CREATE DATABASE microclimate_grid;"
```

### Issue: Port 5000 already in use

**Solution**: Kill process or use different port

```bash
# macOS/Linux - find process
lsof -ti:5000

# Kill process
kill -9 <PID>

# Or run on different port
python app.py --port 5001
```

### Issue: "SQLALCHEMY_DATABASE_URI is not set"

**Solution**: Ensure `.env` file exists and is properly formatted

```bash
# Verify .env exists
ls -la .env

# Check contents
cat .env
```

---

## Common Commands

### Start Application
```bash
source venv/bin/activate  # Activate virtual environment
python app.py            # Start Flask app
```

### Stop Application
```
Press Ctrl+C in terminal
```

### Reset Database
```bash
mysql -u root -p microclimate_grid < database/schema.sql
```

### Create Database Backup
```bash
mysqldump -u root -p microclimate_grid > database/dump.sql
```

### View Logs
```bash
# Flask prints to console
# Check terminal where app is running
```

---

## Performance Testing

### Load Test with Sample Data

```sql
-- Generate 1000 sample readings
DELIMITER //
CREATE PROCEDURE GenerateTestReadings(IN count INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    WHILE i < count DO
        INSERT INTO Reading (sensor_id, reading_value, reading_timestamp)
        VALUES (
            FLOOR(1 + RAND() * 15),
            ROUND(RAND() * 100, 2),
            DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 365) DAY)
        );
        SET i = i + 1;
    END WHILE;
END//
DELIMITER ;

-- Generate test data
CALL GenerateTestReadings(1000);
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Change `FLASK_ENV=production` in `.env`
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use production-grade database server
- [ ] Enable HTTPS
- [ ] Implement authentication
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure firewall rules
- [ ] Remove debug mode
- [ ] Set appropriate file permissions

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)

---

## Support

For issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Verify database connection
4. Check Python/MySQL versions
5. Review `.env` configuration

---

**Happy Coding! 🚀**
