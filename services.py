from sqlalchemy.orm import Session
from models import SQLLog, DOMLog, User, Website
from schemas import SQLQuery
from ml_model import predict_query, predict_dom_mutation
import schemas

def create_user(user: schemas.UserCreate, db: Session):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

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


def process_dom_log(input: schemas.DOMLog, db: Session):
    label, score = predict_dom_mutation(input.log)

    log = DOMLog(
        website_id=input.website_id,
        mutations=input.log,
        prediction=label,
        score=score
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {"prediction": label, "confidence": score}