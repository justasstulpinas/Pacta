from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import Response

from app.database import get_db
from app.dependencies.auth import get_current_user

from app.schemas.filled_contract import FilledContractResponse
from app.services.filled_contract_service import (
    get_submission_by_id,
    confirm_contract,
)
from app.services.contract_submission_service import (
    get_submission_document_html,
    get_submission_document_pdf,
    get_submission_document_docx,
)
from app.files.file_manager import FileManager

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
)


@router.get(
    "/submissions/{submission_id}",
    response_model=FilledContractResponse,
)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    submission = get_submission_by_id(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )
    return submission


@router.post(
    "/submissions/{submission_id}/confirm",
    response_model=FilledContractResponse,
)
def confirm_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    submission = confirm_contract(
        db=db,
        submision_id=submission_id,
        current_user=current_user,
    )
    return submission


@router.get("/submissions/{submission_id}/document")
def get_submission_document(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    html = get_submission_document_html(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )
    return {"html": html}


@router.get("/submissions/{submission_id}/pdf")
def get_submission_pdf(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    pdf = get_submission_document_pdf(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    filename = FileManager.generate_filename(submission_id, "pdf")

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf)),
        },
    )


@router.get("/submissions/{submission_id}/docx")
def get_submission_docx(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docx = get_submission_document_docx(
        db=db,
        submission_id=submission_id,
        current_user=current_user,
    )

    filename = FileManager.generate_filename(submission_id, "docx") 

    return Response(
        content=docx,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(docx)),
        },
    )