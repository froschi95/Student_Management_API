from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime
from ..utils import db
from ..models.users import UserRole
from ..models.enrollments import Enrollment
from ..models.students import Student
from ..models.courses import Course
from ..models.grades import Grade, GradeEnum


enrollment_ns = Namespace('enrollments', description='Student Course Management System')

enrollment_model = enrollment_ns.model('Enrollment', {
    'student_id': fields.Integer(required=True, description='The ID of the student'),
    'course_id': fields.Integer(required=True, description='The ID of the course')
})

grade_model = enrollment_ns.model('Grade', {
    'student_id': fields.Integer(required=True, description='The ID of the student'),
    'course_id': fields.Integer(required=True, description='The ID of the course'),
    'grade': fields.String(required=True, description='The grade for the course', enum=[grade.name for grade in GradeEnum])
})

@enrollment_ns.route('/enroll')
class EnrollmentList(Resource):

    @jwt_required()
    @enrollment_ns.marshal_list_with(enrollment_model)
    def get(self):
        """
        Get All enrolled Students
        """
        current_user_role = get_jwt()['role']
        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        enrollments = Enrollment.query.all()
        return enrollments

    @jwt_required()
    @enrollment_ns.expect(enrollment_model)
    def post(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        data = enrollment_ns.payload

        course_id = data['course_id']
        student_id = data['student_id']

        course = Course.query.get(course_id)
        student = Student.query.get(student_id)

        if not course:
            return {'message': 'Course not found'}, 404

        if not student:
            return {'message': 'Student not found'}, 404

        enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first()

        if enrollment:
            return {'message': 'Enrollment already exists'}, 400

        enrollment = Enrollment(course_id=course_id, student_id=student_id)
        db.session.add(enrollment)
        db.session.commit()

        return {'message': 'Enrollment created successfully', 'id': enrollment.id}, 201


@enrollment_ns.route('/enrollment/<int:enrollment_id>')
class EnrollmentDetail(Resource):
    @jwt_required()
    @enrollment_ns.marshal_with(enrollment_model)
    def get(self, enrollment_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        enrollment = Enrollment.query.get(enrollment_id)

        if not enrollment:
            return {'message': 'Enrollment not found'}, 404

        return enrollment

    @enrollment_ns.expect(grade_model)
    @jwt_required()
    def put(self, enrollment_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        enrollment = Enrollment.query.get(enrollment_id)

        if not enrollment:
            return {'message': 'Enrollment not found'}, 404

        course_id = enrollment_ns.payload.get('course_id')

        if course_id:
            grade = Grade.query.get(course_id)

            if not grade:
                return {'message': 'Invalid grade ID or course ID'}, 400

            enrollment.grade = grade

        db.session.commit()

        return {'message': 'Enrollment updated successfully'}

    @jwt_required()
    def delete(self, enrollment_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        enrollment = Enrollment.query.get(enrollment_id)

        if not enrollment:
            return {'message': 'Enrollment not found'}, 404

        db.session.delete(enrollment)
        db.session.commit()

        return {'message': 'Enrollment deleted successfully'}


@enrollment_ns.route('/students/<int:student_id>/enroll')
class CourseRegistration(Resource):
    @enrollment_ns.expect(enrollment_model)
    @jwt_required()
    def post(self, student_id):
        current_user_id = get_jwt_identity()
        student = Student.query.get(student_id)

        if not student:
            return {'message': 'Student not found'}, 404

        if current_user_id != student.user_id:
            return {'message': 'Unauthorized access'}, 401

        data = enrollment_ns.payload

        course_id = data.get('course_id')

        if not course_id:
            return {'message': 'Course ID required'}, 400

        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found'}, 404

        enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first()

        if enrollment:
            return {'message': 'Student already registered for course'}, 400

        enrollment = Enrollment(course_id=course_id, student_id=student_id)

        db.session.add(enrollment)
        db.session.commit()

        return {'message': 'Course registration successful'}