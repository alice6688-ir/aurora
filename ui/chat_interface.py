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
.feature-box {
    padding: 20px;
    border-radius: 10px;
    background-color: #f0f2f6;
    margin: 10px 0;
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

# Sidebar for navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", [
    "💬 Chat",
    "📖 Reading Companion",
    "📚 Knowledge Base",
    "📧 Email Manager (Coming Soon)",
    "💻 Code Assistant (Coming Soon)"
])

# ============================================================================
# PAGE 1: Chat Interface
# ============================================================================
if page == "💬 Chat":
    st.subheader("💬 Chat with AURORA")
    st.info("Ask questions about your knowledge base or get help with tasks!")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = aurora.chat(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ============================================================================
# PAGE 2: Reading Companion
# ============================================================================
elif page == "📖 Reading Companion":
    st.subheader("📖 Reading Companion")
    st.markdown("Upload documents to read, summarize, and extract insights.")

    # File upload section
    st.markdown("### 📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=['pdf', 'txt'],
        help="Upload a document to analyze"
    )

    if uploaded_file is not None:
        # Save file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Loaded: {uploaded_file.name}")

        # Action buttons
        st.markdown("### 🎯 Choose Action")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 Ingest & Store", use_container_width=True):
                with st.spinner("Reading and storing document..."):
                    result = aurora.ingest_document(temp_path)
                    st.success(result)
                    st.info("💡 Document is now searchable in your knowledge base!")
                os.remove(temp_path)

        with col2:
            if st.button("📝 Summarize", use_container_width=True):
                with st.spinner("Generating summary..."):
                    summary = aurora.summarize_document(temp_path)
                    st.markdown("### 📋 Summary")
                    st.markdown(summary)
                os.remove(temp_path)

        with col3:
            if st.button("💡 Extract Insights", use_container_width=True):
                with st.spinner("Extracting key insights..."):
                    insights = aurora.reading_companion.extract_insights(temp_path)
                    st.markdown("### 🔍 Key Insights")
                    st.markdown(insights)
                os.remove(temp_path)

    st.markdown("---")

    # Manual text entry
    st.markdown("### ✍️ Add Text Manually")

    with st.form("manual_text_form"):
        text_input = st.text_area(
            "Paste text content",
            height=200,
            placeholder="Paste article, notes, or any text you want to add to your knowledge base..."
        )

        col1, col2 = st.columns(2)
        with col1:
            text_title = st.text_input("Title (optional)", placeholder="e.g., Machine Learning Notes")
        with col2:
            text_category = st.text_input("Category (optional)", placeholder="e.g., Research, Personal")

        submitted = st.form_submit_button("➕ Add to Knowledge Base", use_container_width=True)

        if submitted:
            if text_input:
                metadata = {
                    "type": "manual_entry",
                    "title": text_title or "Untitled",
                    "category": text_category or "General"
                }
                result = aurora.knowledge_butler.add_knowledge(text_input, metadata)
                st.success("✅ " + result)
            else:
                st.error("❌ Please enter some text first!")

# ============================================================================
# PAGE 3: Knowledge Base
# ============================================================================
elif page == "📚 Knowledge Base":
    st.subheader("📚 Knowledge Base Manager")

    # Stats section
    stats = aurora.memory.get_collection_stats()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total Chunks", stats['count'])
    with col2:
        st.metric("🗄️ Database Type", "FAISS")
    with col3:
        status = "🟢 Active" if stats['count'] > 0 else "🟡 Empty"
        st.metric("Status", status)

    st.markdown("---")

    # Search interface
    st.markdown("### 🔍 Search Your Knowledge")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search query:",
            placeholder="e.g., What did I learn about neural networks?"
        )
    with col2:
        num_results = st.number_input("Results", min_value=1, max_value=20, value=5)

    if st.button("🔍 Search Knowledge Base", use_container_width=True):
        if search_query:
            with st.spinner("Searching..."):
                results = aurora.memory.search(search_query, k=num_results)

                if results:
                    st.success(f"✅ Found {len(results)} results")

                    for i, doc in enumerate(results, 1):
                        with st.expander(f"📄 Result {i}: {doc.metadata.get('filename', 'Unknown source')}"):
                            # Metadata
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**📁 Source:** {doc.metadata.get('source', 'N/A')}")
                            with col2:
                                st.markdown(f"**🏷️ Type:** {doc.metadata.get('type', 'N/A')}")

                            # Content
                            st.markdown("**📝 Content:**")
                            st.text_area(
                                f"Content {i}",
                                doc.page_content,
                                height=150,
                                key=f"content_{i}",
                                disabled=True
                            )
                else:
                    st.warning("⚠️ No results found. Try a different query.")
        else:
            st.error("❌ Please enter a search query!")

    # Quick stats
    st.markdown("---")
    st.markdown("### 📈 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 View Statistics", use_container_width=True):
            st.info(f"""
            **Knowledge Base Stats:**
            - Total documents: {stats['count']} chunks
            - Database: {stats['name']}
            - Status: Ready for queries
            """)

    with col2:
        st.button("📥 Export Data (Coming Soon)", use_container_width=True, disabled=True)

    with col3:
        st.button("🗑️ Clear Database (Coming Soon)", use_container_width=True, disabled=True)

