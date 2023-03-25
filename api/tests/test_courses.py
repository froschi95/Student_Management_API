import unittest
from api import create_app
from api.config.config import config_dict
from api.utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.courses import Course
from api.models.grades import Grade, GradeEnum
from api.models.users import User, UserRole
from api.models.students import Student
from flask_jwt_extended import create_access_token, get_jwt
from datetime import date


class CourseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()

        with self.appctx:
            db.create_all()
            self.testuser = User(username='testuser', email='testuser@gmail.com', password_hash=generate_password_hash('testpassword'), role='ADMIN')
            db.session.add(self.testuser)
            db.session.commit()


    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None



    def test_get_all_courses(self):
        # course = Course(name='Test Course', credit_hours=3, course_code='TEST 101', teacher='Test Instructor')
        # db.session.add(course)
        # db.session.commit()

        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = self.client.get('/courses/courses', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_create_course(self):
        data = {'name': 'Test Course', 'credit_hours': 3, 'course_code': 'TEST 101', 'teacher': 'Test Instructor'}
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = self.client.post('/courses/courses',json=data, headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_get_specific_course(self):
        test_course = Course(name='Test Course2', credit_hours=3, course_code='TEST 102', teacher='Test Instructor2')
        db.session.add(test_course)
        db.session.commit()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get(f'/courses/course/{test_course.id}', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_update_specific_course(self):
        test_course = Course(name='Test Course2', credit_hours=3, course_code='TEST 102', teacher='Test Instructor2')
        db.session.add(test_course)
        db.session.commit()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        data = {'credit_hours': 4, 'course_code': 'TEST 103'}
        response = self.client.put(f'/courses/course/{test_course.id}', json=data, headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_get_grades_per_course(self):
        test_course = Course(name='Test Course2', credit_hours=3, course_code='TEST 102', teacher='Test Instructor2')
        db.session.add(test_course)
        db.session.commit()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get(f'/courses/grades/{test_course.id}', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_add_grades_per_course(self):
        test_course = Course(name='Test Course2', credit_hours=3, course_code='TEST 102', teacher='Test Instructor2')
        db.session.add(test_course)
        db.session.commit()

        teststudent = Student(name='Teststudent', enrollment_date=date.fromisoformat('2022-08-15'))
        teststudent.save()
        grade_data = {
            'student_id': teststudent.id,
            'grade': GradeEnum.A.name
        }
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.post(f'/courses/grades/{test_course.id}', json=grade_data, headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_update_grades_per_course(self):
        test_course = Course(name='Test Course2', credit_hours=3, course_code='TEST 102', teacher='Test Instructor2')
        db.session.add(test_course)
        db.session.commit()

        teststudent = Student(name='Teststudent', enrollment_date=date.fromisoformat('2022-08-15'))
        teststudent.save()

        course_grade = Grade(course_id=test_course.id, student_id=teststudent.id)
        db.session.add(course_grade)
        db.session.commit()

        grade_update_data = {
            'student_id': teststudent.id,
            'grade': GradeEnum.B.name
        }
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.put(f'/courses/grades/{test_course.id}', json=grade_update_data, headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_student_grades(self):
        teststudent = Student(name='Teststudent', enrollment_date=date.fromisoformat('2022-08-15'))
        teststudent.save()

        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get(f'/courses/grades/student/{teststudent.id}', headers=headers)
        self.assertEqual(response.status_code, 200)