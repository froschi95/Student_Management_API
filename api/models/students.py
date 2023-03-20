from ..utils import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    enrollment_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='student')
    grades = db.relationship('Grade', backref='student', lazy=True)

    def calculate_gpa(self):
        """
        Calculates a students gpa
        """
        total_grade_points = 0
        total_credits = 0

        for grade in self.grades:
            credit_hours = grade.course.credit_hours
            total_credits += credit_hours
            total_grade_points += grade.gradepoint() * credit_hours

        if total_credits == 0:
            return 0

        return total_grade_points / total_credits
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def bulk_save(cls, students_list):
        """
        Save a list of objects to the database in bulk.
        """
        db.session.bulk_save_objects([cls(**student) for student in students_list])
        db.session.commit()
