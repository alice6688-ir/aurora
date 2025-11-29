from memory.vector_store import VectorMemory
from agents.knowledge_butler import KnowledgeButler
from agents.reading_companion import ReadingCompanion
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import Config

class AURORA:
    """Main orchestrator for the AURORA system."""
    
    def __init__(self):
        # Initialize memory
        self.memory = VectorMemory()
        
        # Initialize agents
        self.knowledge_butler = KnowledgeButler(self.memory)
        self.reading_companion = ReadingCompanion(self.memory)
        
        # Initialize LLM for orchestration
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=Config.REASONING_TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Set up agent executor
        self._setup_agent()
    
    def _setup_agent(self):
        """Set up the main agent with all tools."""
        # Collect tools from all agents
        tools = self.knowledge_butler.get_tools()
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are AURORA (Advanced Unified Reasoning & Organisation Resource Agent), 
a personal AI assistant that helps manage knowledge, documents, and information.

You have access to a knowledge base where information is stored and can be retrieved.
When users ask questions, search the knowledge base first. When they want to add documents,
use the reading tools.

Be helpful, concise, and intelligent in your responses."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )
    
    def chat(self, message: str) -> str:
        """Main chat interface."""
        response = self.agent_executor.invoke({"input": message})
        return response["output"]
    
    def ingest_document(self, file_path: str) -> str:
        """Directly ingest a document."""
        return self.reading_companion.ingest_document(file_path)
    
    def summarize_document(self, file_path: str) -> str:
        """Directly summarize a document."""
        return self.reading_companion.summarize_document(file_path)


if __name__ == "__main__":
    print("Initializing AURORA...")
    aurora = AURORA()
    print("AURORA is ready!\n")
    
    print("=== Example: Chat with AURORA ===")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        response = aurora.chat(user_input)
        print(f"\nAURORA: {response}\n")
