from ninja import Schema
from typing import Optional

class LoginInput(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

class TokenOutput(Schema):
    access: str
    refresh: str
    user_type: Optional[str] = None
