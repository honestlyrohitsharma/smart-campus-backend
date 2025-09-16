from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime
import os
import csv
from typing import List

# Local imports
import models
import auth
from database import SessionLocal, engine

# --- Path for local CSV log file ---
LOG_DIRECTORY = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "attendeloger")
LOG_FILE = os.path.join(LOG_DIRECTORY, "pc_attendance_log.csv")

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# --- UPDATED CORS GUEST LIST ---
# We have added your live Netlify website URL here.
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://cozy-horse-267718.netlify.app", # <-- YOUR LIVE WEBSITE
    "https://incomparable-dragon-fb676e.netlify.app" # <-- YOUR OTHER LIVE WEBSITE URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Current user dependency
def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    student_id_str = auth.verify_access_token(token, credentials_exception)
    user = db.query(models.Student).filter(models.Student.student_id_str == student_id_str).first()
    if user is None:
        raise credentials_exception
    return user

# --- (The rest of your main.py file remains the same) ---

# Pydantic Models
class StudentPublic(BaseModel):
    student_id_str: str
    name: str
    card_uid: str
    class Config:
        from_attributes = True

class AttendancePublic(BaseModel):
    timestamp: datetime.datetime
    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    student_id_str: str
    name: str
    card_uid: str
    password: str

class UserLogin(BaseModel):
    student_id_str: str
    password: str

# API Endpoints
@app.get("/")
def read_root():
    return {"status": "Smart Campus Backend is running!"}

@app.post("/api/students/register")
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.student_id_str == student.student_id_str).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Student ID already registered")
    
    hashed_password = auth.hash_password(student.password)
    new_student = models.Student(
        student_id_str=student.student_id_str,
        name=student.name,
        card_uid=student.card_uid,
        hashed_password=hashed_password
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": f"Student {student.name} registered successfully."}

@app.post("/api/auth/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id_str == user_credentials.student_id_str).first()
    if not student or not auth.verify_password(user_credentials.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect student ID or password",
        )
    access_token_data = {"sub": student.student_id_str}
    access_token = auth.create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/students/me", response_model=StudentPublic)
def read_students_me(current_user: models.Student = Depends(get_current_active_user)):
    return current_user

@app.post("/api/attendance/rfid-log")
def log_attendance_from_rfid(card_uid: str, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.card_uid == card_uid).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with card UID {card_uid} not found")
    
    timestamp = datetime.datetime.now()
    new_record = models.AttendanceRecord(student_id=student.id, timestamp=timestamp)
    db.add(new_record)
    db.commit()
    
    try:
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, 'a', newline='') as csvfile:
            log_writer = csv.writer(csvfile)
            if not file_exists:
                log_writer.writerow(['Timestamp', 'Student_ID', 'Name', 'Card_UID'])
            log_writer.writerow([timestamp.isoformat(), student.student_id_str, student.name, card_uid])
    except Exception as e:
        print(f"Error writing to local CSV file: {e}")

    return {"message": f"Attendance logged successfully for {student.name}"}

@app.get("/api/attendance/me", response_model=List[AttendancePublic])
def read_own_attendance(current_user: models.Student = Depends(get_current_active_user), db: Session = Depends(get_db)):
    attendance_records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == current_user.id).all()
    return attendance_records

