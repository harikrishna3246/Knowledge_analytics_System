import PyPDF2
from docx import Document
import os
import hashlib

def get_file_hash(file_path):
    """Generate SHA-256 hash for a file to identify duplicates."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def read_pdf(file_path):
    """Read and extract text from PDF files, attempting to identify headings."""
    text = ""
    headings = []
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            text += page_text + "\n"
            
            # Simple heuristic for headings in PDF text:
            # Usually short lines (less than 60 chars) that don't end with a period
            # and may be in uppercase or start with a number.
            lines = page_text.split('\n')
            for line in lines:
                clean_line = line.strip()
                if 2 < len(clean_line) < 60 and not clean_line.endswith('.'):
                    headings.append(clean_line)
                    
    return text, headings

def read_docx(file_path):
    """Read and extract text from DOCX files, identifying headings via styles."""
    doc = Document(file_path)
    text = ""
    headings = []
    for para in doc.paragraphs:
        text += para.text + "\n"
        # Check if the paragraph has a heading style
        if para.style.name.startswith('Heading') or para.style.name == 'Title':
            headings.append(para.text.strip())
        # Fallback: Bold paragraphs that are short
        elif len(para.text.strip()) < 60 and any(run.bold for run in para.runs):
            headings.append(para.text.strip())
            
    return text, headings

def read_document(file_path):
    """Smart reader - automatically chooses correct reader based on file extension.
    Returns (text, headings)"""
    if file_path.endswith(".pdf"):
        return read_pdf(file_path)
    elif file_path.endswith(".docx"):
        return read_docx(file_path)
    else:
        return "Unsupported file format", []
