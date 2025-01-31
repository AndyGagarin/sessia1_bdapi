import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(24), nullable=False)

    def to_dict(self):
        return {
            'password': self.password,
            'name': self.name
        }

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC), nullable=False)
    category = db.Column(db.String, nullable=False)
    has_comments = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date_created': self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            'date_updated': self.date_updated.strftime("%Y-%m-%d %H:%M:%S"),
            'category': self.category,
            'has_comments': self.has_comments
        }

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC))
    date_updated = db.Column(db.DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))
    author_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    author = db.relationship('Employee', backref='comments')
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    position = db.relationship('Position', backref='comments')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'text': self.text,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'author': {
                'name': self.author.fullname,
                'position': self.position.name
            }
        }


class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(90), nullable=False)
    work_phone_number = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20))
    office_number = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String, nullable=False)
    birth_day = db.Column(db.Date)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    assistant_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    department = db.relationship('Department', backref='employee_list', foreign_keys=[department_id])
    position = db.relationship('Position', backref='employee_list')
    manager = db.relationship('Employee', remote_side=[id], foreign_keys=[manager_id], backref='subordinates')
    assistant = db.relationship('Employee', remote_side=[id], foreign_keys=[assistant_id], backref='assistants')
    other = db.Column(db.Text)
    training_events = db.relationship('TrainingEvent', backref='employee')
    absence_events = db.relationship('AbsenceEvent', backref='employee')
    vacation_events = db.relationship('VacationEvent', backref='employee')

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    head_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    head = db.relationship('Employee', backref='managed_departments', foreign_keys=[head_id])
    employees = db.relationship('Employee', backref='department_ref', foreign_keys='Employee.department_id')

class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    employees = db.relationship('Employee', backref='position_ref')

class TrainingEvent(db.Model):
    __tablename__ = 'training_event'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)

class AbsenceEvent(db.Model):
    __tablename__ = 'absence_event'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)

class VacationEvent(db.Model):
    __tablename__ = 'vacation_event'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)