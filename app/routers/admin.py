from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies.authorization import permission_required
from app.models.user import User
from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.models.enums import SubmissionStatus


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(permission_required("admin:all"))],
)

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    total_templates = db.query(func.count(ContractTemplate.id)).scalar()
    total_submissions = db.query(func.count(FilledContract.id)).scalar()
    confirmed_submissions = db.query(func.count(FilledContract.id)).filter(
        FilledContract.status == SubmissionStatus.CONFIRMED.value
    ).scalar()

    return {
        "total_users": total_users,
        "total_templates": total_templates,
        "total_submissions": total_submissions,
        "confirmed_submissions": confirmed_submissions,    
    }

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "is_verified": u.is_verified,
            "roles":[r.name for r in u.roles],
         }
         for u in users
    ]

@router.get("/templates")
def get_templates(db: Session = Depends(get_db)):
    templates = db.query(ContractTemplate).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "status": t.status,
            "owner_email": t.owner.email if t.owner else None,
            "owner_id": t.owner_id,
        }
        for t in templates
    ]
