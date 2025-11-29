import streamlit as st
from main import AURORA
import os

# Page config
st.set_page_config(
    page_title="AURORA - AI Assistant",
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

aurora = st.session_state.aurora

# Header
st.markdown('<p class="main-header">🌟 AURORA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Unified Reasoning & Organisation Resource Agent</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Ingest Documents", "📊 Knowledge Base"])

# TAB 1: Chat Interface
with tab1:
    st.subheader("Chat with AURORA")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = aurora.chat(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# TAB 2: Document Ingestion
with tab2:
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

# TAB 3: Knowledge Base
with tab3:
    st.subheader("Knowledge Base Overview")
    
    stats = aurora.memory.get_collection_stats()
    st.metric("Total Chunks", stats['count'])
    
    st.markdown("### Search")
    query = st.text_input("Search query:")
    
    if st.button("🔍 Search"):
        if query:
            results = aurora.memory.search(query, k=5)
            for i, doc in enumerate(results, 1):
                with st.expander(f"Result {i}"):
                    st.text(doc.page_content)
