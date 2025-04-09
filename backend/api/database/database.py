from sqlalchemy import create_engine, Column, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database file
DB_FILE = "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///database/{DB_FILE}"

# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize the database and create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
