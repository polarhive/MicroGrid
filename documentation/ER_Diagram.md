# Entity-Relationship Diagram

## Microclimate Sensor Grid Database

### ER Diagram (Text Representation)

```
┌─────────────────┐
│   SensorType    │
├─────────────────┤
│ PK: type_id     │
│    name         │
│    description  │
│    created_at   │
└────────┬────────┘
         │ 1
         │
         │ has
         │
         │ N
┌────────┴────────┐            ┌─────────────────┐
│     Sensor      │            │    Location     │
├─────────────────┤            ├─────────────────┤
│ PK: sensor_id   │            │ PK: location_id │
│    model        │            │    area_name    │
│    install_date │ N       1  │    latitude     │
│    status       ├────────────│    longitude    │
│ FK: type_id     │  located   │    elevation    │
│ FK: location_id │     at     │    created_at   │
│    created_at   │            └─────────────────┘
│    updated_at   │
└────┬───────┬────┘
     │ 1     │ 1
     │       │
     │       │ has
     │       │
     │ N     │ N
┌────┴───────┐     ┌──────────────────┐
│  Reading   │     │ MaintenanceEvent │
├────────────┤     ├──────────────────┤
│PK: reading_│     │PK: maintenance_id│
│    id      │     │ FK: sensor_id    │───┐
│FK: sensor_ │     │ FK: tech_id      │   │
│    id      │     │    event_type    │   │
│    reading_│     │    event_date    │   │
│    value   │     │    notes         │   │
│    reading_│     │    created_at    │   │
│    timestamp     └──────────────────┘   │
└────────────┘              │ N            │
                            │              │
                            │ performed by │
                            │              │
                            │ 1            │
                     ┌──────┴──────────┐   │
                     │   Technician    │   │
                     ├─────────────────┤   │
                     │ PK: tech_id     │   │
                     │    name         │   │
                     │    contact_no   │   │
                     │    specialization  │
                     │    created_at   │   │
                     └─────────────────┘   │
                                           │
                     ┌─────────────────────┘
                     │
          ┌──────────┴──────────┐
          │ SensorStatusLog     │
          ├─────────────────────┤
          │ PK: log_id          │
          │ FK: sensor_id       │
          │    old_status       │
          │    new_status       │
          │    change_timestamp │
          └─────────────────────┘
```

## Relationships

### 1. SensorType → Sensor (One-to-Many)
- **Relationship**: One sensor type can have many sensors
- **Cardinality**: 1:N
- **Foreign Key**: `Sensor.type_id` references `SensorType.type_id`
- **Constraint**: ON DELETE RESTRICT (Cannot delete sensor type if sensors exist)

### 2. Location → Sensor (One-to-Many)
- **Relationship**: One location can have many sensors
- **Cardinality**: 1:N
- **Foreign Key**: `Sensor.location_id` references `Location.location_id`
- **Constraint**: ON DELETE RESTRICT (Cannot delete location if sensors exist)
- **Unique Constraint**: (latitude, longitude) - Each coordinate pair is unique

### 3. Sensor → Reading (One-to-Many)
- **Relationship**: One sensor can have many readings
- **Cardinality**: 1:N
- **Foreign Key**: `Reading.sensor_id` references `Sensor.sensor_id`
- **Constraint**: ON DELETE CASCADE (Deleting sensor deletes all its readings)

### 4. Sensor → MaintenanceEvent (One-to-Many)
- **Relationship**: One sensor can have many maintenance events
- **Cardinality**: 1:N
- **Foreign Key**: `MaintenanceEvent.sensor_id` references `Sensor.sensor_id`
- **Constraint**: ON DELETE CASCADE (Deleting sensor deletes all its maintenance events)

### 5. Technician → MaintenanceEvent (One-to-Many)
- **Relationship**: One technician can perform many maintenance events
- **Cardinality**: 1:N
- **Foreign Key**: `MaintenanceEvent.tech_id` references `Technician.tech_id`
- **Constraint**: ON DELETE RESTRICT (Cannot delete technician if maintenance records exist)

### 6. Sensor → SensorStatusLog (One-to-Many)
- **Relationship**: One sensor can have many status change logs
- **Cardinality**: 1:N
- **Foreign Key**: `SensorStatusLog.sensor_id` references `Sensor.sensor_id`
- **Constraint**: ON DELETE CASCADE (Deleting sensor deletes all status logs)

## Entity Descriptions

### SensorType
Defines different types of sensors in the system.
- **Primary Key**: type_id
- **Attributes**: name, description
- **Examples**: Temperature, Humidity, Pressure, Wind Speed, Rainfall, Solar Radiation

### Location
Geographic locations where sensors are installed.
- **Primary Key**: location_id
- **Attributes**: area_name, latitude, longitude, elevation
- **Unique Constraint**: (latitude, longitude)
- **Examples**: PESU Campus North, Electronic City Phase 1

