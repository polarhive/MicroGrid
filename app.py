from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from models import db, User, SensorType, Location, Sensor, Reading, Technician, MaintenanceEvent, SensorStatusLog
from sqlalchemy import func, text
from datetime import datetime
import os
import csv
from io import StringIO

def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

app = create_app(os.getenv('FLASK_ENV', 'development'))

# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('signup'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use another or log in.', 'danger')
            return redirect(url_for('signup'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/signup.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# =====================================================
# HOME & DASHBOARD ROUTES
# =====================================================

@app.route('/')
@login_required
def index():
    """Dashboard with statistics"""
    # Get statistics
    total_sensors = Sensor.query.count()
    active_sensors = Sensor.query.filter_by(status='ACTIVE').count()
    total_readings = Reading.query.count()
    total_locations = Location.query.count()
    total_technicians = Technician.query.count()
    total_maintenance = MaintenanceEvent.query.count()
    
    # Recent readings
    recent_readings = db.session.query(
        Reading, Sensor, SensorType, Location
    ).join(
        Sensor, Reading.sensor_id == Sensor.sensor_id
    ).join(
        SensorType, Sensor.type_id == SensorType.type_id
    ).join(
        Location, Sensor.location_id == Location.location_id
    ).order_by(
        Reading.reading_timestamp.desc()
    ).limit(10).all()
    
    # Maintenance events count by type
    maintenance_stats = db.session.query(
        MaintenanceEvent.event_type,
        func.count(MaintenanceEvent.maintenance_id).label('count')
    ).group_by(MaintenanceEvent.event_type).all()
    
    # Average readings by sensor type
    avg_readings = db.session.query(
        SensorType.name,
        func.avg(Reading.reading_value).label('avg_value'),
        func.count(Reading.reading_id).label('reading_count')
    ).join(
        Sensor, SensorType.type_id == Sensor.type_id
    ).join(
        Reading, Sensor.sensor_id == Reading.sensor_id
    ).group_by(SensorType.name).all()
    
    return render_template('index.html',
                         total_sensors=total_sensors,
                         active_sensors=active_sensors,
                         total_readings=total_readings,
                         total_locations=total_locations,
                         total_technicians=total_technicians,
                         total_maintenance=total_maintenance,
                         recent_readings=recent_readings,
                         maintenance_stats=maintenance_stats,
                         avg_readings=avg_readings)

# =====================================================
# SENSOR TYPE ROUTES
# =====================================================

@app.route('/sensor-types')
@login_required
def sensor_types_list():
    """List all sensor types"""
    search = request.args.get('search', '')
    
    query = SensorType.query
    if search:
        query = query.filter(SensorType.name.like(f'%{search}%'))
    
    sensor_types = query.order_by(SensorType.name).all()
    return render_template('sensor_types/list.html', sensor_types=sensor_types, search=search)

@app.route('/sensor-types/create', methods=['GET', 'POST'])
@login_required
def sensor_type_create():
    """Create a new sensor type"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        sensor_type = SensorType(name=name, description=description)
        db.session.add(sensor_type)
        db.session.commit()
        
        flash(f'Sensor type "{name}" created successfully!', 'success')
        return redirect(url_for('sensor_types_list'))
    
    return render_template('sensor_types/form.html')

@app.route('/sensor-types/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
def sensor_type_edit(type_id):
    """Edit a sensor type"""
    sensor_type = SensorType.query.get_or_404(type_id)
    
    if request.method == 'POST':
        sensor_type.name = request.form.get('name')
        sensor_type.description = request.form.get('description')
        
        db.session.commit()
        flash(f'Sensor type "{sensor_type.name}" updated successfully!', 'success')
        return redirect(url_for('sensor_types_list'))
    
    return render_template('sensor_types/form.html', sensor_type=sensor_type)

@app.route('/sensor-types/<int:type_id>/delete', methods=['POST'])
@login_required
def sensor_type_delete(type_id):
    """Delete a sensor type"""
    sensor_type = SensorType.query.get_or_404(type_id)
    
    try:
        db.session.delete(sensor_type)
        db.session.commit()
        flash(f'Sensor type "{sensor_type.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sensor type: {str(e)}', 'danger')
    
    return redirect(url_for('sensor_types_list'))

# =====================================================
# LOCATION ROUTES
# =====================================================

@app.route('/locations')
@login_required
def locations_list():
    """List all locations"""
    search = request.args.get('search', '')
    
    query = Location.query
    if search:
        query = query.filter(Location.area_name.like(f'%{search}%'))
    
    locations = query.order_by(Location.area_name).all()
    return render_template('locations/list.html', locations=locations, search=search)

@app.route('/locations/create', methods=['GET', 'POST'])
@login_required
def location_create():
    """Create a new location"""
    if request.method == 'POST':
        area_name = request.form.get('area_name')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        elevation = request.form.get('elevation', 0.0)
        
        location = Location(
            area_name=area_name,
            latitude=latitude,
            longitude=longitude,
            elevation=elevation
        )
        
        try:
            db.session.add(location)
            db.session.commit()
            flash(f'Location "{area_name}" created successfully!', 'success')
            return redirect(url_for('locations_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating location: {str(e)}', 'danger')
    
    return render_template('locations/form.html')

@app.route('/locations/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
def location_edit(location_id):
    """Edit a location"""
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        location.area_name = request.form.get('area_name')
        location.latitude = request.form.get('latitude')
        location.longitude = request.form.get('longitude')
        location.elevation = request.form.get('elevation', 0.0)
        
        try:
            db.session.commit()
            flash(f'Location "{location.area_name}" updated successfully!', 'success')
            return redirect(url_for('locations_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating location: {str(e)}', 'danger')
    
    return render_template('locations/form.html', location=location)

@app.route('/locations/<int:location_id>/delete', methods=['POST'])
@login_required
def location_delete(location_id):
    """Delete a location"""
    location = Location.query.get_or_404(location_id)
    
    try:
        db.session.delete(location)
        db.session.commit()
        flash(f'Location "{location.area_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting location: {str(e)}', 'danger')
    
    return redirect(url_for('locations_list'))

# =====================================================
# SENSOR ROUTES
# =====================================================

@app.route('/sensors')
@login_required
def sensors_list():
    """List all sensors with filtering"""
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    location_filter = request.args.get('location', '')
    
    query = Sensor.query
    
    if search:
        query = query.filter(Sensor.model.like(f'%{search}%'))
    
    if status_filter:
        query = query.filter(Sensor.status == status_filter)
    
    if type_filter:
        query = query.filter(Sensor.type_id == type_filter)
    
    if location_filter:
        query = query.filter(Sensor.location_id == location_filter)
    
    sensors = query.order_by(Sensor.sensor_id.desc()).all()
    
    # Get filter options
    sensor_types = SensorType.query.order_by(SensorType.name).all()
    locations = Location.query.order_by(Location.area_name).all()
    
    return render_template('sensors/list.html',
                         sensors=sensors,
                         sensor_types=sensor_types,
                         locations=locations,
                         search=search,
                         status_filter=status_filter,
                         type_filter=type_filter,
                         location_filter=location_filter)

@app.route('/sensors/create', methods=['GET', 'POST'])
@login_required
def sensor_create():
    """Create a new sensor"""
    if request.method == 'POST':
        model = request.form.get('model')
        install_date = request.form.get('install_date')
        status = request.form.get('status', 'ACTIVE')
        type_id = request.form.get('type_id')
        location_id = request.form.get('location_id')
        
        sensor = Sensor(
            model=model,
            install_date=datetime.strptime(install_date, '%Y-%m-%d').date(),
            status=status,
            type_id=type_id,
            location_id=location_id
        )
        
        db.session.add(sensor)
        db.session.commit()
        
        flash(f'Sensor "{model}" created successfully!', 'success')
        return redirect(url_for('sensors_list'))
    
    sensor_types = SensorType.query.order_by(SensorType.name).all()
    locations = Location.query.order_by(Location.area_name).all()
    
    return render_template('sensors/form.html',
                         sensor_types=sensor_types,
                         locations=locations)

@app.route('/sensors/<int:sensor_id>/edit', methods=['GET', 'POST'])
@login_required
def sensor_edit(sensor_id):
    """Edit a sensor"""
    sensor = Sensor.query.get_or_404(sensor_id)
    
    if request.method == 'POST':
        sensor.model = request.form.get('model')
        sensor.install_date = datetime.strptime(request.form.get('install_date'), '%Y-%m-%d').date()
        sensor.status = request.form.get('status')
        sensor.type_id = request.form.get('type_id')
        sensor.location_id = request.form.get('location_id')
        
        db.session.commit()
        flash(f'Sensor "{sensor.model}" updated successfully!', 'success')
        return redirect(url_for('sensors_list'))
    
    sensor_types = SensorType.query.order_by(SensorType.name).all()
    locations = Location.query.order_by(Location.area_name).all()
    
    return render_template('sensors/form.html',
                         sensor=sensor,
                         sensor_types=sensor_types,
                         locations=locations)

@app.route('/sensors/<int:sensor_id>/delete', methods=['POST'])
@login_required
def sensor_delete(sensor_id):
    """Delete a sensor"""
    sensor = Sensor.query.get_or_404(sensor_id)
    
    try:
        db.session.delete(sensor)
        db.session.commit()
        flash(f'Sensor "{sensor.model}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sensor: {str(e)}', 'danger')
    
    return redirect(url_for('sensors_list'))

@app.route('/sensors/<int:sensor_id>/readings')
@login_required
def sensor_readings(sensor_id):
    """View all readings for a specific sensor"""
    sensor = Sensor.query.get_or_404(sensor_id)
    
    # Call stored procedure
    result = db.session.execute(
        text('CALL GetSensorReadings(:sensor_id)'),
        {'sensor_id': sensor_id}
    )
    readings = result.fetchall()
    
    return render_template('sensors/readings.html',
                         sensor=sensor,
                         readings=readings)

# =====================================================
# READING ROUTES
# =====================================================

@app.route('/readings')
@login_required
def readings_list():
    """List all readings"""
    sensor_filter = request.args.get('sensor', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = db.session.query(
        Reading, Sensor, SensorType, Location
    ).join(
        Sensor, Reading.sensor_id == Sensor.sensor_id
    ).join(
        SensorType, Sensor.type_id == SensorType.type_id
    ).join(
        Location, Sensor.location_id == Location.location_id
    )
    
    if sensor_filter:
        query = query.filter(Reading.sensor_id == sensor_filter)
    
    query = query.order_by(Reading.reading_timestamp.desc())
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    readings = pagination.items
    
    sensors = Sensor.query.order_by(Sensor.model).all()
    
    return render_template('readings/list.html',
                         readings=readings,
                         sensors=sensors,
                         sensor_filter=sensor_filter,
                         pagination=pagination)

@app.route('/readings/create', methods=['GET', 'POST'])
@login_required
def reading_create():
    """Create a new reading"""
    if request.method == 'POST':
        sensor_id = request.form.get('sensor_id')
        reading_value = request.form.get('reading_value')
        reading_timestamp = request.form.get('reading_timestamp')
        
        reading = Reading(
            sensor_id=sensor_id,
            reading_value=reading_value,
            reading_timestamp=datetime.strptime(reading_timestamp, '%Y-%m-%dT%H:%M')
        )
        
        db.session.add(reading)
        db.session.commit()
        
        flash('Reading recorded successfully!', 'success')
        return redirect(url_for('readings_list'))
    
    sensors = Sensor.query.filter_by(status='ACTIVE').order_by(Sensor.model).all()
    
    return render_template('readings/form.html', sensors=sensors)

@app.route('/readings/<int:reading_id>/edit', methods=['GET', 'POST'])
@login_required
def reading_edit(reading_id):
    """Edit a reading"""
    reading = Reading.query.get_or_404(reading_id)
    
    if request.method == 'POST':
        reading.sensor_id = request.form.get('sensor_id')
        reading.reading_value = request.form.get('reading_value')
        reading.reading_timestamp = datetime.strptime(
            request.form.get('reading_timestamp'), '%Y-%m-%dT%H:%M'
        )
        
        db.session.commit()
        flash('Reading updated successfully!', 'success')
        return redirect(url_for('readings_list'))
    
    sensors = Sensor.query.order_by(Sensor.model).all()
    
    return render_template('readings/form.html',
                         reading=reading,
                         sensors=sensors)

@app.route('/readings/<int:reading_id>/delete', methods=['POST'])
@login_required
def reading_delete(reading_id):
    """Delete a reading"""
    reading = Reading.query.get_or_404(reading_id)
    
    db.session.delete(reading)
    db.session.commit()
    
    flash('Reading deleted successfully!', 'success')
    return redirect(url_for('readings_list'))

# =====================================================
# TECHNICIAN ROUTES
# =====================================================

@app.route('/technicians')
@login_required
def technicians_list():
    """List all technicians"""
    search = request.args.get('search', '')
    
    query = Technician.query
    if search:
        query = query.filter(Technician.name.like(f'%{search}%'))
    
    technicians = query.order_by(Technician.name).all()
    
    # Get maintenance count for each technician
    tech_stats = []
    for tech in technicians:
        maintenance_count = MaintenanceEvent.query.filter_by(tech_id=tech.tech_id).count()
        tech_stats.append((tech, maintenance_count))
    
    return render_template('technicians/list.html',
                         tech_stats=tech_stats,
                         search=search)

@app.route('/technicians/create', methods=['GET', 'POST'])
@login_required
def technician_create():
    """Create a new technician"""
    if request.method == 'POST':
        name = request.form.get('name')
        contact_no = request.form.get('contact_no')
        specialization = request.form.get('specialization')
        
        technician = Technician(
            name=name,
            contact_no=contact_no,
            specialization=specialization
        )
        
        db.session.add(technician)
        db.session.commit()
        
        flash(f'Technician "{name}" created successfully!', 'success')
        return redirect(url_for('technicians_list'))
    
    return render_template('technicians/form.html')

@app.route('/technicians/<int:tech_id>/edit', methods=['GET', 'POST'])
@login_required
def technician_edit(tech_id):
    """Edit a technician"""
    technician = Technician.query.get_or_404(tech_id)
    
    if request.method == 'POST':
        technician.name = request.form.get('name')
        technician.contact_no = request.form.get('contact_no')
        technician.specialization = request.form.get('specialization')
        
        db.session.commit()
        flash(f'Technician "{technician.name}" updated successfully!', 'success')
        return redirect(url_for('technicians_list'))
    
    return render_template('technicians/form.html', technician=technician)

@app.route('/technicians/<int:tech_id>/delete', methods=['POST'])
@login_required
def technician_delete(tech_id):
    """Delete a technician"""
    technician = Technician.query.get_or_404(tech_id)
    
    try:
        db.session.delete(technician)
        db.session.commit()
        flash(f'Technician "{technician.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting technician: {str(e)}', 'danger')
    
    return redirect(url_for('technicians_list'))

# =====================================================
# MAINTENANCE EVENT ROUTES
# =====================================================

@app.route('/maintenance')
@login_required
def maintenance_list():
    """List all maintenance events"""
    sensor_filter = request.args.get('sensor', '')
    tech_filter = request.args.get('tech', '')
    event_filter = request.args.get('event_type', '')
    
    query = MaintenanceEvent.query
    
    if sensor_filter:
        query = query.filter(MaintenanceEvent.sensor_id == sensor_filter)
    
    if tech_filter:
        query = query.filter(MaintenanceEvent.tech_id == tech_filter)
    
    if event_filter:
        query = query.filter(MaintenanceEvent.event_type == event_filter)
    
    maintenance_events = query.order_by(MaintenanceEvent.event_date.desc()).all()
    
    sensors = Sensor.query.order_by(Sensor.model).all()
    technicians = Technician.query.order_by(Technician.name).all()
    
    return render_template('maintenance/list.html',
                         maintenance_events=maintenance_events,
                         sensors=sensors,
                         technicians=technicians,
                         sensor_filter=sensor_filter,
                         tech_filter=tech_filter,
                         event_filter=event_filter)

@app.route('/maintenance/create', methods=['GET', 'POST'])
@login_required
def maintenance_create():
    """Create a new maintenance event"""
    if request.method == 'POST':
        sensor_id = request.form.get('sensor_id')
        tech_id = request.form.get('tech_id')
        event_type = request.form.get('event_type')
        event_date = request.form.get('event_date')
        notes = request.form.get('notes')
        
        maintenance = MaintenanceEvent(
            sensor_id=sensor_id,
            tech_id=tech_id,
            event_type=event_type,
            event_date=datetime.strptime(event_date, '%Y-%m-%dT%H:%M'),
            notes=notes
        )
        
        db.session.add(maintenance)
        db.session.commit()
        
        flash('Maintenance event created successfully!', 'success')
        return redirect(url_for('maintenance_list'))
    
    sensors = Sensor.query.order_by(Sensor.model).all()
    technicians = Technician.query.order_by(Technician.name).all()
    
    return render_template('maintenance/form.html',
                         sensors=sensors,
                         technicians=technicians)

@app.route('/maintenance/<int:maintenance_id>/edit', methods=['GET', 'POST'])
@login_required
def maintenance_edit(maintenance_id):
    """Edit a maintenance event"""
    maintenance = MaintenanceEvent.query.get_or_404(maintenance_id)
    
    if request.method == 'POST':
        maintenance.sensor_id = request.form.get('sensor_id')
        maintenance.tech_id = request.form.get('tech_id')
        maintenance.event_type = request.form.get('event_type')
        maintenance.event_date = datetime.strptime(
            request.form.get('event_date'), '%Y-%m-%dT%H:%M'
        )
        maintenance.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Maintenance event updated successfully!', 'success')
        return redirect(url_for('maintenance_list'))
    
    sensors = Sensor.query.order_by(Sensor.model).all()
    technicians = Technician.query.order_by(Technician.name).all()
    
    return render_template('maintenance/form.html',
                         maintenance=maintenance,
                         sensors=sensors,
                         technicians=technicians)

@app.route('/maintenance/<int:maintenance_id>/delete', methods=['POST'])
@login_required
def maintenance_delete(maintenance_id):
    """Delete a maintenance event"""
    maintenance = MaintenanceEvent.query.get_or_404(maintenance_id)
    
    db.session.delete(maintenance)
    db.session.commit()
    
    flash('Maintenance event deleted successfully!', 'success')
    return redirect(url_for('maintenance_list'))

# =====================================================
# REPORTS & ANALYTICS ROUTES
# =====================================================

@app.route('/reports')
@login_required
def reports():
    """Reports and analytics page"""
    # Average readings by area
    area_stats = db.session.query(
        Location.area_name,
        SensorType.name.label('sensor_type'),
        func.avg(Reading.reading_value).label('avg_value'),
        func.count(Reading.reading_id).label('reading_count')
    ).join(
        Sensor, Location.location_id == Sensor.location_id
    ).join(
        SensorType, Sensor.type_id == SensorType.type_id
    ).join(
        Reading, Sensor.sensor_id == Reading.sensor_id
    ).group_by(
        Location.area_name, SensorType.name
    ).all()
    
    # Top technicians by maintenance count
    result = db.session.execute(text('CALL GetTopTechnicians(10)'))
    top_technicians = result.fetchall()
    
    # Maintenance summary
    result2 = db.session.execute(text('CALL GetMaintenanceSummary()'))
    maintenance_summary = result2.fetchall()
    
    # Sensor status distribution
    status_dist = db.session.query(
        Sensor.status,
        func.count(Sensor.sensor_id).label('count')
    ).group_by(Sensor.status).all()
    
    # Recent status changes
    status_logs = db.session.query(
        SensorStatusLog, Sensor
    ).join(
        Sensor, SensorStatusLog.sensor_id == Sensor.sensor_id
    ).order_by(
        SensorStatusLog.change_timestamp.desc()
    ).limit(20).all()
    
    return render_template('reports/index.html',
                         area_stats=area_stats,
                         top_technicians=top_technicians,
                         maintenance_summary=maintenance_summary,
                         status_dist=status_dist,
                         status_logs=status_logs)

# =====================================================
# API ROUTES (Optional - for AJAX)
# =====================================================

@app.route('/api/sensors/<int:sensor_id>')
@login_required
def api_sensor(sensor_id):
    """Get sensor details as JSON"""
    sensor = Sensor.query.get_or_404(sensor_id)
    return jsonify(sensor.to_dict())

@app.route('/api/sensors/<int:sensor_id>/latest-reading')
@login_required
def api_latest_reading(sensor_id):
    """Get latest reading for a sensor"""
    reading = Reading.query.filter_by(
        sensor_id=sensor_id
    ).order_by(
        Reading.reading_timestamp.desc()
    ).first()
    
    if reading:
        return jsonify(reading.to_dict())
    return jsonify({'error': 'No readings found'}), 404

# =====================================================
# CSV EXPORT ROUTES
# =====================================================

@app.route('/export/sensors/csv')
@login_required
def export_sensors_csv():
    """Export all sensors to CSV"""
    # Get all sensors with related data
    sensors = db.session.query(
        Sensor, SensorType, Location
    ).join(
        SensorType, Sensor.type_id == SensorType.type_id
    ).join(
        Location, Sensor.location_id == Location.location_id
    ).all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['ID', 'Model', 'Type', 'Location', 'Latitude', 'Longitude', 
                     'Install Date', 'Status', 'Created At'])
    
    # Write data
    for sensor, sensor_type, location in sensors:
        writer.writerow([
            sensor.sensor_id,
            sensor.model,
            sensor_type.name,
            location.area_name,
            float(location.latitude),
            float(location.longitude),
            sensor.install_date.strftime('%Y-%m-%d'),
            sensor.status,
            sensor.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=sensors_export.csv'}
    )

@app.route('/export/readings/csv')
@login_required
def export_readings_csv():
    """Export all readings to CSV"""
    # Get all readings with related data
    readings = db.session.query(
        Reading, Sensor, SensorType, Location
    ).join(
        Sensor, Reading.sensor_id == Sensor.sensor_id
    ).join(
        SensorType, Sensor.type_id == SensorType.type_id
    ).join(
        Location, Sensor.location_id == Location.location_id
    ).order_by(Reading.reading_timestamp.desc()).limit(10000).all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['Reading ID', 'Sensor ID', 'Sensor Model', 'Sensor Type', 
                     'Location', 'Reading Value', 'Timestamp'])
    
    # Write data
    for reading, sensor, sensor_type, location in readings:
        writer.writerow([
            reading.reading_id,
            sensor.sensor_id,
            sensor.model,
            sensor_type.name,
            location.area_name,
            float(reading.reading_value),
            reading.reading_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=readings_export.csv'}
    )

@app.route('/export/locations/csv')
@login_required
def export_locations_csv():
    """Export all locations to CSV"""
    locations = Location.query.all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['ID', 'Area Name', 'Latitude', 'Longitude', 'Elevation (m)', 'Created At'])
    
    # Write data
    for location in locations:
        writer.writerow([
            location.location_id,
            location.area_name,
            float(location.latitude),
            float(location.longitude),
            float(location.elevation) if location.elevation else 0.0,
            location.created_at.strftime('%Y-%m-%d %H:%M:%S') if location.created_at else ''
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=locations_export.csv'}
    )

@app.route('/export/technicians/csv')
@login_required
def export_technicians_csv():
    """Export all technicians to CSV"""
    technicians = Technician.query.all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Contact Number', 'Specialization', 'Created At'])
    
    # Write data
    for tech in technicians:
        writer.writerow([
            tech.tech_id,
            tech.name,
            tech.contact_no or '',
            tech.specialization or '',
            tech.created_at.strftime('%Y-%m-%d %H:%M:%S') if tech.created_at else ''
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=technicians_export.csv'}
    )

@app.route('/export/maintenance/csv')
@login_required
def export_maintenance_csv():
    """Export all maintenance events to CSV"""
    maintenance_events = db.session.query(
        MaintenanceEvent, Sensor, Technician
    ).join(
        Sensor, MaintenanceEvent.sensor_id == Sensor.sensor_id
    ).join(
        Technician, MaintenanceEvent.tech_id == Technician.tech_id
    ).order_by(MaintenanceEvent.event_date.desc()).all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['ID', 'Sensor Model', 'Technician', 'Event Type', 
                     'Event Date', 'Notes', 'Created At'])
    
    # Write data
    for event, sensor, tech in maintenance_events:
        writer.writerow([
            event.maintenance_id,
            sensor.model,
            tech.name,
            event.event_type,
            event.event_date.strftime('%Y-%m-%d %H:%M:%S'),
            event.notes or '',
            event.created_at.strftime('%Y-%m-%d %H:%M:%S') if event.created_at else ''
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=maintenance_export.csv'}
    )

@app.route('/export/sensor-types/csv')
@login_required
def export_sensor_types_csv():
    """Export all sensor types to CSV"""
    sensor_types = SensorType.query.all()
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Description', 'Created At'])
    
    # Write data
    for st in sensor_types:
        writer.writerow([
            st.type_id,
            st.name,
            st.description or '',
            st.created_at.strftime('%Y-%m-%d %H:%M:%S') if st.created_at else ''
        ])
    
    # Create response
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=sensor_types_export.csv'}
    )

# =====================================================
# TEMPLATE FILTERS
# =====================================================

# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

# =====================================================
# TEMPLATE FILTERS
# =====================================================

@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object"""
    if value is None:
        return ''
    return value.strftime(format)

@app.template_filter('date')
def format_date(value):
    """Format a date object"""
    if value is None:
        return ''
    return value.strftime('%Y-%m-%d')

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        # db.create_all()  # Commented out since we use SQL schema
        pass
    
    app.run(host='0.0.0.0', port=5000, debug=True)
