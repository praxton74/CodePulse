from langchain_core.tools import tool
from ingestion.chat import ask_repo
import os 
from dotenv import load_dotenv
from tavily import TavilyClient
from github import Github
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def get_tools(repo_name: str,repo_full_name: str = None, github_token: str = None):
    gh = Github(github_token) if github_token else None
    @tool
    def code_search(query:str)->str:
        """Search the codebase for ANYTHING related to the repo — functions, classes, 
    files, logic, implementation details. Use this for ANY question about the code
    including questions about specific files like 'tell me about rag.py' or 
    'what does main.py contain'."""
        return ask_repo(repo_name, query) 
    
    @tool
    def web_search(query:str)->str:
        """Search the web for external documentation, error explanations, 
        library usage, or anything not found in the codebase itself."""
        results = tavily.search(query, max_results=3)
        return results

    @tool
    def github_api(query: str) -> str:
        """Fetch PRs, issues, commits and repo info from GitHub.
        Use for questions about recent changes, open issues, contributors, or repo history."""
        if not gh:
            return "No GitHub token provided — cannot fetch GitHub data"
        
        try:
            # extract username/repo from repo_name stored in closure
            repo = gh.get_repo(repo_full_name or repo_name)  # needs full name like "NotKshitiz/rag-from-scratch"
            
            results = {
                "open_prs": [{"title": pr.title, "number": pr.number} for pr in repo.get_pulls(state="open")[:5]],
                "open_issues": [{"title": i.title, "number": i.number} for i in repo.get_issues(state="open")[:5]],
                "recent_commits": [{"message": c.commit.message, "author": c.commit.author.name} for c in repo.get_commits()[:5]],
                "description": repo.description,
                "stars": repo.stargazers_count,
            }
            return str(results)
        except Exception as e:
            return f"GitHub API error: {str(e)}"

    return [code_search, web_search, github_api]       
    
    # @tool
    # def read_file(file_path: str) -> str:
    #         """Read a specific file from the repo by its path.
    #         Use when asked for the full content, "show me the entire file",Do NOT use for general questions"""
    #         repo = gh.get_repo(repo_name)
    #         try:
    #             content = repo.get_contents(file_path)
    #             return content.decoded_content.decode("utf-8")
    #         except Exception as e:
    #             return f"Could not read file {file_path}: {str(e)}"
       