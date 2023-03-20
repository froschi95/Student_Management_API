from ..utils import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    credit_hours = db.Column(db.Integer, nullable=False)
    course_code = db.Column(db.String(10))
    grades = db.relationship('Grade', backref='course', lazy=True)