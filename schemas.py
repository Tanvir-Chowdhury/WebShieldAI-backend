from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    plan: str = 'free'

class GetUser(BaseModel):
    id: int
    email: EmailStr
    name: str
    plan: str
    class Config:
        from_attributes = True

class WebsiteCreate(BaseModel):
    name: str
    url: str
    user_id: int
    defacement_enabled: bool = False
    sqli_enabled: bool = False
    dom_enabled: bool = False
    xss_enabled: bool = False

class GetWebsite(BaseModel):
    id: int
    name: str
    url: str
    user_id: int
    defacement_enabled: bool
    sqli_enabled: bool
    dom_enabled: bool
    xss_enabled: bool

    class Config:
        from_attributes = True

class SQLQuery(BaseModel):
    website_id: int
    query: str

class SQLPrediction(BaseModel):
    prediction: str
    confidence: float
    

class DomLogCreate(BaseModel):
    website_id: int
    
class XSSLogCreate(BaseModel):
    website_id: int
    
class DefacementLogCreate(BaseModel):
    website_id: int
    
class ProtectionUpdate(BaseModel):
    protection_type: str
    enabled: bool
    
class AttackLogOut(BaseModel):
    id: int
    type: str                 # "xss" | "defacement" | "dom" | "sql"
    website_id: Union[int, str]
    occurred_at: datetime     # normalized timestamp
    ip_address: Optional[str] = None
    query: Optional[str] = None
    prediction: Optional[str] = None
    score: Optional[float] = None