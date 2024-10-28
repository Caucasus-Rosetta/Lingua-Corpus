import subprocess
import os
import glob

def get_git_root():
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            universal_newlines=True
        ).strip()
        return root
    except subprocess.CalledProcessError:
        return None
        
files = glob.glob(get_git_root()+'/data/raw/ady/2009/*')
print(files)
