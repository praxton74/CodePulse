import os 
from ingestion.parser import parse_file
from ingestion.chroma import store_chunks
from ingestion.clone_repo import clone_repo
import shutil

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}


import stat

def handle_remove_readonly(func,path,exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)
    
def ingest(github_url:str):
    repo_name = github_url.split("/")[-1].replace(".git","")
    temp_dir = clone_repo(github_url, f"./temp/{repo_name}")
    
    chunks = []
    try:
        for dirpath, dirnames,filenames in os.walk(temp_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for f in filenames:
                full_path = os.path.join(dirpath,f)
                file_chunks = parse_file(full_path)
                
                rel = os.path.relpath(full_path,temp_dir)
                for c in file_chunks:
                    c["file"] = rel
                chunks.extend(file_chunks)
        print(f"Extracted {len(chunks)} chunks")
        store_chunks(repo_name, chunks)
    finally:
        shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
    return {"repo":repo_name,"chunks":len(chunks)}