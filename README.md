# aurora
Advanced Unified Reasoning &amp; Organisation Resource Agent

Overview: A unified personal AI system designed to act as a high level assistant. It integrates multiple agents into one platform to handle knowledge management, research, communication, and coding assistance. Unlike traditional assistants, AURORA builds a **long-term memory and cohesive** of everything you read, write, or code, allowing it to reason over your personal knowledge and provide actionable insights.

Core Agents:
1. Knowledge Butler
- Stores and retrieves your personal knowledge in a vector database
- Supports semantic search and natural-language queries
- Updates memory automatically from other agents

2. Reading Companion
- Ingests PDFs, articles, and notes
- Summarizes and extracts insights
- Feeds structured knowledge into the Knowledge Butler

3. Email Summarizer & Communication Agent
- Summarizes emails and classifies priorities
- Extracts tasks and action items
- Drafts context-aware responses

4. Coding Research Assistant
- Reads codebases and explains functions and workflows
- Suggests improvements, generates documentation, and refactors code
- Connects coding knowledge to the Knowledge Butler

Data Flow:
User Inputs → Preprocessing Pipelines → Vector Memory → LangChain Orchestrator → Agent Responses → Output
