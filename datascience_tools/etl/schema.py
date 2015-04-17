from . import db 
from sqlalchemy.types import Enum


class Student(db.Model):
    """ A Unique Student Record for the 
    DSaPP Data Warehouse. Links to each feature
    by using the feature metaclass. 
    """
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    ethnicity = db.Column(Enum('')) # implement some standard here
    yearEnteringNinthGrade = db.Column(db.Integer)


    ## Features
    GPAs = db.relationship(backref = 'GPA', lazy='dynamic')
    Retained = db.relationship(backref = 'Retained', lazy='dynamic')
    SATs = db.relationship(backref ='sat', lazy = 'dynamic')
    PSATs = db.relationship(backref = 'psat', lazy = 'dynamic')
    ACTs = db.relationship(backref = 'act', lazy = 'dynamic')
    courses = db.relationship(backref = 'courses', lazy = 'dynamic')
    AbsenceRates = db.relationship(backref = 'AbsenceRate', lazy='dynamic')
    Suspensions = db.relationship(backref = 'Suspensions', lazy='dynamic')
    Outcomes= db.relationship(backref = 'outcome', lazy='dynamic')
    PostSecEnrollment = db.relationship(backref = 'PostSecEnrollment', lazy='dynamic')
    PostSecOutcome = db.relationship(backref = 'PostSecOutcome', lazy='dynamic')
    FreeLunch = db.relationship(backref = 'FreeLunch', lazy='dynamic')

# A join table for the Many-To Many Relations
# See: https://pythonhosted.org/Flask-SQLAlchemy/models.html#many-to-many-relationships
# for more. 
students = db.Table('students',
        db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
        db.Column('school_id', db.Integer, db.ForeignKey('school.id'))
        )

class District(db.Model):
    """ A district is the data provider 
    in the schema, ie Cabarrus or CPS. 
    Each District has students. 
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    districtType = db.Column(Enum('Public','Charter','Private','International', 
        'Other', name='districtType'))
    schools = db.relationship(backref='school', lazy='dynamic')

class School(db.Model):
    """
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    schoolType = db.Column(Enum('Elementary','Middle','High','Mixed','Other', 
        name='schoolType'))
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    students = db.relationship('Student', secondary=students,
            backref=db.backref('students', lazy='dynamic'))

class Feature(db.Model):
    """A metaclass the represents the base 
    linking information in a feature tha we use 
    to make modeling descisions. 
    DO NOT ACCESS THIS CLASS DIRECTLY."""
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id') 

class GPA(Feature):
    gpa = db.Column(db.Float)

class Retained(Feature):

class SAT(Feature):

class PSAT(Feature):

class ACT(Feature):

class Course(Feature):

class AbsenceRate(Feature):

class Suspensions(Feature):

class Outcome(Feature):

class PostSecEnrollment(Feature):

class PostSecOutcome(Feature):
   
class FreeLunch(Feature):
