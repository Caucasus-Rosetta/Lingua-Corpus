import subprocess, os, glob, fitz, re
from tqdm import tqdm

def root_dir():
    return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], universal_newlines=True).strip()

def create_file(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f: 
        f.write('')
        
def clean_text(text, replace_chars={'':''}):
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    for old, new in replace_chars.items():
       text = re.sub(old, new, text)
    return text.strip()
    
def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        try:
            fixed_text = page.get_text().encode('latin1').decode('cp1251')
        except:
            fixed_text = page.get_text()
        text += fixed_text + "\n"
    doc.close()
    return text
        
files = glob.glob(root_dir()+'/data/raw/ady/2009/*')
output = root_dir()+"/data/interim/ady/1.txt"
create_file(output)
with open(output, 'a', encoding='utf-8') as f:
    for path in tqdm(files):
        text = extract_pdf(path)
        text = clean_text(text,{r'-\n':''})
        f.write(text + '\n')
