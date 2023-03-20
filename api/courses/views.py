from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from ..models.courses import Course
from ..models.users import UserRole
from ..models.enrollments import Enrollment
from ..utils import db

course_ns = Namespace('courses', description='Course operations')

course_model = course_ns.model('Course', {
    'name': fields.String(required=True, description='Course name'),
    'course_code': fields.String(description='Course code'),
    'credit_hours': fields.Integer(required=True, description='Credit hours')
})

@course_ns.route('/courses')
class CourseList(Resource):
    @course_ns.marshal_list_with(course_model)
    @jwt_required()
    def get(self):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        courses = Course.query.all()
        return courses, 200

    @course_ns.expect(course_model)
    @jwt_required()
    def post(self):
        current_user_role = get_jwt()['role']
        print(current_user_role)

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        name = course_ns.payload.get('name')
        credit_hours = course_ns.payload.get('credit_hours')
        course_code = course_ns.payload.get('course_code')

        if not name:
            return {'message': 'Course name required'}, 400

        if not credit_hours:
            return {'message': 'Credit hours required'}, 400
        
        if not course_code:
            course_code = 'None'

        course = Course(name=name, credit_hours=credit_hours, course_code=course_code)

        db.session.add(course)
        db.session.commit()

        return {'message': 'Course created successfully'}, 201


@course_ns.route('/course/<int:course_id>')
class CourseDetail(Resource):

    @course_ns.marshal_with(course_model)
    @jwt_required()
    def get(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found'}, 404

        return course, 200

    @course_ns.expect(course_model)
    @jwt_required()
    def put(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found'}, 404

        name = course_ns.payload.get('name')
        credit_hours = course_ns.payload.get('credit_hours')
        course_code = course_ns.payload.get('course_code')

        if not name and not credit_hours:
            return {'message': 'At least one field required to update course'}, 400

        if name:
            course.name = name

        if credit_hours:
            course.credit_hours = credit_hours

        if course_code:
            course.course_code = course_code

        db.session.commit()

        return {'message': 'Course updated successfully'}

    @jwt_required()
    def delete(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found'}, 404

        enrollments = Enrollment.query.filter_by(course_id=course_id).all()

        for enrollment in enrollments:
            db.session.delete(enrollment)