# EventFlow AI - Frontend

Streamlit frontend for the EventFlow AI real-time event orchestration platform.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   * `GOOGLE_CLOUD_PROJECT=promptwars-virtual2026`
   * `BACKEND_URL=http://localhost:8000`
   * `FIRESTORE_DATABASE=(default)`

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Features
- **Real-time Updates**: Live status of gates, zones, and concessions via Firestore listeners.
- **Dynamic Heatmap**: Interactive zones monitoring density.
- **Chat Interface**: SSE powered conversational AI.
