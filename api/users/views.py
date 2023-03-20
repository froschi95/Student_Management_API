from flask_restx import Resource, Namespace, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from ..utils import db
from ..models.users import User, UserRole
from ..models.enrollments import Enrollment
from ..models.grades import Grade
from ..models.students import Student
from werkzeug.security import generate_password_hash
from flask import request
import csv
from datetime import date
from io import TextIOWrapper
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
from ..config.config import DevConfig


users_ns = Namespace('users', description='Admin and Student related Operations')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)

# Define schemas for resources
user_model = users_ns.model('User', {
    'username': fields.String(required=True, description='The username'),
    'email': fields.String(required=True, description='The email address'),
    'password': fields.String(required=True, description='The password'),
    'role': fields.String(required=True, enum=[role.name for role in UserRole], description='The user role')
})
student_model = users_ns.model('Student', {
    'id': fields.Integer,
    'name': fields.String(),
    'enrollment_date': fields.Date,
    'user': fields.Nested(user_model),
    'gpa': fields.Float
})

grade_model = users_ns.model('Grade', {
    'student_id': fields.Integer(required=True, description='The ID of the student'),
    'course_id': fields.Integer(required=True, description='The ID of the course'),
    'grade': fields.String(required=True, description='The grade for the course', enum=['A', 'B', 'C', 'D', 'F'])
})

