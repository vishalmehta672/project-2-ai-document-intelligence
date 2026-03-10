from app.workers import celery_app
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes):
    """Extract text from PDF file"""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text


@celery_app.task(bind=True, name="process_document", max_retries=3)
def process_document(self, file_path: str, document_type: str):
    """Process document intelligently"""
    try:
        logger.info(f"Processing document: {file_path} of type: {document_type}")
        
        # Read file bytes
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        # Extract text based on document type
        if document_type.lower() == "pdf":
            extracted_text = extract_text_from_pdf(file_bytes)
        else:
            extracted_text = "Unsupported document type"
        
        result = {
            "file_path": file_path,
            "document_type": document_type,
            "extracted_text": extracted_text,
            "status": "completed",
        }
        logger.info(f"Document processing completed: {file_path}")
        return result
    except Exception as exc:
        logger.error(f"Error processing document {file_path}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="extract_text", max_retries=3)
def extract_text(file_path: str):
    """Extract text from document"""
    try:
        logger.info(f"Extracting text from: {file_path}")
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        extracted_text = extract_text_from_pdf(file_bytes)
        return {"text": extracted_text, "file_path": file_path}
    except Exception as exc:
        logger.error(f"Error extracting text from {file_path}: {str(exc)}")
        raise exc