# ============================================================================
# PAGE 4: Email Manager (Placeholder)
# ============================================================================
elif page == "📧 Email Manager (Coming Soon)":
    st.subheader("📧 Email & Communication Manager")

    st.info("🚧 This feature is under development!")

    st.markdown("""
    ### Planned Features:
    
    **📥 Email Integration:**
    - Connect to Gmail/Outlook
    - Automatically summarize incoming emails
    - Classify by priority (urgent, important, low priority)
    
    **✍️ Smart Responses:**
    - Generate context-aware draft replies
    - Suggest response templates
    - Learn from your writing style
    
    **📋 Task Extraction:**
    - Automatically detect action items
    - Create task lists from emails
    - Set reminders for follow-ups
    
    **📊 Email Analytics:**
    - Track email volume by sender
    - Identify patterns in communication
    - Highlight important threads
    """)

    st.markdown("---")
    st.markdown("### 🛠️ Want to build this?")
    st.code("""
# You can start by creating agents/email_agent.py
# It would integrate with Gmail API or IMAP
# And use AURORA's memory for context-aware responses
    """, language="python")

# ============================================================================
# PAGE 5: Code Assistant (Placeholder)
# ============================================================================
elif page == "💻 Code Assistant (Coming Soon)":
    st.subheader("💻 Code Research Assistant")

    st.info("🚧 This feature is under development!")

    st.markdown("""
    ### Planned Features:
    
    **📂 Repository Analysis:**
    - Scan and index entire codebases
    - Understand project structure
    - Map dependencies and imports
    
    **🔍 Code Search:**
    - Find functions by description
    - Locate where variables are used
    - Search across multiple files
    
    **📝 Documentation:**
    - Auto-generate docstrings
    - Create README files
    - Explain complex functions
    
    **🔧 Code Improvement:**
    - Suggest refactoring opportunities
    - Identify code smells
    - Recommend best practices
    
    **🐛 Debugging Helper:**
    - Explain error messages
    - Suggest fixes for common issues
    - Analyze stack traces
    """)

    st.markdown("---")
    st.markdown("### 🛠️ Want to build this?")
    st.code("""
# You can start by creating agents/code_assistant.py
# It would use tree-sitter for code parsing
# And integrate with AURORA's knowledge base
    """, language="python")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Info")
stats = aurora.memory.get_collection_stats()
st.sidebar.metric("Knowledge Items", stats['count'])
st.sidebar.markdown("---")
st.sidebar.markdown("**AURORA v1.0**")
st.sidebar.markdown("🧠 Your Personal AI Brain")
st.sidebar.markdown("[GitHub](https://github.com) • [Docs](https://docs.aurora.ai)")