# Define resource routes
@users_ns.route('/users')
class UserList(Resource):

    @users_ns.marshal_list_with(user_model)
    @jwt_required()
    def get(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        users = User.query.all()

        return users, 200

    @users_ns.expect(user_model)
    @jwt_required()
    def post(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        username = users_ns.payload.get('username')
        email = users_ns.payload.get('email')
        password = users_ns.payload.get('password')
        role = users_ns.payload.get('role')

        if not username:
            return {'message': 'Username is required'}, 400

        if not email:
            return {'message': 'Email is required'}, 400

        if not password:
            return {'message': 'Password is required'}, 400

        if not role:
            return {'message': 'Role is required'}, 400

        if not role in UserRole.__members__:
            return {'message': 'Invalid user role'}, 400

        user = User(username=username, email=email, role=UserRole[role], password_hash=generate_password_hash(password))
        # user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully', 'id': user.id}, 201

@users_ns.route('/user/<int:user_id>')
class UserDetail(Resource):

    @users_ns.marshal_with(user_model)
    @jwt_required()
    def get(self, user_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        return user
    

    @users_ns.expect(user_model)
    @jwt_required()
    def put(self, user_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        username = users_ns.payload.get('username')
        email = users_ns.payload.get('email')
        password = users_ns.payload.get('password')
        role = users_ns.payload.get('role').get('role')

        if username:
            user.username = username

        if email:
            user.email = email

        if password:
            user.password_hash = generate_password_hash(password)

        if role:
            if not UserRole.has_value(role):
                return {'message': 'Invalid user role'}, 400

            user.role = UserRole[role]

        db.session.commit()

        return {'message': 'User updated successfully'}

    @jwt_required()
    def delete(self, user_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted successfully'}


@users_ns.route('/students')
class StudentList(Resource):

    @jwt_required()
    @users_ns.marshal_list_with(student_model)
    def get(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        students = Student.query.all()

        return students, 200


    @jwt_required()
    @users_ns.expect(student_model)
    def post(self):
        current_user_role = get_jwt()['role']
        # print(current_user_role)

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        student_data = users_ns.payload
        # student_user_data = student_data.pop('user', None)
        # data = users_ns.payload

        # print(student_data)
        student = Student(name=student_data['name'], enrollment_date=date.fromisoformat(student_data['enrollment_date']))
        if 'user' in student_data:
            password = student_data['user'].pop('password')
            new_user = User(**student_data['user'], password_hash=generate_password_hash(password))
            student.user = new_user

        student.save()

        return {"message": "Student created Successfully"}, 201
    

    @jwt_required()
    # @users_ns.expect(upload_parser)
    def put(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401
        
        # args = upload_parser.parse_args()
        # upload_file = args['file']
        upload_file = request.files.get('file')

        if not upload_file:
            return {'message': 'No file provided'}, 400

        # file = request.files['file']
        # file = users_ns.payload.files['file']
        
        if upload_file.content_type != 'text/csv':
            return {'message': 'Invalid file type, only CSV files are allowed'}, 400


        students = []

        filename = secure_filename(upload_file.filename)
        file_path = os.path.join(DevConfig.UPLOAD_FOLDER, filename)
        upload_file.save(file_path)
        
        try:
            with open(upload_file, mode='r', encoding='utf-8') as f:
                stream = TextIOWrapper(f, encoding='utf-8')
                csv_reader = csv.DictReader(stream)
                
                for row in csv_reader:
                    name = row.get('name')
                    enrollment_date = row.get('enrollment_date')

                    # Create a new user object with the provided credentials
                    username = row.get('username')
                    email = row.get('email')
                    password = row.get('password')
                    role = UserRole.STUDENT
                    user = User(username=username, email=email, password_hash=generate_password_hash(password), role=role)

                    # Create a new student object with the provided data and the user object
                    student = Student(name=name, enrollment_date=date.fromisoformat(enrollment_date), user=user)
                    
                    students.append(student)
                
            Student.bulk_save(students)
            
            return {'message': 'Students created successfully'}, 201
        
        except Exception as e:
            return {'message': 'Error creating students: {}'.format(str(e))}, 400

    @jwt_required()
    def delete(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        Student.query.delete()

        return {'message': 'All students deleted successfully'}, 200


@users_ns.route('/students/student/<int:student_id>')
class StudentDetail(Resource):

    @jwt_required()
    @users_ns.marshal_with(student_model)
    def get(self, student_id):
        current_user_role = get_jwt()['role']
        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found'}, 404


        return student

    @users_ns.expect(student_model)
    @jwt_required()
    def put(self, student_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found'}, 404

        data = users_ns.payload

        # Update student's name and enrollment date
        if 'name' in data:
            student.name = data['name']

        if 'enrollment_date' in data:
            student.enrollment_date = date.fromisoformat(data['enrollment_date'])

         # Update student's user information
        if 'user' in data:
            if not student.user:
                user = User(**data['user'])
                student.user = user
                
            else:
                user = student.user
                if 'username' in data['user']:
                    user.username = data['user']['username']
                if 'email' in data['user']:
                    user.email = data['user']['email']
                if 'password' in data['user']:
                    user.password_hash = generate_password_hash(data['user']['password'])

        db.session.commit()

        return {'message': 'Student updated successfully'}

    @jwt_required()
    def delete(self, student_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401
        
        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found'}, 404

        db.session.delete(student)
        db.session.commit()

        return {'message': 'Student deleted successfully'}, 200

    

@users_ns.route('/students/student/<int:student_id>/grades')
class StudentGrades(Resource):
    @jwt_required()
    @users_ns.marshal_list_with(grade_model)
    def get(self, student_id):
        current_user_id = get_jwt()['sub']
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value and current_user_id != student_id:
            return {'message': 'Unauthorized access'}, 401

        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found'}, 404
        
        # # Check if student is enrolled in the course
        # enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        # if not enrollment:
        #     return {'message': 'Student is not enrolled in the course'}, 404

        grades = Grade.query.filter_by(student_id=student_id).all()

        return grades
    


# @users_ns.route('/students/int:id/grades')
# class StudentGrades(Resource):

#     @jwt_required()
#     def get(self, id):
#         current_user_role = get_jwt()['role']
#         current_user_id = get_jwt()['id']
#         student = Student.query.get_or_404(id)

#         if current_user_role == UserRole.STUDENT and student.user_id != current_user_id:
#             return {'message': 'Unauthorized'}, 403

#         grades = []
#         for grade in student.grades:
#             grades.append({
#                 'id': grade.id,
#                 'grade': grade.grade.name,
#                 'course': grade.course.name
#             })

#         return {
#             'id': student.id,
#             'name': student.name,
#             'enrollment_date': student.enrollment_date.isoformat(),
#             'gpa': student.calculate_gpa(),
#             'grades': grades
#         }