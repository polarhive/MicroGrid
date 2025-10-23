# User Requirements Specification (URS)
## Microclimate Sensor Grid Management System

**Project**: UE23CS351A Database Management Systems Mini Project  
**System Name**: Microclimate Sensor Grid Management System  
**Date**: October 2025  
**Version**: 1.0

---

## 1. Introduction

### 1.1 Purpose
The Microclimate Sensor Grid Management System is designed to monitor, manage, and analyze environmental data collected from a distributed network of sensors across multiple geographic locations. The system provides comprehensive tools for sensor management, data collection, maintenance tracking, and analytical reporting.

### 1.2 Scope
This system encompasses:
- **Sensor Management**: Registration, configuration, and monitoring of environmental sensors
- **Data Collection**: Recording and storage of sensor readings
- **Maintenance Tracking**: Logging and scheduling of sensor maintenance activities
- **Personnel Management**: Managing technicians and their assignments
- **Location Management**: Geographic mapping of sensor deployments
- **Analytics & Reporting**: Data visualization and insights generation

### 1.3 Target Users
- **System Administrators**: Overall system management and configuration
- **Field Technicians**: Sensor installation and maintenance
- **Data Scientists**: Analysis of environmental data
- **Operations Managers**: Monitoring system health and performance
- **Researchers**: Access to historical environmental data

### 1.4 Definitions and Acronyms
- **CRUD**: Create, Read, Update, Delete operations
- **IoT**: Internet of Things
- **hPa**: Hectopascal (unit of pressure)
- **W/m²**: Watts per square meter (unit of solar radiation)

---

## 2. System Overview

### 2.1 System Context
The Microclimate Sensor Grid Management System serves as a centralized platform for managing environmental monitoring infrastructure. It integrates data from various sensor types deployed across different locations to provide real-time and historical insights into microclimate conditions.

### 2.2 System Architecture
- **Frontend**: Web-based interface using Bootstrap 5 for responsive design
- **Backend**: Flask (Python) web framework
- **Database**: MySQL 8.0+ with stored procedures and triggers
- **ORM**: SQLAlchemy for database abstraction
- **Deployment**: Standalone web server accessible via browser

---

## 3. Functional Requirements

### 3.1 Sensor Type Management

#### FR-1.1: Create Sensor Type
- **Description**: System shall allow users to define new sensor types
- **Inputs**: Name (required), Description (optional)
- **Outputs**: Confirmation message, unique type_id
- **Business Rules**: Name must be unique
- **Priority**: High

#### FR-1.2: View Sensor Types
- **Description**: System shall display list of all sensor types
- **Inputs**: Optional search query
- **Outputs**: Paginated list with name, description, creation date
- **Priority**: High

#### FR-1.3: Update Sensor Type
- **Description**: System shall allow editing of sensor type details
- **Inputs**: type_id, updated name/description
- **Outputs**: Confirmation message
- **Business Rules**: Cannot modify if sensors are using this type
- **Priority**: Medium

#### FR-1.4: Delete Sensor Type
- **Description**: System shall allow deletion of unused sensor types
- **Inputs**: type_id
- **Outputs**: Confirmation or error message
- **Business Rules**: Cannot delete if sensors reference this type
- **Priority**: Medium

### 3.2 Location Management

#### FR-2.1: Register Location
- **Description**: System shall allow registration of sensor deployment locations
- **Inputs**: Area name, Latitude (required), Longitude (required), Elevation (optional)
- **Outputs**: Confirmation message, unique location_id
- **Business Rules**: 
  - Latitude/Longitude combination must be unique
  - Latitude: -90 to 90 degrees
  - Longitude: -180 to 180 degrees
- **Priority**: High

#### FR-2.2: View Locations
- **Description**: System shall display all registered locations
- **Inputs**: Optional search query
- **Outputs**: List with coordinates and elevation
- **Priority**: High

