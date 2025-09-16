from ninja import Schema
from typing import Optional

class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

class UserCreate(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str  # 'customer' или 'worker'
