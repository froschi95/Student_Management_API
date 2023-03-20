from ..utils import db
from enum import Enum

class GradeEnum(Enum):
    A = 4.0
    B = 3.0
    C = 2.0
    D = 1.0
    F = 0.0

class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Enum(GradeEnum), default=GradeEnum.F)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def gradepoint(self):
        return self.grade.value