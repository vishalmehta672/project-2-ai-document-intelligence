import fitz  # PyMuPDF
import io


def extract_text_from_pdf(file_bytes: bytes):

    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text()

    return text