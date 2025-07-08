from fastapi import FastAPI, Depends, HTTPException
from db import create_table, get_db
from sqlalchemy.orm import Session
import models, schemas, services

app = FastAPI(title="WebShieldAI API")

create_table()

@app.post("/users/", response_model=schemas.GetUser)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.create_user(user, db)

@app.post("/websites/", response_model=schemas.GetWebsite)
def create_website(website: schemas.WebsiteCreate, db: Session = Depends(get_db)):
    return services.create_website(website, db)


@app.post("/predict-sqli/")
def predict_sql_query(input: schemas.SQLQuery, db: Session = Depends(get_db)):
    return services.process_sql_query(input, db)

@app.post("/predict-dom/")
def predict_dom_log(input: schemas.DOMLog, db: Session = Depends(get_db)):
    return services.process_dom_log(input, db)