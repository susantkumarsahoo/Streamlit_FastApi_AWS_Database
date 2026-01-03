from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import pandas as pd
from io import BytesIO
from datetime import datetime
from database import get_db, init_db, Complaint

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComplaintData(BaseModel):
    date: str
    complaint_details: str
    complaint_number: str
    circle: str
    consumer_number: str
    dept: str
    remarks: str

@app.on_event("startup")
def startup():
    init_db()
    print("✅ Database initialized successfully!")

@app.get("/")
def read_root():
    return {"message": "Complaint Management API is running"}

@app.post("/add_complaint")
def add_complaint(data: ComplaintData, db: Session = Depends(get_db)):
    complaint = Complaint(
        date=datetime.strptime(data.date, "%Y-%m-%d"),
        complaint_details=data.complaint_details,
        complaint_number=data.complaint_number,
        circle=data.circle,
        consumer_number=data.consumer_number,
        dept=data.dept,
        remarks=data.remarks
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return {"message": "Complaint added successfully", "id": complaint.id}

@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = file.file.read()
    
    if file.filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(contents))
    elif file.filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(BytesIO(contents))
    else:
        return {"error": "Only CSV or Excel files are supported"}
    
    df.columns = df.columns.str.strip().str.upper()
    
    count = 0
    for _, row in df.iterrows():
        complaint = Complaint(
            date=pd.to_datetime(row.get('DATE', datetime.now())),
            complaint_details=str(row.get('COMPLAINT DETAILS', '')),
            complaint_number=str(row.get('COMPLAINT NUMBER', '')),
            circle=str(row.get('CIRCLE', '')),
            consumer_number=str(row.get('CONSUMER NUMBER', '')),
            dept=str(row.get('DEPT', '')),
            remarks=str(row.get('REMARKS', ''))
        )
        db.add(complaint)
        count += 1
    
    db.commit()
    return {"message": f"Successfully uploaded {count} records"}

@app.get("/complaints")
def get_complaints(db: Session = Depends(get_db)):
    complaints = db.query(Complaint).order_by(Complaint.date.desc()).all()
    
    result = []
    for c in complaints:
        result.append({
            "id": c.id,
            "date": c.date.strftime("%Y-%m-%d"),
            "complaint_details": c.complaint_details,
            "complaint_number": c.complaint_number,
            "circle": c.circle,
            "consumer_number": c.consumer_number,
            "dept": c.dept,
            "remarks": c.remarks
        })
    
    return {"complaints": result, "count": len(result)}