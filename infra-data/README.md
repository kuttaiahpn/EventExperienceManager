# EventFlow AI - Data Infrastructure

This repository contains the data infrastructure scripts and the scenario engine for the EventFlow AI real-time event orchestration platform.

## Configuration

All configuration is handled via environment variables. Ensure the following match your environment if not using the defaults:
- `GOOGLE_CLOUD_PROJECT` (default: promptwars-virtual2026)
- `VERTEX_AI_LOCATION` (default: us-central1)
- `FIRESTORE_DATABASE` (default: (default))
- `PUBSUB_TOPIC_TELEMETRY` (default: event-telemetry)
- `GCS_DOCS_BUCKET` (default: eventflow-ai-docs-promptwars-virtual2026)
- `EMBEDDING_MODEL` (default: text-embedding-004)

Never hardcode API keys or credentials! Authenticate via Google Cloud Application Default Credentials (ADC).

## Setup Instructions

### 1. Seed Venue State

Reads initial state from `seed_data/*.json` and writes to Firestore. Uses batch writes for efficiency.
```bash
python seed_venue_state.py
```

### 2. Ingest Documents

Downloads PDFs and text files from the GCS bucket, chunks them using LangChain, generates Vertex AI embeddings (`text-embedding-004`), and writes them to the `knowledge_base` collection in Firestore.
```bash
python ingest_documents.py
```

### 3. Deploy Scenario Engine

The scenario engine is an always-on background service publishing lifecycle and telemetry events to the `event-telemetry` Pub/Sub topic. It cycles through 4 realistic event stages every 10 minutes.

**Build and Run Locally with Docker:**
```bash
docker build -t scenario-engine .
docker run -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
  scenario-engine
```

**Deploy to Cloud Run:**
```bash
gcloud run deploy scenario-engine \
  --source . \
  --port 8080 \
  --region us-central1
```

Note: Cloud Run health checks will use the `/health` endpoint exposed on port 8080.
