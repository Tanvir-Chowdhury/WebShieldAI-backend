from fastapi import FastAPI, Depends, HTTPException
from db import create_table, get_db
from sqlalchemy.orm import Session
import models, schemas, services
import defacement_loop 
from defacement_control import toggle_defacement

app = FastAPI(title="WebShieldAI API")

create_table()

# defacement_loop.run_deface_loop(app)

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

@app.post("/websites/{website_id}/toggle-defacement/")
def toggle_defacement_route(website_id: int, enable: bool):
    return toggle_defacement(website_id, enable)