### Sensor
Individual sensor devices deployed in the field.
- **Primary Key**: sensor_id
- **Attributes**: model, install_date, status
- **Foreign Keys**: type_id (SensorType), location_id (Location)
- **Status Values**: ACTIVE, INACTIVE, MAINTENANCE

### Reading
Measurements recorded by sensors.
- **Primary Key**: reading_id (BIGINT for large data volumes)
- **Attributes**: reading_value, reading_timestamp
- **Foreign Key**: sensor_id (Sensor)
- **Index**: (sensor_id, reading_timestamp) for efficient queries

### Technician
Personnel who perform maintenance on sensors.
- **Primary Key**: tech_id
- **Attributes**: name, contact_no, specialization
- **Examples**: Temperature Sensors specialist, General Maintenance

### MaintenanceEvent
Records of maintenance activities performed on sensors.
- **Primary Key**: maintenance_id
- **Attributes**: event_type, event_date, notes
- **Foreign Keys**: sensor_id (Sensor), tech_id (Technician)
- **Event Types**: CALIBRATION, REPAIR, REPLACEMENT

### SensorStatusLog
Automatically maintained log of sensor status changes (populated by triggers).
- **Primary Key**: log_id
- **Attributes**: old_status, new_status, change_timestamp
- **Foreign Key**: sensor_id (Sensor)

## Normalization

### Current Normal Form: 3NF (Third Normal Form)

**1NF (First Normal Form):**
- ✓ All attributes contain atomic values
- ✓ Each row is unique (enforced by primary keys)
- ✓ No repeating groups

**2NF (Second Normal Form):**
- ✓ All non-key attributes are fully functionally dependent on the primary key
- ✓ No partial dependencies

**3NF (Third Normal Form):**
- ✓ No transitive dependencies
- ✓ All attributes depend only on the primary key
- ✓ Separate tables for entities with distinct purposes

## Database Constraints

### Primary Keys
- All tables have auto-incrementing primary keys
- Ensures unique identification of records

### Foreign Keys
- Maintain referential integrity
- Prevent orphaned records
- Support cascading deletes where appropriate

### Unique Constraints
- `Location(latitude, longitude)` - Prevents duplicate coordinates

### Check Constraints (via ENUM)
- `Sensor.status`: ACTIVE, INACTIVE, MAINTENANCE
- `MaintenanceEvent.event_type`: CALIBRATION, REPAIR, REPLACEMENT

### Not Null Constraints
- Essential fields like sensor_id, reading_value, timestamps are mandatory

## Indexes

### Performance Optimization
```sql
-- Sensor lookups by status, type, location
CREATE INDEX idx_sensor_status ON Sensor(status);
CREATE INDEX idx_sensor_type ON Sensor(type_id);
CREATE INDEX idx_sensor_location ON Sensor(location_id);

-- Reading queries by sensor and timestamp
CREATE INDEX idx_sensor_timestamp ON Reading(sensor_id, reading_timestamp);

-- Maintenance queries
CREATE INDEX idx_maintenance_sensor ON MaintenanceEvent(sensor_id);
CREATE INDEX idx_maintenance_tech ON MaintenanceEvent(tech_id);
CREATE INDEX idx_maintenance_date ON MaintenanceEvent(event_date);
```

## Triggers

### 1. before_sensor_update
- **Purpose**: Log sensor status changes
- **Action**: BEFORE UPDATE on Sensor
- **Logic**: When status changes, insert record into SensorStatusLog

### 2. after_maintenance_insert
- **Purpose**: Update sensor status after maintenance
- **Action**: AFTER INSERT on MaintenanceEvent
- **Logic**: If event_type is REPAIR or REPLACEMENT, set sensor status to MAINTENANCE

### 3. before_reading_insert
- **Purpose**: Validate reading timestamps
- **Action**: BEFORE INSERT on Reading
- **Logic**: Ensure reading_timestamp is not in the future

## Stored Procedures

### 1. GetSensorReadings(sensor_id)
Returns all readings for a specific sensor with sensor details.

### 2. GetMaintenanceSummary()
Provides aggregate statistics on maintenance events by type.

### 3. GetLocationStatistics(location_id)
Returns sensor and reading statistics for a specific location.

### 4. GetTopTechnicians(limit)
Lists technicians ranked by number of maintenance events performed.

### 5. GetAvgReadingsBySensorType()
Calculates average, min, max readings per sensor type.

## Views

### 1. ActiveSensorsView
Shows all active sensors with full details (type, location).

### 2. LatestReadingsView
Displays the most recent reading for each sensor.

### 3. MaintenanceStatsView
Aggregates maintenance statistics per sensor.

---

**Prepared for**: UE23CS351A Mini Project  
**Database**: microclimate_grid  
**DBMS**: MySQL 8.0+
