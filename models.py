from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User Model for Authentication"""
    __tablename__ = 'User'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def get_id(self):
        """Override UserMixin method to use user_id instead of id"""
        return str(self.user_id)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SensorType(db.Model):
    """Sensor Type Model"""
    __tablename__ = 'SensorType'
    
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sensors = db.relationship('Sensor', backref='sensor_type', lazy=True)
    
    def __repr__(self):
        return f'<SensorType {self.name}>'
    
    def to_dict(self):
        return {
            'type_id': self.type_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Location(db.Model):
    """Location Model"""
    __tablename__ = 'Location'
    
    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    area_name = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    elevation = db.Column(db.Numeric(6, 2), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sensors = db.relationship('Sensor', backref='location', lazy=True)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('latitude', 'longitude', name='unique_coordinates'),)
    
    def __repr__(self):
        return f'<Location {self.area_name}>'
    
    def to_dict(self):
        return {
            'location_id': self.location_id,
            'area_name': self.area_name,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'elevation': float(self.elevation) if self.elevation else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Sensor(db.Model):
    """Sensor Model"""
    __tablename__ = 'Sensor'
    
    sensor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model = db.Column(db.String(50), nullable=False)
    install_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE'), default='ACTIVE')
    type_id = db.Column(db.Integer, db.ForeignKey('SensorType.type_id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('Location.location_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    readings = db.relationship('Reading', backref='sensor', lazy=True, cascade='all, delete-orphan')
    maintenance_events = db.relationship('MaintenanceEvent', backref='sensor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Sensor {self.model}>'
    
    def to_dict(self):
        return {
            'sensor_id': self.sensor_id,
            'model': self.model,
            'install_date': self.install_date.isoformat() if self.install_date else None,
            'status': self.status,
            'type_id': self.type_id,
            'location_id': self.location_id,
            'sensor_type': self.sensor_type.name if self.sensor_type else None,
            'location_name': self.location.area_name if self.location else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Reading(db.Model):
    """Reading Model"""
    __tablename__ = 'Reading'
    
    reading_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('Sensor.sensor_id'), nullable=False)
    reading_value = db.Column(db.Numeric(10, 4), nullable=False)
    reading_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reading {self.reading_id}>'
    
    def to_dict(self):
        return {
            'reading_id': self.reading_id,
            'sensor_id': self.sensor_id,
            'reading_value': float(self.reading_value),
            'reading_timestamp': self.reading_timestamp.isoformat() if self.reading_timestamp else None,
            'sensor_model': self.sensor.model if self.sensor else None
        }

class Technician(db.Model):
    """Technician Model"""
    __tablename__ = 'Technician'
    
    tech_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.String(15))
    specialization = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    maintenance_events = db.relationship('MaintenanceEvent', backref='technician', lazy=True)
    
    def __repr__(self):
        return f'<Technician {self.name}>'
    
    def to_dict(self):
        return {
            'tech_id': self.tech_id,
            'name': self.name,
            'contact_no': self.contact_no,
            'specialization': self.specialization,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MaintenanceEvent(db.Model):
    """Maintenance Event Model"""
    __tablename__ = 'MaintenanceEvent'
    
    maintenance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('Sensor.sensor_id'), nullable=False)
    tech_id = db.Column(db.Integer, db.ForeignKey('Technician.tech_id'), nullable=False)
    event_type = db.Column(db.Enum('CALIBRATION', 'REPAIR', 'REPLACEMENT'), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaintenanceEvent {self.maintenance_id}>'
    
    def to_dict(self):
        return {
            'maintenance_id': self.maintenance_id,
            'sensor_id': self.sensor_id,
            'tech_id': self.tech_id,
            'event_type': self.event_type,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'notes': self.notes,
            'sensor_model': self.sensor.model if self.sensor else None,
            'technician_name': self.technician.name if self.technician else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SensorStatusLog(db.Model):
    """Sensor Status Log Model (for trigger logging)"""
    __tablename__ = 'SensorStatusLog'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('Sensor.sensor_id'), nullable=False)
    old_status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE'))
    new_status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE'))
    change_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SensorStatusLog {self.log_id}>'
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'sensor_id': self.sensor_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'change_timestamp': self.change_timestamp.isoformat() if self.change_timestamp else None
        }
