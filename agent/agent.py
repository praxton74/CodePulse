from langgraph.prebuilt import create_react_agent
from agent.tools import get_tools
import os 
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")                           # Keeps your agent's tools stable
)
SYSTEM_PROMPT = """You are RepoMind, an AI assistant that helps users understand GitHub repositories.
You have access to 3 tools:
- code_search: search the codebase for functions and classes
- github_api: fetch PRs, issues, commits from GitHub
- web_search: search the web for external docs or error explanations

Always cite the file name and line numbers when answering about code.
If you're unsure, search before answering — never guess."""
def run_agent(repo_name:str,question:str, github_token:str = None):
    tools = get_tools(repo_name, github_token)
    agent = create_react_agent(llm, tools,prompt=SYSTEM_PROMPT)
    result = agent.invoke({"messages": [("user", question)]})
    last_message = result["messages"][-1]

    # handle Gemini's response format
    if hasattr(last_message, 'content'):
        content = last_message.content
        if isinstance(content, list):
            # Gemini returns list of content blocks
            return " ".join([c.get("text", "") for c in content if isinstance(c, dict)])
        return content
    return str(last_message)
