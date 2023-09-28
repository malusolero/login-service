from pydantic import BaseModel, Field

class CreateUserResponseSchema(BaseModel):
    """
        Defines the successful response of user creation inside database
    """

    username: str = "Test user"

class CreateUserRequestSchema(BaseModel):
    """
        Defines the parameters for creating a user inside database
    """

    username: str = "Test user"
    password: str = "mytestpasswrod"


class VerifyLoginSchema(BaseModel):
    """
        Defines parameters for checking if user is with right credentials
    """

    token: dict = { "token": "JWT token", "duration": 600}

class HeaderSchema(BaseModel):
    """
        Header Schema used for receiving token inside Authorization Header
    """
    authorization: str = Field( alias="Authorization")