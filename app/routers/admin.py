from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies.authorization import permission_required
from datetime import datetime, timedelta

from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract
from app.models.enums import SubmissionStatus
from sqlalchemy.orm import joinedload
from sqlalchemy import cast, Date


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
            "is_suspended": u.is_suspended,
            "roles": [r.name for r in u.roles],
            "last_login": u.last_login,
            "created_at": u.created_at,
            "template_count": len(u.contract_templates),
        }
        for u in users
    ]


@router.patch("/users/{user_id}/suspend")
def toggle_suspend_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User not found")
    user.is_suspended = not user.is_suspended
    db.commit()
    return {"id": user.id, "is_suspended": user.is_suspended}


@router.patch("/users/{user_id}/verify")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User not found")
    user.is_verified = True
    user.verification_token = None
    user.is_suspended = False
    db.commit()
    return {"id": user.id, "is_verified": True, "is_suspended": False}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User not found")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

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

@router.get("/submissions")
def get_submissions(db: Session = Depends(get_db)):
    submissions = (
        db.query(FilledContract)
        .options(joinedload(FilledContract.template).joinedload(ContractTemplate.owner))
        .all()
    )
    return [
        {
            "id": s.id,
            "status": s.status,
            "submitter_email": s.submitter_email,
            "submitted_at": s.submitted_at,
            "confirmed_at": s.confirmed_at,
            "template_id": s.template_id,
            "template_name": s.template.name if s.template else None,
            "owner_email": s.template.owner.email if s.template and s.template.owner else None,
        }
        for s in submissions
    ]


@router.get("/analytics/submissions")
def analytics_submissions(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.query(cast(FilledContract.submitted_at, Date), func.count(FilledContract.id))
        .filter(FilledContract.submitted_at >= since)
        .group_by(cast(FilledContract.submitted_at, Date))
        .order_by(cast(FilledContract.submitted_at, Date))
        .all()
    )
    return [{"date": str(row[0]), "count": row[1]} for row in rows]


@router.get("/analytics/user-growth")
def analytics_user_growth(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.query(cast(UserProfile.created_at, Date), func.count(UserProfile.id))
        .filter(UserProfile.created_at >= since)
        .group_by(cast(UserProfile.created_at, Date))
        .order_by(cast(UserProfile.created_at, Date))
        .all()
    )
    return [{"date": str(row[0]), "count": row[1]} for row in rows]


@router.get("/analytics/active-users")
def analytics_active_users(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.query(cast(User.last_login, Date), func.count(User.id))
        .filter(User.last_login >= since)
        .group_by(cast(User.last_login, Date))
        .order_by(cast(User.last_login, Date))
        .all()
    )
    return [{"date": str(row[0]), "count": row[1]} for row in rows]
