import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from pathlib import Path
PY_LANGUAGE = Language(tspython.language())

parser = Parser(PY_LANGUAGE)
NODE_TYPES = ["function_definition", "class_definition"]
MAX_CHUNK_WORDS = 400

def parse_file(file_path:str) -> list[dict]:
    if Path(file_path).suffix != ".py":
        return []
    
    with open(file_path, "rb") as f:
        source = f.read()
    
    tree = parser.parse(source)
    chunks = []
    
    for node in walk(tree.root_node):
        if node.type in NODE_TYPES:
            text = source[node.start_byte:node.end_byte].decode("utf-8",errors="ignore")
            name = get_name(node)
            
            if len(text.split()) > MAX_CHUNK_WORDS:
                lines = text.split("\n")
                for i in range(0,len(lines),35):
                    chunk_lines = lines[i:i+35]
                    chunks.append({
                        "text":"\n".join(chunk_lines),
                        "type": "large_chunk",
                        "name": f"{name}_part{i}",
                        "file": file_path,
                        "line_start": node.start_point[0] + 1 + i,
                        "line_end": node.start_point[0] + 1 + i + len(chunk_lines),
                    })
            else:
                chunks.append({
                    "text": text,
                    "type": node.type,
                    "name": name,
                    "file": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                })
    return chunks

def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)
        
def get_name(node)->str:
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode("utf-8")
    return "unknown"