#### FR-2.3: Update Location
- **Description**: System shall allow editing of location details
- **Inputs**: location_id, updated information
- **Outputs**: Confirmation message
- **Priority**: Medium

#### FR-2.4: Delete Location
- **Description**: System shall allow deletion of unused locations
- **Inputs**: location_id
- **Outputs**: Confirmation or error message
- **Business Rules**: Cannot delete if sensors are deployed at this location
- **Priority**: Low

### 3.3 Sensor Management

#### FR-3.1: Register Sensor
- **Description**: System shall allow registration of new sensors
- **Inputs**: 
  - Model (required)
  - Sensor Type (required)
  - Location (required)
  - Installation Date (required)
  - Status (ACTIVE/INACTIVE/MAINTENANCE)
- **Outputs**: Confirmation message, unique sensor_id
- **Priority**: High

#### FR-3.2: View Sensors
- **Description**: System shall display all registered sensors
- **Inputs**: Optional filters (status, type, location, search query)
- **Outputs**: Filtered list with all sensor details
- **Priority**: High

#### FR-3.3: Update Sensor
- **Description**: System shall allow updating sensor information
- **Inputs**: sensor_id, updated fields
- **Outputs**: Confirmation message
- **Business Rules**: Status changes are logged automatically
- **Priority**: High

#### FR-3.4: Delete Sensor
- **Description**: System shall allow sensor deletion
- **Inputs**: sensor_id
- **Outputs**: Confirmation message
- **Business Rules**: Cascades to delete all readings and maintenance events
- **Priority**: Medium

#### FR-3.5: View Sensor Readings
- **Description**: System shall display all readings for a specific sensor
- **Inputs**: sensor_id
- **Outputs**: List of readings with timestamps and values
- **Business Rules**: Uses stored procedure GetSensorReadings()
- **Priority**: High

### 3.4 Reading Management

#### FR-4.1: Record Reading
- **Description**: System shall allow manual recording of sensor readings
- **Inputs**: 
  - Sensor (required)
  - Reading Value (required, decimal)
  - Timestamp (required)
- **Outputs**: Confirmation message, unique reading_id
- **Business Rules**: Timestamp cannot be in the future
- **Priority**: High

#### FR-4.2: View Readings
- **Description**: System shall display all sensor readings
- **Inputs**: Optional sensor filter, pagination parameters
- **Outputs**: Paginated list (50 per page) with sensor details
- **Priority**: High

#### FR-4.3: Update Reading
- **Description**: System shall allow correction of reading data
- **Inputs**: reading_id, updated values
- **Outputs**: Confirmation message
- **Priority**: Medium

#### FR-4.4: Delete Reading
- **Description**: System shall allow deletion of erroneous readings
- **Inputs**: reading_id
- **Outputs**: Confirmation message
- **Priority**: Low

### 3.5 Technician Management

#### FR-5.1: Register Technician
- **Description**: System shall allow registration of maintenance personnel
- **Inputs**: 
  - Name (required)
  - Contact Number (optional, 10 digits)
  - Specialization (optional)
- **Outputs**: Confirmation message, unique tech_id
- **Priority**: Medium

#### FR-5.2: View Technicians
- **Description**: System shall display all registered technicians
- **Inputs**: Optional search query
- **Outputs**: List with maintenance count for each technician
- **Priority**: Medium

#### FR-5.3: Update Technician
- **Description**: System shall allow updating technician information
- **Inputs**: tech_id, updated fields
- **Outputs**: Confirmation message
- **Priority**: Medium

#### FR-5.4: Delete Technician
- **Description**: System shall allow deletion of technician records
- **Inputs**: tech_id
- **Outputs**: Confirmation or error message
- **Business Rules**: Cannot delete if maintenance records exist
- **Priority**: Low

### 3.6 Maintenance Event Management

#### FR-6.1: Log Maintenance Event
- **Description**: System shall allow logging of maintenance activities
- **Inputs**: 
  - Sensor (required)
  - Technician (required)
  - Event Type (CALIBRATION/REPAIR/REPLACEMENT)
  - Event Date (required)
  - Notes (optional)
