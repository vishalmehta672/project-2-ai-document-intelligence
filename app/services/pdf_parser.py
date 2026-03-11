import fitz  # PyMuPDF
import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str):
    """Extract text from PDF file"""
    try:
        logger.info(f"Starting PDF extraction from: {file_path}")
        
        # Read file bytes
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        logger.debug(f"Loaded PDF file with size: {len(file_bytes)} bytes")
        
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        logger.info(f"PDF opened successfully, total pages: {pdf.page_count}")
        
        text = ""
        for page_num, page in enumerate(pdf):
            page_text = page.get_text()
            text += page_text
            logger.debug(f"Extracted page {page_num + 1}/{pdf.page_count}: {len(page_text)} characters")
        
        pdf.close()
        
        logger.info(f"PDF extraction completed successfully, total text: {len(text)} characters")
        return text
        
    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}", exc_info=True)
        raise