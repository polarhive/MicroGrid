# Screenshots Documentation

## Application Screenshots

This directory contains screenshots demonstrating all CRUD operations and features of the Microclimate Sensor Grid Management System.

### Required Screenshots

#### 1. Dashboard
- [ ] `01_dashboard.png` - Main dashboard showing statistics and quick actions

#### 2. Sensor Types
- [ ] `02_sensor_types_list.png` - List of all sensor types
- [ ] `03_sensor_type_create.png` - Create new sensor type form
- [ ] `04_sensor_type_edit.png` - Edit sensor type form
- [ ] `05_sensor_type_delete.png` - Delete confirmation dialog

#### 3. Locations
- [ ] `06_locations_list.png` - List of all locations
- [ ] `07_location_create.png` - Create new location form
- [ ] `08_location_edit.png` - Edit location form
- [ ] `09_location_delete.png` - Delete confirmation

#### 4. Sensors
- [ ] `10_sensors_list.png` - List of all sensors with filters
- [ ] `11_sensors_filtered.png` - Sensors list with applied filters
- [ ] `12_sensor_create.png` - Create new sensor form
- [ ] `13_sensor_edit.png` - Edit sensor form
- [ ] `14_sensor_readings.png` - View readings for specific sensor
- [ ] `15_sensor_delete.png` - Delete confirmation

#### 5. Readings
- [ ] `16_readings_list.png` - List of all readings with pagination
- [ ] `17_reading_create.png` - Record new reading form
- [ ] `18_reading_edit.png` - Edit reading form
- [ ] `19_reading_delete.png` - Delete confirmation

#### 6. Technicians
- [ ] `20_technicians_list.png` - List of all technicians
- [ ] `21_technician_create.png` - Create new technician form
- [ ] `22_technician_edit.png` - Edit technician form
- [ ] `23_technician_delete.png` - Delete confirmation

#### 7. Maintenance Events
- [ ] `24_maintenance_list.png` - List of all maintenance events
- [ ] `25_maintenance_filtered.png` - Maintenance events with filters
- [ ] `26_maintenance_create.png` - Log new maintenance event form
- [ ] `27_maintenance_edit.png` - Edit maintenance event form
- [ ] `28_maintenance_delete.png` - Delete confirmation

#### 8. Reports & Analytics
- [ ] `29_reports_status_distribution.png` - Sensor status distribution chart
- [ ] `30_reports_maintenance_summary.png` - Maintenance summary (stored procedure)
- [ ] `31_reports_avg_readings.png` - Average readings by area and type (JOIN query)
- [ ] `32_reports_top_technicians.png` - Top technicians (stored procedure)
- [ ] `33_reports_status_changes.png` - Recent status changes (trigger log)

#### 9. Database Features
- [ ] `34_trigger_log.png` - SensorStatusLog table showing trigger results
- [ ] `35_stored_procedure.png` - Execution of stored procedure
- [ ] `36_database_schema.png` - MySQL Workbench schema diagram

#### 10. Error Handling
- [ ] `37_validation_error.png` - Form validation error
- [ ] `38_constraint_error.png` - Foreign key constraint error
- [ ] `39_success_message.png` - Success flash message

### How to Take Screenshots

1. **Setup Database**: Ensure database is populated with sample data
2. **Start Application**: Run `python app.py`
3. **Navigate**: Open `http://localhost:5000` in browser
4. **Capture**: Use screenshot tool to capture each screen
5. **Name**: Save with descriptive names as listed above
6. **Store**: Place all screenshots in this directory

### Screenshot Guidelines

- **Resolution**: 1920x1080 or higher preferred
- **Format**: PNG format for clarity
- **Content**: Show full browser window or focused content area
- **Data**: Include visible data in tables (sample records)
- **UI**: Ensure all UI elements are visible
- **Quality**: High quality, no compression artifacts

### Tools for Screenshots

**macOS:**
- Cmd+Shift+3 (Full screen)
- Cmd+Shift+4 (Selection)
- Cmd+Shift+5 (Advanced options)

**Windows:**
- Windows+Shift+S (Snipping tool)
- PrtScn (Full screen)

**Linux:**
- Gnome Screenshot
- Spectacle (KDE)
- Flameshot

### Submission Checklist

Before submitting, ensure:
- [ ] All 39 screenshots are captured
- [ ] Screenshots are clearly named
- [ ] All CRUD operations are demonstrated
- [ ] Database features (triggers, procedures) are shown
- [ ] Reports page shows all analytics
- [ ] Screenshots are high quality and readable

---

**Note**: This directory currently contains placeholder documentation. Add actual screenshots before final submission.
