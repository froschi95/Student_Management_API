from flask import Flask
from flask_restx import Api
from .utils import db
from .config.config import config_dict
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed
from .models.courses import Course
from .models.enrollments import Enrollment
from .models.grades import Grade
from .models.students import Student
from .models.users import User, UserRole
from .courses.views import course_ns
from .auth.views import auth_ns
from .users.views import users_ns
from .enrollment.views import enrollment_ns


def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    api = Api(app, description='A Student Management API')

    api.add_namespace(users_ns)
    api.add_namespace(course_ns, path='/courses')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(enrollment_ns, path='/enrollment')


    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Student': Student,
            'Course': Course,
            'Grade': Grade,
            'Enrollment': Enrollment,
            'UserRole': UserRole
        }

    return app