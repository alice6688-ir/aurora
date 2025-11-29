from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import List
import os
from config import Config

class DocumentProcessor:
    """Handles document loading and chunking."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load and chunk a PDF file."""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                "source": file_path,
                "type": "pdf",
                "filename": os.path.basename(file_path)
            })
        
        return self.text_splitter.split_documents(documents)
    
    def load_text(self, file_path: str) -> List[Document]:
        """Load and chunk a text file."""
        loader = TextLoader(file_path)
        documents = loader.load()
        
        for doc in documents:
            doc.metadata.update({
                "source": file_path,
                "type": "text",
                "filename": os.path.basename(file_path)
            })
        
        return self.text_splitter.split_documents(documents)
    
    def process_text(self, text: str, metadata: dict) -> List[Document]:
        """Process raw text into chunks."""
        doc = Document(page_content=text, metadata=metadata)
        return self.text_splitter.split_documents([doc])
