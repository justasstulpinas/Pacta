from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import Response

from app.database import get_db
from app.dependencies.auth import get_current_user

from app.schemas.filled_contract import FilledContractResponse
from app.services.filled_contract_service import FilledContractService
from app.services.contract_submission_service import ContractSubmissionService
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
    service = FilledContractService(db)
    submission = service.get_submission_by_id(submission_id, current_user)
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
    service = FilledContractService(db)
    submission = service.confirm_submission(submission_id, current_user)
    return submission


@router.get("/submissions/{submission_id}/document")
def get_submission_document(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ContractSubmissionService(db)
    html = service.get_submission_document_html(submission_id, current_user)
    return {"html": html}


@router.get("/submissions/{submission_id}/pdf")
def get_submission_pdf(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ContractSubmissionService(db)
    pdf = service.get_submission_document_pdf(submission_id, current_user)
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
    service = ContractSubmissionService(db)
    docx = service.get_submission_document_docx(submission_id, current_user)
    filename = FileManager.generate_filename(submission_id, "docx")

    return Response(
        content=docx,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(docx)),
        },
    )
