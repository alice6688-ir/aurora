from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import List, Dict, Optional
import chromadb
from config import Config

class VectorMemory:
    """Manages the vector database for AURORA's long-term memory."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.vectorstore = Chroma(
            collection_name=Config.COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=Config.CHROMA_DB_PATH
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        ids = self.vectorstore.add_documents(documents)
        return ids
    
    def add_text(self, text: str, metadata: Dict) -> str:
        """Add a single text with metadata."""
        doc = Document(page_content=text, metadata=metadata)
        ids = self.vectorstore.add_documents([doc])
        return ids[0]
    
    def search(self, query: str, k: int = Config.TOP_K_RESULTS, 
               filter_dict: Optional[Dict] = None) -> List[Document]:
        """Semantic search over stored documents."""
        if filter_dict:
            results = self.vectorstore.similarity_search(
                query, k=k, filter=filter_dict
            )
        else:
            results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def search_with_score(self, query: str, k: int = Config.TOP_K_RESULTS):
        """Search with relevance scores."""
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results
    
    def delete_by_metadata(self, filter_dict: Dict):
        """Delete documents matching metadata filter."""
        client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        collection = client.get_collection(Config.COLLECTION_NAME)
        collection.delete(where=filter_dict)
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        collection = client.get_collection(Config.COLLECTION_NAME)
        return {
            "count": collection.count(),
            "name": collection.name
        }
