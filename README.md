# Microclimate Sensor Grid Management System

A comprehensive Flask web application for managing a network of microclimate sensors, their readings, locations, and maintenance events.

## Project Overview

This project is developed as per **UE23CS351A Mini Project Guidelines** and provides a complete CRUD interface for managing:
- Sensor Types
- Locations
- Sensors
- Readings
- Technicians
- Maintenance Events

## Features

- **Full CRUD Operations** for all entities
- **Dashboard** with real-time statistics
- **Search & Filter** capabilities for sensors
- **Reports & Analytics** with complex SQL queries
- **Stored Procedures & Triggers** for automated operations
- **Responsive UI** using Bootstrap 5
- **RESTful API** architecture

## Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: MySQL 8.0+
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Environment Management**: python-dotenv

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
cd /path/to/your/workspace
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your MySQL credentials:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=microclimate_grid
SECRET_KEY=your_secret_key
```

### Step 5: Setup Database

1. **Login to MySQL:**
   ```bash
   mysql -u root -p
   ```

2. **Create Database and Import Schema:**
   ```sql
   CREATE DATABASE microclimate_grid;
   exit;
   ```

3. **Import the schema with sample data:**
   ```bash
   mysql -u root -p microclimate_grid < database/schema.sql
   ```

### Step 6: Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Project Structure

```
MicroGrid/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── database/
│   ├── schema.sql        # Complete database schema
│   └── dump.sql          # Database dump with data
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Dashboard
│   ├── sensor_types/     # SensorType CRUD
│   ├── locations/        # Location CRUD
│   ├── sensors/          # Sensor CRUD
│   ├── readings/         # Reading CRUD
│   ├── technicians/      # Technician CRUD
│   ├── maintenance/      # Maintenance CRUD
│   └── reports/          # Reports & Analytics
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── script.js     # Custom JavaScript
└── screenshots/          # Application screenshots
```

## Database Schema

The application uses 6 main tables:

1. **SensorType** - Types of sensors (Temperature, Humidity, etc.)
2. **Location** - Geographic locations with coordinates
3. **Sensor** - Individual sensor devices
4. **Reading** - Sensor measurements
5. **Technician** - Maintenance personnel
6. **MaintenanceEvent** - Maintenance activities

See `database/schema.sql` for complete schema including triggers and stored procedures.

## Usage

### Dashboard
- Navigate to `/` to view the main dashboard
- View statistics on active sensors, readings, and maintenance

### CRUD Operations
- **Sensor Types**: `/sensor-types`
- **Locations**: `/locations`
- **Sensors**: `/sensors`
- **Readings**: `/readings`
- **Technicians**: `/technicians`
- **Maintenance**: `/maintenance`

### Reports & Analytics
- Navigate to `/reports` for advanced analytics
- View aggregate data, joins, and complex queries

### Search & Filter
- Use search bars on list pages
- Filter sensors by type, status, and location

## Key Features Implemented

### Stored Procedures
- `GetSensorReadings(sensor_id)` - Fetch all readings for a sensor
- `GetMaintenanceSummary()` - Summary of maintenance events

### Triggers
- `before_sensor_update` - Log status changes
- `after_maintenance_insert` - Update maintenance timestamp

### Complex Queries
- Sensor readings by location
- Technician performance metrics
- Average readings per sensor type
- Maintenance frequency analysis

## Security Notes

- Never commit `.env` file
- Change `SECRET_KEY` in production
- Use strong database passwords
- Implement proper authentication for production

## Documentation

Complete documentation available in `documentation/` folder:
- ER Diagram
- User Requirements Specification
- API Documentation
- Screenshots

## Acknowledgments

- PESU University
- UE23CS351A Database Management Systems TAs
- Flask Documentation
- Bootstrap Framework

---

**Last Updated**: October 2025
