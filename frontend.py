import streamlit as st
import requests

API_URL = "https://repomind-production-96d6.up.railway.app"

st.set_page_config(page_title="RepoMind", page_icon="🧠", layout="wide")
st.title("🧠 RepoMind")
st.caption("Chat with any GitHub repository")

# sidebar
with st.sidebar:
    st.header("Connect a Repository")
    
    input_type = st.radio("How do you want to connect?", ["GitHub URL (ingest)", "Repo name (already indexed)"])
    
    if input_type == "GitHub URL (ingest)":
        github_url = st.text_input("GitHub URL", placeholder="https://github.com/username/repo")
        github_token = st.text_input("GitHub Token (optional, for private repos)", type="password")
        
        if st.button("Ingest Repo", type="primary"):
            if github_url:
                with st.spinner("Cloning and indexing repo... this may take a moment"):
                    res = requests.post(f"{API_URL}/ingest", json={"github_url": github_url})
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"✅ Done! {data['result']['chunks']} chunks indexed")
                        repo_name = github_url.rstrip("/").split("/")[-1]
                        repo_full = "/".join(github_url.rstrip("/").split("/")[-2:])
                        st.session_state.repo_name = repo_name
                        st.session_state.repo_full = repo_full
                        st.session_state.github_token = github_token or None
                    else:
                        st.error(f"Failed to ingest: {res.text}")
            else:
                st.warning("Please enter a GitHub URL")

    else:
        col1, col2 = st.columns(2)
        with col1:
            repo_name_only = st.text_input("Repo name", placeholder="rag-from-scratch")
        with col2:
            repo_full_only = st.text_input("Full name (optional)", placeholder="NotKshitiz/rag-from-scratch")
        
        github_token_only = st.text_input("GitHub Token (optional)", type="password")

        if st.button("Use this repo", type="primary"):
            if repo_name_only:
                st.session_state.repo_name = repo_name_only
                st.session_state.repo_full = repo_full_only or None
                st.session_state.github_token = github_token_only or None
                st.success(f"✅ Using `{repo_name_only}`")
            else:
                st.warning("Please enter a repo name")

    # show active repo
    if "repo_name" in st.session_state:
        st.divider()
        st.info(f"**Active repo:** `{st.session_state.repo_name}`")
        if st.session_state.get("repo_full"):
            st.caption(f"GitHub: {st.session_state.repo_full}")
        
        # clear button
        if st.button("Clear / Switch repo"):
            for key in ["repo_name", "repo_full", "github_token", "messages"]:
                st.session_state.pop(key, None)
            st.rerun()

# main chat area
if "repo_name" not in st.session_state:
    st.info("👈 Connect a repository from the sidebar to get started")
    
    st.subheader("What can you ask?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔍 Code questions**")
        st.caption("How does the retrieve function work?")
        st.caption("What does rag.py do?")
        st.caption("Explain the chunking logic")
    with col2:
        st.markdown("**🐙 GitHub questions**")
        st.caption("What are the open issues?")
        st.caption("What changed in the last PR?")
        st.caption("Who are the contributors?")
    with col3:
        st.markdown("**🌐 External questions**")
        st.caption("What is FAISS IndexFlatIP?")
        st.caption("How does cosine similarity work?")
        st.caption("What's the difference between FAISS and ChromaDB?")

else:
    # chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # suggested questions if no messages yet
    if not st.session_state.messages:
        st.subheader("Try asking:")
        suggestions = [
            "Give me an overview of this codebase",
            "How does the main function work?",
            "What are the open issues?",
            "Explain the most important file in this repo"
        ]
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            if cols[i % 2].button(suggestion):
                st.session_state.pending_question = suggestion
                st.rerun()

    # handle suggested question click
    if "pending_question" in st.session_state:
        prompt = st.session_state.pop("pending_question")
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = requests.post(f"{API_URL}/chat", json={
                    "repo_name": st.session_state.repo_name,
                    "repo_full_name": st.session_state.get("repo_full"),
                    "question": prompt,
                    "github_token": st.session_state.get("github_token")
                })
                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {res.text}")

    # chat input
    if prompt := st.chat_input("Ask anything about the repo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = requests.post(f"{API_URL}/chat", json={
                    "repo_name": st.session_state.repo_name,
                    "repo_full_name": st.session_state.get("repo_full"),
                    "question": prompt,
                    "github_token": st.session_state.get("github_token")
                })
                if res.status_code == 200:
                    answer = res.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {res.text}")