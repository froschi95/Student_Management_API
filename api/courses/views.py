from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..models.courses import Course
from ..models.users import UserRole
from ..models.enrollments import Enrollment
from ..models.grades import Grade, GradeEnum
from ..utils import db

course_ns = Namespace('courses', description='Course operations')

course_model = course_ns.model('Course', {
    'name': fields.String(required=True, description='Course name'),
    'course_code': fields.String(description='Course code'),
    'teacher': fields.String(description='Name of Instructor or Teacher'),
    'credit_hours': fields.Integer(required=True, description='Credit hours')
})

grade_model = course_ns.model('Grade', {
    'student_id': fields.Integer(required=True, description='The ID of the student'),
    'course_id': fields.Integer(required=True, description='The ID of the course'),
    'grade': fields.String(required=True, description='The grade for the course', enum=[grade.name for grade in GradeEnum])
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
        teacher = course_ns.payload.get('teacher')

        if not name:
            return {'message': 'Course name required'}, 400

        if not credit_hours:
            return {'message': 'Credit hours required'}, 400
        if not teacher:
            return {'message': 'Name of Instructor Required'}, 400
        
        if not course_code:
            course_code = 'None'

        course = Course(name=name, credit_hours=credit_hours, course_code=course_code, teacher=teacher)

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
        teacher = course_ns.payload.get('teacher')

        if not name and not credit_hours:
            return {'message': 'At least one field required to update course'}, 400

        if name:
            course.name = name

        if credit_hours:
            course.credit_hours = credit_hours

        if course_code:
            course.course_code = course_code
        if teacher: 
            course.teacher = teacher

        db.session.commit()

        return {'message': 'Course updated successfully'}, 200

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

        db.session.delete(course)
        db.session.commit()

        return {'message': 'Course deleted successfully'}
    

# Get, add, update, and delete grades

@course_ns.route('/grades/<int:course_id>')
class GradesByCourse(Resource):
    @course_ns.marshal_list_with(grade_model)
    @jwt_required()
    def get(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        grades = Grade.query.filter_by(course_id=course_id).all()
        return grades, 200

    @course_ns.expect(grade_model)
    @jwt_required()
    def post(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        student_id = course_ns.payload.get('student_id')
        grade_val = course_ns.payload.get('grade')

        if not student_id:
            return {'message': 'Student ID required'}, 400

        if not grade_val:
            return {'message': 'Grade value required'}, 400

        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found'}, 404

        grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()

        if grade:
            return {'message': 'Grade already exists for this student and course'}, 400
        
        if not grade_val in GradeEnum.__members__:
            return {'message': 'Invalid Grade Value'}
        
        new_grade = Grade(student_id=student_id, course_id=course_id, grade=grade_val)
        db.session.add(new_grade)
        db.session.commit()

        return {'message': 'Grade created successfully'}, 201

    @course_ns.expect(grade_model)
    @jwt_required()
    def put(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        student_id = course_ns.payload.get('student_id')
        grade_val = course_ns.payload.get('grade')

        if not student_id or not grade_val:
            return {'message': 'Student ID and grade value required'}, 400

        course = Course.query.get(course_id)

        if not course:
            return {'message': 'Course not found'}, 404

        grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()

        if not grade:
            return {'message': 'Grade not found for this student and course'}, 404

        grade.grade = grade_val
        db.session.commit()

        return {'message': 'Grade updated successfully'}, 200

    @jwt_required()
    def delete(self, course_id):
        current_user_role = get_jwt()['role']

        if current_user_role != UserRole.ADMIN.value:
            return {'message': 'Unauthorized access'}, 401

        grade = Grade.query.filter_by(course_id=course_id).delete()

        if not grade:
            return {'message': 'Grade not found'}, 404

        db.session.commit()

        return {'message': 'Grade deleted successfully'}
    


@course_ns.route('/grades/student/<int:student_id>')
class GradesByStudent(Resource):

    @course_ns.marshal_list_with(grade_model)
    @jwt_required()
    def get(self, student_id):
        current_user_role = get_jwt()['role']
        current_user = get_jwt_identity()
        print(current_user)

        if (current_user_role != UserRole.ADMIN.value) or (student_id != current_user):
            return {'message': 'Unauthorized access'}, 401

        grades = Grade.query.filter_by(student_id=student_id).all()
        return grades, 200