from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from utils.document_processor import DocumentProcessor
from memory.vector_store import VectorMemory
from typing import List
from langchain.schema import Document
from config import Config

class ReadingCompanion:
    """Reads and processes documents, extracting insights."""
    
    def __init__(self, vector_memory: VectorMemory):
        self.memory = vector_memory
        self.processor = DocumentProcessor()
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=Config.SUMMARIZATION_TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
    
    def ingest_document(self, file_path: str) -> str:
        """Ingest a document and add it to memory."""
        # Determine file type and load
        if file_path.endswith('.pdf'):
            chunks = self.processor.load_pdf(file_path)
        elif file_path.endswith('.txt'):
            chunks = self.processor.load_text(file_path)
        else:
            return f"Unsupported file type: {file_path}"
        
        # Add to vector store
        self.memory.add_documents(chunks)
        
        return f"Successfully ingested {len(chunks)} chunks from {file_path}"
    
    def summarize_document(self, file_path: str) -> str:
        """Summarize a document."""
        # Load document
        if file_path.endswith('.pdf'):
            chunks = self.processor.load_pdf(file_path)
        elif file_path.endswith('.txt'):
            chunks = self.processor.load_text(file_path)
        else:
            return f"Unsupported file type: {file_path}"
        
        # Use summarization chain
        chain = load_summarize_chain(
            self.llm,
            chain_type="map_reduce"
        )
        
        summary = chain.run(chunks)
        
        # Store summary in memory
        self.memory.add_text(
            summary,
            metadata={
                "type": "summary",
                "source": file_path,
                "original_chunks": len(chunks)
            }
        )
        
        return summary
    
    def extract_insights(self, file_path: str) -> str:
        """Extract key insights from a document."""
        # First get summary
        summary = self.summarize_document(file_path)
        
        # Extract insights using LLM
        prompt = PromptTemplate(
            input_variables=["summary"],
            template="""Based on this document summary, extract 3-5 key insights or takeaways:

Summary:
{summary}

Provide insights as a numbered list."""
        )
        
        response = self.llm.invoke(prompt.format(summary=summary))
        
        return response.content
