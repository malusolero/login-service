from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, jsonify
from flask_httpauth import HTTPBasicAuth

from sqlalchemy.exc import IntegrityError

from model import Session, User

from schema import VerifyLoginSchema, CreateUserResponseSchema, CreateUserRequestSchema, ErrorSchema, HeaderSchema

from flask_cors import CORS


info = Info(title="Login Service API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# Docs tags
home_tag = Tag(name="Docs", description="Select docs between: Swagger, Redoc or RapiDoc")
login_tag = Tag(name="Login", description="Create user, login and check if user is authenticated" )

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    session = Session()
    # first try token
    userId = User.verify_auth_token(username_or_token)
    print('USERID')
    print(userId)
    # then check for username and password pair
    if not userId:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
        return user

    user = session.query(User).filter_by(id = userId).first()
    
    if not user:
        return False
    
    return user

@app.get('/', tags=[home_tag])
def home():
    """ Redirects for /openapi, screen for choosing the documentation.
    """
    return redirect('/openapi')

@app.post('/user', tags=[login_tag], responses={"200": CreateUserResponseSchema, "409": ErrorSchema, "400": ErrorSchema})
def register(form: CreateUserRequestSchema):

    """
        Endpoint for creating a user inside database
    """
    username = form.username 
    password = form.password

    try:
        session = Session()

        if not username  or not password:
            
            error_message = "No username or password, try again with credentials!"
            return {"message": error_message}, 400
        # Check for existing users
        if session.query(User).filter_by(username = username).first() is not None:
            error_message = "User name alreeady exists in database, try logging in first!"
            return {"message": error_message}, 409

        if not User.validate_password(password):
            error_message = "Weak password. The password must be at least 8 digits long, contain at least one uppercase letter, lowercase letter and one digit."
            return { "message": error_message},"400"
        user = User(username = username)
        user.hash_password(password)
        session.add(user)
        session.commit()
        return {'username': user.username}, 201

    except IntegrityError as e:
        error_msg = "Type with received name already exists :/"
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Error happened when trying to create a new user inside database :/"
        return {"mesage": error_msg}, 400
        
@app.post('/user/login', tags=[login_tag], responses={"200": VerifyLoginSchema, "404": ErrorSchema, "401": ErrorSchema})
def checkCredentials(form: CreateUserRequestSchema):
    """
        Endpoint for getting a token when receiving valid credentials
    """
    username = form.username 
    password = form.password

    try:
        session = Session()

        if not username  or not password:
            error_message = "No username or password, try again with credentials!"
            return {"message": error_message}, 400

        user: User = session.query(User).filter_by(username = username).first()

        if user is None:
            error_message = "User not found!"
            return {"message": error_message}, 404
        
        valid = user.verify_password(password)
        if valid:
            token = user.generate_auth_token()
            return jsonify({ 'token': token, 'duration': 6000 })
        else:
            error_message = 'Wrong credentials'
            return { "message": error_message}, 401

    except Exception as e:
        return {"message": "Error ocurred"}, 400

@app.get('/user/is-authenticated', tags=[login_tag], responses={"200": CreateUserResponseSchema, "401": {}})
def checkAuthenticated(header: HeaderSchema):
    """
        Endpoint for checking authentication state when receiving a token via request headers Authorization
    """
    try:

        token = header.authorization.split()[1]
    except:
        return {}, 401

    user = verify_password(token, None)

    if user:
        return { "username": user.username}, 200
    else:
        return {}, 401

@app.put('/user', tags=[login_tag], responses={"200": CreateUserResponseSchema, "401": ErrorSchema, "404": ErrorSchema, "400": ErrorSchema})
def updateUser(header: HeaderSchema, body: CreateUserRequestSchema):
    """
        Endpoint for updating username and/or password
    """

    print(body.password)
    try:

        token = header.authorization.split()[1]
    except:
        return {}, 401

    user = verify_password(token, None)

    if not user:
        return {}, 401

    if not User.validate_password(body.password):
        error_message = "Weak password. The password must be at least 8 digits long, contain at least one uppercase letter, lowercase letter and one digit."
        return { "message": error_message},"400"

    session = Session()
    updated = session.query(User).filter(User.id == user.id).update({ "username": body.username, "password": body.password})
    session.commit()

    if updated:
        return {"username": body.username}, 200
    else:
        error_msg = 'User not found in database'
        return {"message": error_msg}, 404

@app.delete('/user', tags=[login_tag], responses={"200": {}, "401": ErrorSchema, "404": ErrorSchema, "400": ErrorSchema})
def deleteUser(header: HeaderSchema):
    """
        Endpoint for removing an user from the database
    """
    try:

        token = header.authorization.split()[1]
    except:
        return {}, 401

    user = verify_password(token, None)

    if not user:
        return {}, 401

    session = Session()
    updated = session.query(User).filter(User.id == user.id).delete() 
    session.commit()

    if updated:
        return {}, 200
    else:
        error_msg = 'User not found in database'
        return {"message": error_msg}, 404

    




