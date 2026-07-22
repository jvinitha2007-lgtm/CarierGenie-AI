import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from db import Base, SessionLocal, engine, get_db
from models import Application, Opportunity, User
from schemas import ApplicationUpdate, AuthRequest, ProfileResponse, ProfileUpdate
from security import create_token, current_user, hash_password, verify_password

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger('careergenie')

SEED_OPPORTUNITIES = [
    {'title': 'Frontend Engineer Intern', 'company': 'Linear', 'location': 'Remote', 'match': 96, 'tag': 'Internship', 'color': 'violet', 'skills': ['React', 'TypeScript'], 'deadline': 'Jun 28'},
    {'title': 'AI Product Fellow', 'company': 'Anthropic', 'location': 'San Francisco', 'match': 91, 'tag': 'Fellowship', 'color': 'cyan', 'skills': ['Python', 'Product'], 'deadline': 'Jul 04'},
    {'title': 'Global Hack Week', 'company': 'MLH', 'location': 'Online', 'match': 88, 'tag': 'Hackathon', 'color': 'orange', 'skills': ['Open to all students'], 'deadline': 'Jul 12'},
    {'title': 'Women in Tech Scholarship', 'company': 'TechForward', 'location': 'Online', 'match': 86, 'tag': 'Scholarship', 'color': 'green', 'skills': ['Leadership', 'STEM'], 'deadline': 'Aug 01'},
]

def seed_database() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.email == 'alex@example.com')):
            db.add(User(email='alex@example.com', password_hash=hash_password('career123'), name='Alex Morgan'))
        if not db.scalar(select(Opportunity.id)):
            db.add_all(Opportunity(**item) for item in SEED_OPPORTUNITIES)
        db.commit()

@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_database()
    yield

app = FastAPI(title='CareerGenie AI API', version='2.0.0', lifespan=lifespan)
origins = [item.strip() for item in os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176').split(',')]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def profile_payload(user: User) -> dict[str, Any]:
    return {'name': user.name, 'role': user.role, 'skills': user.skills, 'email': user.email, 'role_name': user.role_name}

def opportunity_payload(item: Opportunity) -> dict[str, Any]:
    return {'id': item.id, 'title': item.title, 'company': item.company, 'location': item.location, 'match': item.match, 'tag': item.tag, 'color': item.color, 'skills': item.skills, 'deadline': item.deadline}

@app.get('/api/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'CareerGenie AI', 'database': 'connected', 'time': datetime.utcnow().isoformat()}

@app.post('/api/auth/signup')
def signup(request: AuthRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    if db.scalar(select(User).where(User.email == request.email)):
        raise HTTPException(status_code=409, detail='An account with this email already exists.')
    user = User(email=request.email, password_hash=hash_password(request.password), name=request.email.split('@')[0].title())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'token': create_token(user.id), 'profile': profile_payload(user)}

@app.post('/api/auth/login')
def login(request: AuthRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    user = db.scalar(select(User).where(User.email == request.email))
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid email or password.')
    return {'token': create_token(user.id), 'profile': profile_payload(user)}

@app.get('/api/dashboard')
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    rows = db.scalars(select(Application).where(Application.user_id == user.id)).all()
    counts = {'Saved': 0, 'Applied': 0, 'Interview': 0, 'Offers': 0}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    return {'career_score': 78, 'resume_score': 84, 'profile_completion': 72, 'streak': 12, 'applications': [4, 8, 6, 13, 11, 19], 'pipeline': counts}

@app.get('/api/opportunities')
def opportunities(q: str | None = Query(default=None), category: str | None = Query(default=None), _: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    statement = select(Opportunity)
    if q:
        term = f'%{q}%'
        statement = statement.where(or_(Opportunity.title.ilike(term), Opportunity.company.ilike(term), Opportunity.tag.ilike(term)))
    if category and category != 'All':
        statement = statement.where(Opportunity.tag == category)
    return [opportunity_payload(item) for item in db.scalars(statement).all()]

@app.get('/api/profile', response_model=ProfileResponse)
def get_profile(user: User = Depends(current_user)) -> dict[str, Any]:
    return profile_payload(user)

@app.post('/api/profile', response_model=ProfileResponse)
def save_profile(update: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    user.name, user.role, user.skills = update.name, update.role, update.skills
    db.commit()
    db.refresh(user)
    return profile_payload(user)

@app.get('/api/applications')
def get_applications(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(select(Application).where(Application.user_id == user.id)).all()
    return [{'opportunity': opportunity_payload(row.opportunity), 'opportunity_id': row.opportunity_id, 'status': row.status} for row in rows]

@app.post('/api/applications')
def save_application(update: ApplicationUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    opportunity = db.get(Opportunity, update.opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail='Opportunity not found.')
    row = db.scalar(select(Application).where(Application.user_id == user.id, Application.opportunity_id == update.opportunity_id))
    if not row:
        row = Application(user_id=user.id, opportunity_id=update.opportunity_id)
        db.add(row)
    row.status = update.status
    db.commit()
    return {'opportunity_id': row.opportunity_id, 'status': row.status}
