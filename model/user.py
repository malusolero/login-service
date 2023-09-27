
import time
import jwt
import re

from os import environ
from sqlalchemy import Column, String, Integer
from model import Base
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    password_hash = Column(String(64), nullable=False)
    username = Column(String(32), index=True, unique=True)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        print(self.password_hash)
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expires_in = 6000):
        print(jwt.encode(
            { 'id': self.id, 'exp': time.time() + expires_in }, 
            environ.get('SECRET_KEY'), algorithm='HS256'))
        return jwt.encode(
            { 'id': self.id, 'exp': time.time() + expires_in }, 
            environ.get('SECRET_KEY'), algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        print(token)
        try:
            data = jwt.decode(token, environ.get('SECRET_KEY'),
            ['HS256'])
            print('dataaaaaaaa')
            print(data)
        except Exception as e:
            print(e)
            return 
        return data['id']

    @staticmethod
    def validate_password(password: str):
        print(password)
        pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"
        match = re.match(pattern, password)
        return bool(match)