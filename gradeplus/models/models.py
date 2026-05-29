from database.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default='user')
    language      = db.Column(db.String(10),  default='en')
    dark_mode     = db.Column(db.Boolean,     default=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    subjects      = db.relationship('Subject',  backref='user', lazy=True, cascade='all, delete-orphan')
    semesters     = db.relationship('Semester', backref='user', lazy=True, cascade='all, delete-orphan')
    timetables    = db.relationship('Timetable', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'language': self.language,
            'dark_mode': self.dark_mode
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    marks       = db.Column(db.Float,   default=0)
    total_marks = db.Column(db.Float,   default=100)
    credit_hrs  = db.Column(db.Integer, default=3)
    system      = db.Column(db.String(20), default='pakistan')

    def percentage(self):
        if self.total_marks == 0:
            return 0
        return round((self.marks / self.total_marks) * 100, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'marks': self.marks,
            'total_marks': self.total_marks,
            'credit_hrs': self.credit_hrs,
            'percentage': self.percentage(),
            'system': self.system
        }

class Semester(db.Model):
    __tablename__ = 'semesters'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name       = db.Column(db.String(50), nullable=False)
    gpa        = db.Column(db.Float,  default=0.0)
    cgpa       = db.Column(db.Float,  default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gpa': self.gpa,
            'cgpa': self.cgpa,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

class Timetable(db.Model):
    __tablename__ = 'timetables'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day          = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    hours        = db.Column(db.Float, default=1.0)
    priority     = db.Column(db.String(10), default='medium')

    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day,
            'subject_name': self.subject_name,
            'hours': self.hours,
            'priority': self.priority
        }