- **Outputs**: Confirmation message, unique maintenance_id
- **Business Rules**: 
  - REPAIR/REPLACEMENT events automatically set sensor to MAINTENANCE status
  - Trigger: after_maintenance_insert
- **Priority**: High

#### FR-6.2: View Maintenance Events
- **Description**: System shall display all maintenance events
- **Inputs**: Optional filters (sensor, technician, event type)
- **Outputs**: Filtered list of maintenance events
- **Priority**: High

#### FR-6.3: Update Maintenance Event
- **Description**: System shall allow editing of maintenance records
- **Inputs**: maintenance_id, updated fields
- **Outputs**: Confirmation message
- **Priority**: Medium

#### FR-6.4: Delete Maintenance Event
- **Description**: System shall allow deletion of maintenance records
- **Inputs**: maintenance_id
- **Outputs**: Confirmation message
- **Priority**: Low

### 3.7 Dashboard & Analytics

#### FR-7.1: Display Dashboard
- **Description**: System shall provide overview dashboard
- **Outputs**:
  - Total sensor count
  - Active sensor count
  - Total readings count
  - Total locations
  - Total technicians
  - Total maintenance events
  - Recent 10 readings
  - Maintenance events by type
  - Average readings by sensor type
- **Priority**: High

#### FR-7.2: Generate Reports
- **Description**: System shall provide analytics and reports
- **Outputs**:
  - Sensor status distribution
  - Maintenance summary (via stored procedure)
  - Average readings by area and sensor type (complex JOIN)
  - Top technicians by maintenance count (via stored procedure)
  - Recent sensor status changes (from trigger log)
- **Business Rules**: Uses stored procedures and complex queries
- **Priority**: High

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### NFR-1.1: Response Time
- System shall respond to user actions within 2 seconds under normal load
- Database queries shall execute within 1 second for 95% of requests

#### NFR-1.2: Scalability
- System shall support up to 10,000 sensors
- System shall handle up to 1 million readings
- Database shall support concurrent access by up to 50 users

### 4.2 Reliability Requirements

#### NFR-2.1: Availability
- System shall maintain 99% uptime during business hours
- Database backups shall be performed daily

#### NFR-2.2: Data Integrity
- All database operations shall maintain ACID properties
- Foreign key constraints shall prevent orphaned records
- Triggers shall automatically log important events

### 4.3 Usability Requirements

#### NFR-3.1: User Interface
- Interface shall be responsive and work on desktop, tablet, and mobile
- Interface shall use Bootstrap 5 for consistent styling
- All actions shall provide clear feedback messages

#### NFR-3.2: Accessibility
- Interface shall be navigable using keyboard
- Error messages shall be clear and actionable
- Forms shall include validation with helpful error messages

### 4.4 Security Requirements

#### NFR-4.1: Data Protection
- Database credentials shall be stored in environment variables
- SQL injection shall be prevented through parameterized queries
- Sensitive operations shall require confirmation

#### NFR-4.2: Input Validation
- All user inputs shall be validated on both client and server side
- Date/time inputs shall be validated for logical consistency
- Numeric inputs shall be validated for range and format

### 4.5 Maintainability Requirements

#### NFR-5.1: Code Quality
- Code shall follow PEP 8 style guidelines for Python
- Database schema shall be properly normalized (3NF)
- All functions shall have clear, descriptive names

#### NFR-5.2: Documentation
- Code shall include inline comments for complex logic
- README shall provide clear setup instructions
- Database schema shall be documented with ER diagram

---

## 5. Database Requirements

### 5.1 Data Storage

#### DR-1.1: Tables
System shall maintain 7 tables:
1. SensorType
2. Location
3. Sensor
4. Reading
5. Technician
6. MaintenanceEvent
7. SensorStatusLog (auto-populated by trigger)

#### DR-1.2: Data Types
- Integer IDs with auto-increment
- Decimal for precise measurements
- ENUM for constrained values
- DateTime for timestamps
- Text for descriptions and notes

