from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileAvatarOut, ProfileLogoIn, ProfileLogoPositionIn, ProfileOut, ProfileSignatureIn, ProfileUpdate
from app.services.profile_service import ProfileService


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.get_profile(current_user)


@router.put("", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.update_profile(payload, current_user)


@router.delete("", status_code=204)
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    service.delete_profile_account(current_user)
    return Response(status_code=204)


@router.post("/avatar", response_model=ProfileAvatarOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()
    service = ProfileService(db)
    return service.upload_avatar(
        file_bytes=file_bytes,
        content_type=file.content_type,
        current_user=current_user,
    )


@router.delete("/avatar", response_model=ProfileAvatarOut)
def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.delete_avatar(current_user)


@router.post("/signature", response_model=ProfileOut)
def save_signature(
    payload: ProfileSignatureIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.save_signature(payload, current_user)


@router.delete("/signature", response_model=ProfileOut)
def delete_signature(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.delete_signature(current_user)


@router.post("/logo", response_model=ProfileOut)
def save_logo(
    payload: ProfileLogoIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.save_logo(payload, current_user)


@router.delete("/logo", response_model=ProfileOut)
def delete_logo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.delete_logo(current_user)


@router.patch("/logo-position", response_model=ProfileOut)
def update_logo_position(
    payload: ProfileLogoPositionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(db)
    return service.update_logo_position(payload, current_user)
