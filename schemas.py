from pydantic import BaseModel, EmailStr

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
    defacement_enabled: bool
    sqli_enabled: bool
    dom_enabled: bool

class GetWebsite(BaseModel):
    id: int
    name: str
    url: str
    user_id: int

    class Config:
        from_attributes = True

class SQLQuery(BaseModel):
    website_id: int
    query: str

class SQLPrediction(BaseModel):
    prediction: str
    confidence: float
    
class DOMLog(BaseModel):
    website_id: int
    log: str

class DOMPrediction(BaseModel):
    prediction: str
    confidence: float
    
    