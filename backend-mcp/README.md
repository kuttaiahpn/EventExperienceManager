# EventFlow AI Backend

This is the backend intelligence layer for EventFlow AI. 
It uses LangGraph for agent orchestration, tools via MCP mapping, and Firebase Firestore/PubSub for data syncing and event streaming.

## Setup

1. Copy `.env` to configuration values:
```bash
cp .env.example .env
```
2. Install Python >= 3.11
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run locally:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```
