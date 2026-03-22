# Multi-Agent Support Desk

This project is a multi-agent support desk system powered by FastAPI, LangGraph, and Qdrant. It features a conversational support agent capable of Retrieval-Augmented Generation (RAG) and automated ticket creation, alongside a backend triage agent that automatically classifies, categorizes, and updates open tickets.

## Architecture

The system utilizes two distinct AI agents orchestrated via **LangGraph**:
1. **Support Agent (Customer-Facing)**: Handles user queries, searches the Knowledge Base (Qdrant) for FAQ answers, citing sources. If an issue is reported, it naturally guides the user through providing necessary information, escalates by creating a ticket in the MySQL database, and maintains session memory.
2. **Triage Agent (Ops-Facing)**: Runs via a background/internal trigger to process the queue of `OPEN` tickets. It strictly classifies the category, severity, priority, and owner, leaving internal notes and updating the status to `IN_PROGRESS`, `WAITING_FOR_USER`, or `RESOLVED`.

**Tech Stack**:
* **Web Framework**: FastAPI
* **Agent Orchestration**: LangGraph / LangChain
* **LLM & Embeddings**: OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)
* **Vector Store**: Qdrant
* **Database**: MySQL

## Setup Instructions

1. **Create and activate a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate

2. **Install dependencies**:
```powershell
pip install -r requirements.txt

```
3. **Configure Environment Variables**:
Create a `.env` file in the root directory and add your keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=mysql+aiomysql://support_user:<password>@localhost:3306/support_desk

```

## Run Instructions

1. **Start the FastAPI server**:
```powershell
uvicorn app.main:app --reload

```


*The server will start on `http://127.0.0.1:8000`.*
*During startup, the SQLite database will be initialized, and the Knowledge Base (Markdown files in `/kb`) will automatically be chunked, embedded, and indexed into Qdrant.*
2. **Access API Documentation**:
Navigate to `http://127.0.0.1:8000/docs` to interact with the endpoints via the Swagger UI.

