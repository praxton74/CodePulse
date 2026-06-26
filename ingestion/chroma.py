import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_fn = SentenceTransformerEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(repo_name:str):
    safe = repo_name.replace("/","_").replace(".","_")
    return chroma_client.get_or_create_collection(
        name=f"repo_{safe}",
        embedding_function=embedding_fn
        )
    
def store_chunks(repo_name:str,chunks:list[dict]):
    collection = get_collection(repo_name)
    collection.add(
        documents = [c["text"] for c in chunks],
        metadatas = [
            {
                "file": c["file"],
                "name": c["name"],
                "type": c["type"],
                "line_start": c["line_start"],
                "line_end": c["line_end"]
            }
            for c in chunks
        ],
        ids = [f"{c['file']}::{c['name']}::{i}" for i,c in enumerate(chunks)]
    )
    print(f"Stored {len(chunks)} chunks for repo {repo_name} in ChromaDB")
    
def query_chunks(repo_name:str,question:str,top_k:int = 5):
    collection = get_collection(repo_name)
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )
    return results