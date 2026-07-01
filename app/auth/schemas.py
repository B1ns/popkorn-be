# app/auth/schemas.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSignup(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=72)
    
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    