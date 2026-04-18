# Integration Testing Suite: EventFlow AI

This document outlines the cross-component validation performed to ensure the integrity of the EventFlow AI orchestration engine.

## 📡 1. Telemetry Pipeline Validation
- **Path:** `Simulation Sandbox -> Pub/Sub -> Subscriber Worker -> Firestore`
- **Validation:** Verified that triggering a "Vendor Slowdown" in the UI sends a valid JSON payload to the `event-telemetry` topic, which is processed by the background worker to update the `is_active` status of the targeted concession in Firestore.
- **Latency Check:** Observed sub-second synchronization between Simulation trigger and Dashboard indicator updates.

## 🤖 2. Agentic Tool-Chain Integration
- **Path:** `User Chat -> LangGraph Orchestrator -> Tool Calling -> Firestore`
- **Validation:** 
  - Verified that the `Manager Agent` successfully identifies when to call `lc_update_venue_state`.
  - Confirmed that the `Technical ID Resolver` correctly maps natural language strings (e.g., "Gate D") to canonical Firestore IDs (`Gate_D`).

## 🔎 3. Vector Retrieval & RAG Accuracy
- **Path:** `User Query -> Vertex AI Embedding (004) -> Firestore Vector Search`
- **Validation:**
  - Verified that queries regarding "Clear Bag Policy" and "Medical Support" return top-5 relevant chunks from the ingested PDF.
  - Confirmed that "Squashed Text" issues were resolved by moving to a layout-aware PDF extraction engine (PyMuPDF).

## 🚢 4. Deployment Readiness
- **Target:** Google Cloud Run
- **Validation:** 
  - Verified `Dockerfile` multi-stage build compatibility.
  - Confirmed that the Frontend service can communicate with the Backend service via the `BACKEND_URL` environment variable.
