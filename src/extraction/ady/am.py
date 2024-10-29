import subprocess, os, glob, fitz, re
from tqdm import tqdm

def root_dir():
    return subprocess.check_output(["git", "rev-parse", "--show-toplevel"], universal_newlines=True).strip()

def get_all_files_in_directory(directory):
    pattern = os.path.join(directory, '**', '*')
    return [f for f in glob.glob(pattern, recursive=True) if os.path.isfile(f)]
    
def create_file(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f: 
        f.write('')

def replace_between_letters(target_letter, replacement, text):
    pattern = f'(?<=[А-Яа-яЁё]){target_letter}(?=[А-Яа-яЁё])'
    return re.sub(pattern, replacement, text, flags=re.UNICODE)

def replace_no_letters_before(target_letter, replacement, text):
    pattern = f'(?<![А-Яа-яЁё]){target_letter}'
    return re.sub(pattern, replacement, text, flags=re.UNICODE)
    
def replace_no_letters_after(target_letter, replacement, text):
    pattern = f'{target_letter}(?![А-Яа-яЁё])'
    return re.sub(pattern, replacement, text, flags=re.UNICODE)
    
def clean_text(text):
    text = re.sub(r' +', ' ', text) # remove extra white spaces
    text = re.sub(r'\n\s*\n', '\n', text) # remove extra line breaks
    text = re.sub(r'[-\xad]\n', '', text) # remove line break hyphens
    text = re.sub(r'\xad', '', text) # remove soft hyphens
    text = replace_between_letters('I', 'ӏ', text) # u04CF cyrillic letter small palocka
    text = replace_no_letters_before('I', 'Ӏ', text) # u04C0 cyrillic letter capital palocka
    text = replace_no_letters_after('I', 'ӏ', text) # u04CF cyrillic letter small palocka
    return text.strip()
    
def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        fixed_text = page.get_text().encode('latin1', errors='ignore').decode('cp1251')
        text += fixed_text + "\n"
    doc.close()
    return text

def print_unique_chars(filename):
    unique_chars = set()
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            for char in line:
                unique_chars.add(char)
    
    print("Unique characters in the file:")
    print(sorted(unique_chars))
    
files = get_all_files_in_directory(root_dir()+'/data/raw/ady/')
output = root_dir()+"/data/interim/ady/ady/1.txt"
create_file(output)
with open(output, 'a', encoding='utf-8') as f:
    for path in tqdm(files):
        text = extract_pdf(path)
        text = clean_text(text)
        f.write(text + '\n')
        
print_unique_chars(output)
