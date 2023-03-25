import unittest
from api import create_app
from api.config.config import config_dict
from api.utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.users import User, UserRole
from api.models.students import Student
from flask_jwt_extended import create_access_token, get_jwt
from datetime import date


class UserTestCase(unittest.TestCase):

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


    def test_admin_user_registration(self):
        data = {
            "username": "user1",
            "email": "user1@gmail.com",
            "password": "283@admin",
            "role": "ADMIN"
        }

        response = self.client.post('/auth/signup', json=data)
        user = User.query.filter_by(username='user1').first()
        assert user.username == "user1"
        assert user.role == UserRole.ADMIN
        assert response.status_code == 201


    def test_admin_user_login(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }

        # signup = self.client.post('/auth/signup', json=data)
        response = self.client.post('/auth/login', json=data)
        # assert signup.status_code == 201
        assert response.status_code == 200


    def test_get_users(self):
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get('/users/users', headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_create_new_users(self):
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        new_student = {
                'username': 'student1',
                'email': 'student@uni.com',
                'password': 'password',
                'role': UserRole.STUDENT.name
            }
        response = self.client.post('/users/users', json=new_student, headers=headers)
        self.assertEqual(response.status_code, 201)


    def test_get_specific_user(self):
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get(f'/users/user/{self.testuser.id}', headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_update_specific_user(self):
        data = {
                'username': 'student1',
                'email': 'student@uni.com',
                'password_hash': generate_password_hash('password'),
                'role': UserRole.STUDENT.name
            }
        test_student = User(username=data['username'], email=data['email'], password_hash=data['password_hash'], role=data['role'])
        db.session.add(test_student)
        db.session.commit()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        test_student_update = {
            'username': 'student1',
            'email': 'test_student@uni.com'
        }
        response = self.client.put(f'/users/user/{test_student.id}', json=test_student_update, headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_get_students(self):
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get('/users/students', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_create_new_student(self):
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        new_student = {
                'name': 'student2',
                'enrollment_date': '2023-01-20'
            }
        response = self.client.post('/users/students', json=new_student, headers=headers)
        self.assertEqual(response.status_code, 201)


    def test_get_specific_student(self):
        teststudent = Student(name='Teststudent', enrollment_date=date.fromisoformat('2022-08-15'))
        teststudent.save()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get(f'/users/students/student/{teststudent.id}', headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_update_specific_student(self):
        teststudent = Student(name='Teststudent', enrollment_date=date.fromisoformat('2022-08-15'))
        teststudent.save()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        teststudent_update = {
                        "name": "Barley Bree",
                        "enrollment_date": "2023-03-02",
                        "user": {
                            "username": "Barley01",
                            "email": "Barley.Bree@gmail.com",
                            "role": "UserRole.STUDENT"
                        }
                    }
        response = self.client.put(f'/users/students/student/{teststudent.id}', json=teststudent_update, headers=headers)
        self.assertEqual(response.status_code, 200)
        

    def test_get_specific_student_grades(self):
        teststudent = Student(name='Teststudent', enrollment_date=date.fromisoformat('2022-08-15'))
        teststudent.save()
        access_token = create_access_token(identity=self.testuser.id, additional_claims={'role': self.testuser.role.value})
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get(f'/users/students/student/{teststudent.id}/grades', headers=headers)
        self.assertEqual(response.status_code, 200)