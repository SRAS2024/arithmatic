from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.response_models import PDFResponse
from app.services.pdf_service import PDFService
from app.utils.file_utils import save_upload_to_temp, cleanup_temp_file, is_pdf_file

router = APIRouter()
pdf_service = PDFService()


@router.post("/pdf", response_model=PDFResponse)
async def pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not is_pdf_file(file.filename):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    temp_path = None
    try:
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

        temp_path = save_upload_to_temp(content, suffix=".pdf")
        result = pdf_service.process_pdf(temp_path)
        return PDFResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        return PDFResponse(error=str(e))
    finally:
        if temp_path:
            cleanup_temp_file(temp_path)
