from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from app.workers.tasks import process_document
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("data/uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"data/uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine document type from extension
        document_type = file.filename.split(".")[-1].lower()
        
        # Trigger Celery task
        task = process_document.delay(file_path, document_type)
        
        logger.info(f"Document uploaded: {file.filename}, Task ID: {task.id}")
        
        return {
            "task_id": task.id,
            "filename": file.filename,
            "document_type": document_type,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a processing task"""
    from app.workers.celery_app import celery_app
    
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }