import os
from dulwich import porcelain

def clone_repo(repo_url: str, destination_path: str) -> str:
    try:
        os.makedirs(os.path.dirname(destination_path) or ".", exist_ok=True)
        print(f"Cloning {repo_url}...")
        porcelain.clone(repo_url, destination_path, depth=1)
        print(f"Repository cloned to {destination_path}")
        return destination_path
    except Exception as e:
        raise RuntimeError(f"Failed to clone repository {repo_url}: {e}")