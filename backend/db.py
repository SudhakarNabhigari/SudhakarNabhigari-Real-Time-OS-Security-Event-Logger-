from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Define base class for models
Base = declarative_base()


# ---------------- Event Model ----------------
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    host = Column(String(128))
    event_type = Column(String(64))
    details = Column(Text)


# ---------------- Alert Model ----------------
class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(String(16))
    message = Column(Text)
    meta = Column(Text)


# ---------------- Database Setup ----------------
engine = create_engine('sqlite:///events.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Initializes the database and creates all tables."""
    Base.metadata.create_all(engine)
