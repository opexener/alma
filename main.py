from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import uuid
from typing import List, Optional
from config import APP_TITLE, ACCESS_TOKEN_EXPIRE_MINUTES, ATTORNEY_EMAIL
from database import get_db, create_tables, DBLead
from models import Lead, LeadState
from auth import Token, authenticate_user, create_access_token, get_current_user
from email_utils import EmailSender, send_prospect_confirmation, send_attorney_notification

app = FastAPI(title=APP_TITLE)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Authentication endpoint
@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Public endpoint to submit a lead
@app.post("/leads/", response_model=Lead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save resume file
    file_extension = os.path.splitext(resume.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)

    # Make sure the upload directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as buffer:
        content = await resume.read()
        buffer.write(content)

    # Create lead in the database
    db_lead = DBLead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_path=file_path,
        state=LeadState.PENDING,
        created_at=datetime.now()
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    # Send confirmation to prospect
    send_prospect_confirmation(email, first_name, last_name)

    # Send notification to attorney
    send_attorney_notification(ATTORNEY_EMAIL, first_name, last_name, email, file_path)

    return db_lead

# Protected endpoint to get all leads
@app.get("/leads/", response_model=List[Lead])
async def get_leads(
    skip: int = 0, 
    limit: int = 100,
    state: Optional[LeadState] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Add authentication dependency
):
    limit = min(limit, 100)
    query = db.query(DBLead)
    if state:
        query = query.filter(DBLead.state == state)
    leads = query.offset(skip).limit(limit).all()
    return leads

# Protected endpoint to get a specific lead
@app.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Add authentication dependency
):
    lead = db.query(DBLead).filter(DBLead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

# Protected endpoint to update a lead's state
@app.put("/leads/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: int, 
    state: LeadState = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Add authentication dependency
):
    lead = db.query(DBLead).filter(DBLead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.state = state
    lead.updated_at = datetime.now()
    db.commit()
    db.refresh(lead)
    return lead

# Root endpoint
@app.get("/")
async def root():
    return {"message": APP_TITLE}
