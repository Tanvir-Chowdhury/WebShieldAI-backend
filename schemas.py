from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    plan: str = 'free'

class GetUser(BaseModel):
    id: int
    email: str
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
    
    