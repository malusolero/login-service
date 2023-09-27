from pydantic import BaseModel

class ErrorSchema(BaseModel):
    """ Generic error representation schema
    """
    message: str