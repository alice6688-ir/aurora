import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from main import AURORA

# Page config
st.set_page_config(
    page_title="AURORA",
    page_icon="🌟",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    color: #4A90E2;
    margin-bottom: 0.5rem;
}
.sub-header {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize AURORA
@st.cache_resource
def get_aurora():
    return AURORA()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'aurora' not in st.session_state:
    st.session_state.aurora = get_aurora()

if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Chat"

aurora = st.session_state.aurora

# Header
st.markdown('<p class="main-header">🌟 AURORA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Unified Reasoning & Organisation Resource Agent</p>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["💬 Chat", "📚 Ingest Documents", "📊 Knowledge Base"])

# ============================================================================
# PAGE 1: Chat Interface
# ============================================================================
if page == "💬 Chat":
    st.subheader("Chat with AURORA")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input (NOT inside tabs/columns)
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AURORA's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = aurora.chat(prompt)
                st.markdown(response)

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})

# ============================================================================
# PAGE 2: Document Ingestion
# ============================================================================
elif page == "📚 Ingest Documents":
    st.subheader("Ingest Documents into AURORA's Memory")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=['pdf', 'txt']
    )

    if uploaded_file is not None:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Ingest Document"):
                with st.spinner("Ingesting..."):
                    result = aurora.ingest_document(temp_path)
                    st.success(result)
                os.remove(temp_path)

        with col2:
            if st.button("📝 Summarize"):
                with st.spinner("Summarizing..."):
                    summary = aurora.summarize_document(temp_path)
                    st.info(summary)
                os.remove(temp_path)

    st.markdown("---")

    st.markdown("### Manual Text Entry")
    text_input = st.text_area("Enter text to add to knowledge base", height=200)
    text_title = st.text_input("Title (optional)")

    if st.button("➕ Add to Knowledge Base"):
        if text_input:
            metadata = {
                "type": "manual_entry",
                "title": text_title or "Untitled"
            }
            result = aurora.knowledge_butler.add_knowledge(text_input, metadata)
            st.success(result)
        else:
            st.error("Please enter some text!")

# ============================================================================
# PAGE 3: Knowledge Base
# ============================================================================
elif page == "📊 Knowledge Base":
    st.subheader("Knowledge Base Overview")

    # Get stats
    stats = aurora.memory.get_collection_stats()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Chunks", stats['count'])
    with col2:
        st.metric("Database", stats['name'])

    st.markdown("---")

    # Search interface
    st.markdown("### Search Knowledge Base")
    search_query = st.text_input("Enter search query:")
    num_results = st.slider("Number of results", 1, 10, 5)

    if st.button("🔍 Search"):
        if search_query:
            with st.spinner("Searching..."):
                results = aurora.memory.search(search_query, k=num_results)

                if results:
                    st.success(f"Found {len(results)} results:")
                    for i, doc in enumerate(results, 1):
                        with st.expander(f"Result {i}: {doc.metadata.get('filename', 'Unknown')}"):
                            st.markdown(f"**Source:** {doc.metadata.get('source', 'N/A')}")
                            st.markdown(f"**Type:** {doc.metadata.get('type', 'N/A')}")
                            st.markdown("**Content:**")
                            st.text(doc.page_content)
                else:
                    st.warning("No results found.")
        else:
            st.error("Please enter a search query!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**AURORA v1.0**")
st.sidebar.markdown("Your Personal AI Brain 🧠")
