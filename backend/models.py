import json

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Patient(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(255))
    insurances = db.relationship('Insurance', back_populates='patient', lazy='dynamic')
    providers = db.relationship('Provider', secondary='patient_provider', back_populates='patients')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Patient username %r>' % self.username


class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    specialty = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(255))
    preferred_contact = db.Column(db.String(20))
    patients = db.relationship('Patient', secondary='patient_provider', back_populates='providers')

    def __repr__(self):
        dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return json.dumps(dict)


class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    policy_number = db.Column(db.String(255))
    coverage_start_date = db.Column(db.Date)
    coverage_end_date = db.Column(db.Date)
    deductible = db.Column(db.Float)
    copay = db.Column(db.Float)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship('Patient', back_populates='insurances')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return json.dumps(dict)


# Association table for the many-to-many relationship between Patient and Provider
patient_provider = db.Table('patient_provider',
                            db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'), primary_key=True),
                            db.Column('provider_id', db.Integer, db.ForeignKey('provider.id'), primary_key=True)
                            )
