from sqlalchemy.orm import Session
from models import SQLLog, DomManipulationLog, User, Website
from schemas import SQLQuery
from ml_model import predict_query, predict_dom_mutation
import models,schemas
from passlib.context import CryptContext
from fastapi import Depends, Request

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
def create_user(user: schemas.UserCreate, db: Session):
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_pw,
        plan=user.plan
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_website(website: schemas.WebsiteCreate, db: Session):
    new_website = Website(**website.dict())
    db.add(new_website)
    db.commit()
    db.refresh(new_website)
    return new_website

def process_sql_query(input: SQLQuery, db: Session):
    if input.query is None or input.query.strip() == "":
        return {"prediction": 0, "confidence": 0}
    label, score = predict_query(input.query)

    log = SQLLog(
        website_id=input.website_id,
        query=input.query,
        prediction=label,
        score=score
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {"prediction": label, "confidence": score}


def log_dom_event(
    log: schemas.DomLogCreate,
    request: Request,
    db: Session
):
    client_ip = request.client.host

    new_log = DomManipulationLog(
        website_id=log.website_id,
        ip_address=client_ip
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return {"message": "Logged", "log_id": new_log.id}