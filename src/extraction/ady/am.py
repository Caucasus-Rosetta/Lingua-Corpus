import subprocess, os, glob, fitz, re
from tqdm import tqdm

def root_dir():
    return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], universal_newlines=True).strip()

def create_file(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f: 
        f.write('')
        
def clean_text(text):
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'-\n', '', text)
    return text.strip()
    
def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        fixed_text = page.get_text().encode('latin1', errors='ignore').decode('cp1251')
        text += fixed_text + "\n"
    doc.close()
    return text
        
files = glob.glob(root_dir()+'/data/raw/ady/2009/*')
output = root_dir()+"/data/interim/ady/ady/1.txt"
create_file(output)
with open(output, 'a', encoding='utf-8') as f:
    for path in tqdm(files):
        text = extract_pdf(path)
        text = clean_text(text)
        f.write(text + '\n')
