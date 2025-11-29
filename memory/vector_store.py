from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from typing import List, Dict, Optional
import pickle
import os
from config import Config

class VectorMemory:
    """Manages the vector database for AURORA's long-term memory."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )

        # Try to load existing vectorstore
        if os.path.exists(Config.CHROMA_DB_PATH):
            try:
                self.vectorstore = FAISS.load_local(
                    Config.CHROMA_DB_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except:
                self.vectorstore = FAISS.from_texts(
                    ["Initial document"],
                    self.embeddings
                )
        else:
            # Create new vectorstore
            self.vectorstore = FAISS.from_texts(
                ["Initial document"],
                self.embeddings
            )

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        self.vectorstore.add_documents(documents)
        self._save()
        return [str(i) for i in range(len(documents))]

    def add_text(self, text: str, metadata: Dict) -> str:
        """Add a single text with metadata."""
        doc = Document(page_content=text, metadata=metadata)
        self.vectorstore.add_documents([doc])
        self._save()
        return "added"

    def search(self, query: str, k: int = Config.TOP_K_RESULTS,
               filter_dict: Optional[Dict] = None) -> List[Document]:
        """Semantic search over stored documents."""
        results = self.vectorstore.similarity_search(query, k=k)
        return results

    def search_with_score(self, query: str, k: int = Config.TOP_K_RESULTS):
        """Search with relevance scores."""
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results

    def delete_by_metadata(self, filter_dict: Dict):
        """Delete documents matching metadata filter."""
        # FAISS doesn't support deletion easily
        pass

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        return {
            "count": self.vectorstore.index.ntotal,
            "name": "aurora_faiss_memory"
        }

    def _save(self):
        """Save vectorstore to disk."""
        os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)
        self.vectorstore.save_local(Config.CHROMA_DB_PATH)
