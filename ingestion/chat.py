from ingestion.chroma import query_chunks
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_repo(repo_name:str,question:str)-> str:
    results = query_chunks(repo_name,question,top_k=5)
    
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    
    context = ""
    for doc,meta in zip(docs,metas):
        context += f"\n# {meta['file']} :: {meta['name']} (line {meta['line_start']}-{meta['line_end']})\n"
        context += doc + "\n"
        
    prompt = f"""You are a code assistant. Answer the question using ONLY the code context below.
Always cite the file and function name in your answer.

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content