from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ===== AWS RDS MySQL Configuration =====
# IMPORTANT: Replace these values with your actual AWS RDS credentials

DB_USER = "admin"                    # Your RDS Master username
DB_PASSWORD = "Susant123456"   # Your RDS Master password
DB_HOST = "database-1.cto8gawq6gq9.us-east-1.rds.amazonaws.com"
DB_PORT = "3306"                     # Default MySQL port
DB_NAME = "test_mysql"            # Your database name (create this first!)

# MySQL Connection String
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Test connections before using
    pool_recycle=3600,           # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10     # 10 second timeout
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    complaint_details = Column(String(500))
    complaint_number = Column(String(100))
    circle = Column(String(100))
    consumer_number = Column(String(100))
    dept = Column(String(100))
    remarks = Column(String(500))

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()