import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
import io
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os

def extract_with_pdfplumber(pdf_path):
    """
    Extract text using pdfplumber - good for maintaining formatting
    and handling complex PDFs with tables
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error with pdfplumber: {str(e)}"

def extract_with_pypdf2(pdf_path):
    """
    Extract text using PyPDF2 - faster but simpler approach,
    might miss some formatting
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error with PyPDF2: {str(e)}"

def extract_with_pymupdf(pdf_path):
    """
    Extract text using PyMuPDF (fitz) - fast and accurate,
    good for complex PDFs
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            fixed_text = page.get_text().encode('latin1').decode('cp1251')
            text += fixed_text + "\n"
        doc.close()
        return text
    except Exception as e:
        return f"Error with PyMuPDF: {str(e)}"

def extract_with_ocr(pdf_path):
    """
    Extract text using OCR (Tesseract) - useful for scanned PDFs
    or when text extraction fails
    """
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        text = ""
        
        for image in images:
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(img_byte_arr))
            
            # Extract text from image using OCR
            text += pytesseract.image_to_string(img) + "\n"
            
        return text
    except Exception as e:
        return f"Error with OCR: {str(e)}"

def extract_text_from_pdf(pdf_path, method='all'):
    """
    Main function to extract text using specified method
    
    Args:
        pdf_path (str): Path to PDF file
        method (str): Extraction method ('pdfplumber', 'pypdf2', 'pymupdf', 'ocr', 'all')
    
    Returns:
        dict: Results from each specified method
    """
    methods = {
        'pdfplumber': extract_with_pdfplumber,
        'pypdf2': extract_with_pypdf2,
        'pymupdf': extract_with_pymupdf,
        #'ocr': extract_with_ocr
    }
    
    results = {}
    
    if method == 'all':
        for name, func in methods.items():
            results[name] = func(pdf_path)
    elif method in methods:
        results[method] = methods[method](pdf_path)
    else:
        raise ValueError(f"Invalid method. Choose from: {', '.join(methods.keys())}")
    
    return results

# Example usage
if __name__ == "__main__":
    pdf_path = "/home/nart/Documents/Lingua-Corpus/data/raw/ady/2009/02.05.pdf"
    
    # Extract using all methods
    results = extract_text_from_pdf(pdf_path, method='all')
    
    # Print results from each method
    for method, text in results.items():
        print(f"\n=== Results from {method} ===")
        print(text[:500] + "..." if len(text) > 500 else text)
