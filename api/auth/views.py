from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from ..models.users import User, UserRole
from ..utils import db
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

auth_ns = Namespace('auth', description='Authentication and authorization')

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='The user\'s username'),
    'password': fields.String(required=True, description='The user\'s password'),
})

signup_model = auth_ns.model('Signup', {
    'username': fields.String(required=True, description='The user\'s username'),
    'email': fields.String(required=True, description='The user\'s email address'),
    'password': fields.String(required=True, description='The user\'s password'),
    'role': fields.String(required=True, description='The user\'s role')
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json

        # Find user by username
        user = User.query.filter_by(username=data['username']).first()

        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {'message': 'Invalid email or password'}, 401

        # Create access token
        additional_claims = {'role': user.role.value}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.username, additional_claims=additional_claims)
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        return response, 200

@auth_ns.route('/signup')
class SignupResource(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not username or not email or not password or not role:
            return {'message': 'Missing required fields'}, 400

        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 400

        if User.query.filter_by(email=email).first():
            return {'message': 'Email address already registered'}, 400

        if role not in UserRole.__members__:
            return {'message': 'Invalid role'}, 400

        user = User(username=username, email=email, password_hash=generate_password_hash(password), role=UserRole[role])
        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201
    

@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return {'access_token': access_token}, 200