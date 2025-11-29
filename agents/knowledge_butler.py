from langchain.agents import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from memory.vector_store import VectorMemory
from typing import Dict, List
from config import Config

class KnowledgeButler:
    """The Knowledge Butler manages AURORA's long-term memory."""
    
    def __init__(self, vector_memory: VectorMemory):
        self.memory = vector_memory
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=Config.REASONING_TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
    
    def search_knowledge(self, query: str) -> str:
        """Search the knowledge base and synthesize an answer."""
        # Retrieve relevant documents
        results = self.memory.search(query, k=Config.TOP_K_RESULTS)
        
        if not results:
            return "I couldn't find any relevant information in my knowledge base."
        
        # Prepare context from results
        context = "\n\n".join([
            f"Source: {doc.metadata.get('filename', 'Unknown')}\n{doc.page_content}"
            for doc in results
        ])
        
        # Generate answer using LLM
        prompt = PromptTemplate(
            input_variables=["context", "query"],
            template="""You are AURORA's Knowledge Butler. Based on the following context from my knowledge base, answer the query.

Context:
{context}

Query: {query}

Provide a clear, concise answer. If the context doesn't fully answer the query, say so and provide what information you can."""
        )
        
        response = self.llm.invoke(
            prompt.format(context=context, query=query)
        )
        
        return response.content
    
    def add_knowledge(self, text: str, metadata: Dict) -> str:
        """Add new knowledge to the memory."""
        doc_id = self.memory.add_text(text, metadata)
        return f"Added knowledge with ID: {doc_id}"
    
    def get_stats(self) -> str:
        """Get knowledge base statistics."""
        stats = self.memory.get_collection_stats()
        return f"Knowledge base contains {stats['count']} chunks of information."
    
    def get_tools(self) -> List[Tool]:
        """Return LangChain tools for this agent."""
        return [
            Tool(
                name="SearchKnowledge",
                func=self.search_knowledge,
                description="Search AURORA's knowledge base for information. Input should be a natural language query."
            ),
            Tool(
                name="GetKnowledgeStats",
                func=self.get_stats,
                description="Get statistics about the knowledge base."
            )
        ]
