from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.response_models import HandwritingResponse
from app.services.handwriting_service import HandwritingService
from app.utils.file_utils import save_upload_to_temp, cleanup_temp_file, is_image_file

router = APIRouter()
hw_service = HandwritingService()


@router.post("/handwriting", response_model=HandwritingResponse)
async def handwriting_endpoint(
    file: UploadFile = File(...),
    language: str = Form("eng"),
    enhance: bool = Form(True),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if not is_image_file(file.filename):
        raise HTTPException(status_code=400, detail="File must be an image")

    temp_path = None
    try:
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

        suffix = "." + file.filename.rsplit(".", 1)[-1] if "." in file.filename else ".png"
        temp_path = save_upload_to_temp(content, suffix=suffix)

        result = hw_service.recognize(temp_path, language=language, enhance=enhance)
        return HandwritingResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        return HandwritingResponse(text="", error=str(e))
    finally:
        if temp_path:
            cleanup_temp_file(temp_path)
