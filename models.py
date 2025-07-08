from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    plan = Column(String, default='free')
    websites = relationship("Website", back_populates="owner")

class Website(Base):
    __tablename__ = 'websites'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="websites")
    defacement_enabled = Column(Boolean, default=False)
    sqli_enabled = Column(Boolean, default=False)
    dom_enabled = Column(Boolean, default=False)
    sql_logs = relationship("SQLLog", back_populates="website")
    dom_logs = relationship("DOMLog", back_populates="website")
    defacement_logs = relationship("DefacementLog", back_populates="website")

class SQLLog(Base):
    __tablename__ = 'sql_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey('websites.id'))
    query = Column(Text)
    prediction = Column(String)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    website = relationship("Website", back_populates="sql_logs")
    
class DOMLog(Base):
    __tablename__ = 'dom_logs'

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey('websites.id'))
    mutations = Column(JSON)  
    prediction = Column(String)
    score = Column(Float)   
    timestamp = Column(DateTime, default=datetime.now)

    website = relationship("Website", back_populates="dom_logs")
    
    
# in models.py
class DefacementLog(Base):
    __tablename__ = 'defacement_logs'

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey('websites.id'))
    prediction = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

    website = relationship("Website", back_populates="defacement_logs")
