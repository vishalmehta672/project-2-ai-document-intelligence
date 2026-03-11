from app.models.invoice_schema import InvoiceSchema
from app.services.llm_extractor import LLMExtractor
from app.services.pdf_parser import extract_text_from_pdf
from app.workers.celery_app import celery_app
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_document(self, file_path: str, document_type: str):
    """
    Background task to process uploaded document
    """

    try:
        logger.info(f"Starting document processing - File: {file_path}, Type: {document_type}")

        # Step 1 — Parse PDF
        logger.info("Step 1: Extracting text from PDF...")
        text = extract_text_from_pdf(file_path)

        # Step 2 — Send text to LLM
        logger.info("Step 2: Sending extracted text to LLM for structured extraction...")
        logger.debug(f"Extracted text length::::::: {text}")
        structured_data = LLMExtractor.extract_invoice_data(text)
        logger.info(f"LLM extraction completed <<->> Extracted fields: {structured_data}")
        
        if "error" in structured_data:
            logger.error(f"LLM extraction error: {structured_data['error']}")
            raise Exception(f"LLM extraction failed: {structured_data['error']}")

        # Step 3 — Validate with schema
        logger.info("Step 3: Validating extracted data against InvoiceSchema...")
        invoice = InvoiceSchema(**structured_data)
        logger.info(f"Validation successful - Invoice: {invoice.invoice_number}")

        logger.info("Document processing completed successfully")

        return {
            "file_path": file_path,
            "document_type": document_type,
            "extracted_text": text,
            "structured_data": invoice.dict(),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }


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