import PyPDF2
from docx import Document
import os

def read_pdf(file_path):
    """Read and extract text from PDF files"""
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def read_docx(file_path):
    """Read and extract text from DOCX files"""
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def read_document(file_path):
    """Smart reader - automatically chooses correct reader based on file extension"""
    if file_path.endswith(".pdf"):
        return read_pdf(file_path)
    elif file_path.endswith(".docx"):
        return read_docx(file_path)
    else:
        return "Unsupported file format"
