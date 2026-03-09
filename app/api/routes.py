from fastapi import APIRouter, UploadFile, File
from app.services.pdf_parser import extract_text_from_pdf

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    
    contents = await file.read()

    text = extract_text_from_pdf(contents)

    return {
        "filename": file.filename,
        "text_preview": text[:500]
    }