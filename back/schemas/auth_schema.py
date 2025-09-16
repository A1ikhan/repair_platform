from ninja import Schema

class LoginInput(Schema):
    username: str
    password: str

class TokenOutput(Schema):
    access: str
    refresh: str
