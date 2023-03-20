from ..utils import db
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    ADMIN = 'admin'
    STUDENT = 'student'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT)
    # date_created = db.Column(db.Datetime(), default=datetime.utcnow)
    student = db.relationship('Student', uselist=False, back_populates='user')


    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()