### 5.2 Data Integrity

#### DR-2.1: Constraints
- Primary keys on all tables
- Foreign keys with appropriate cascade/restrict rules
- Unique constraint on Location coordinates
- NOT NULL on essential fields

#### DR-2.2: Triggers
1. before_sensor_update: Log status changes
2. after_maintenance_insert: Update sensor status
3. before_reading_insert: Validate timestamp

### 5.3 Stored Procedures

#### DR-3.1: Required Procedures
1. GetSensorReadings(sensor_id)
2. GetMaintenanceSummary()
3. GetLocationStatistics(location_id)
4. GetTopTechnicians(limit)
5. GetAvgReadingsBySensorType()

### 5.4 Views

#### DR-4.1: Predefined Views
1. ActiveSensorsView
2. LatestReadingsView
3. MaintenanceStatsView

---

## 6. Interface Requirements

### 6.1 User Interface

#### UI-1.1: Navigation
- Persistent navigation bar with links to all sections
- Breadcrumb navigation where applicable
- Quick action buttons on dashboard

#### UI-1.2: Forms
- Clear labels and placeholders
- Required field indicators
- Inline validation
- Submit and cancel buttons

#### UI-1.3: Data Display
- Sortable and filterable tables
- Pagination for large datasets
- Search functionality
- Export capabilities

### 6.2 API Interface (Optional Future Enhancement)

#### API-1.1: RESTful Endpoints
- GET /api/sensors/:id - Retrieve sensor details
- GET /api/sensors/:id/latest-reading - Get latest reading

---

## 7. Constraints

### 7.1 Technical Constraints
- Must use MySQL 8.0 or higher
- Must use Flask web framework
- Must use SQLAlchemy ORM
- Must use Bootstrap 5 for frontend

### 7.2 Business Constraints
- Cannot delete sensor types in use
- Cannot delete locations with deployed sensors
- Cannot delete technicians with maintenance records
- Sensor status must be ACTIVE, INACTIVE, or MAINTENANCE

---

## 8. Assumptions and Dependencies

### 8.1 Assumptions
- Users have basic computer literacy
- Users have access to modern web browsers
- MySQL server is properly configured
- Python 3.8+ is available

### 8.2 Dependencies
- MySQL database server
- Python packages: Flask, SQLAlchemy, PyMySQL, python-dotenv
- Web browser with JavaScript enabled
- Network connectivity for Bootstrap CDN

---

## 9. Future Enhancements

### 9.1 Planned Features
- Real-time data ingestion from IoT sensors
- Automated alerting for abnormal readings
- Advanced data visualization with charts
- Mobile application
- User authentication and role-based access
- RESTful API for third-party integration
- Automated report generation and email delivery
- Predictive maintenance using machine learning

### 9.2 Scalability Improvements
- Implement caching (Redis)
- Database query optimization
- Load balancing for high traffic
- Microservices architecture

---

## 10. Acceptance Criteria

### 10.1 Functionality
- ✓ All CRUD operations work for all 6 main tables
- ✓ Dashboard displays accurate statistics
- ✓ Filters and search work correctly
- ✓ Triggers automatically log status changes
- ✓ Stored procedures return correct results
- ✓ Complex JOIN queries execute successfully

### 10.2 Quality
- ✓ No SQL injection vulnerabilities
- ✓ All forms validate input
- ✓ Error handling prevents crashes
- ✓ Responsive design works on all devices
- ✓ Database maintains referential integrity

### 10.3 Documentation
- ✓ README with setup instructions
- ✓ ER diagram with relationships
- ✓ User Requirements Specification
- ✓ SQL schema with sample data
- ✓ Screenshots of all CRUD operations

---

**Prepared by**: Student Name  
**Roll Number**: Your Roll Number  
**Course**: UE23CS351A - Database Management Systems  
**Institution**: PESU University  
**Date**: October 2025
