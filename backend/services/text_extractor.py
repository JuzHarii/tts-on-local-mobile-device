import pdfplumber
from docx import Document
import os

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(
        p.text.strip() for p in doc.paragraphs if p.text.strip()
    )

def extract_text_from_pdf(path: str) -> str:
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
    return "\n".join(texts)

def extract_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return extract_text_from_docx(path)
    elif ext == ".pdf":
        return extract_text_from_pdf(path)
    else:
        raise ValueError("Unsupported file type")
