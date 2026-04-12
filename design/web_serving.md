# web_serving — Design

## Purpose

Local web interface for exploring the knowledge graph visually. FastAPI backend serving a Cytoscape.js frontend.

---

## Dependencies

- `note_modeling` — value objects
- `rdf_projection` — `RDFlibGraphQuery` for SPARQL (phase 2)
- `service.py` — orchestration layer
- `fastapi` — web framework
- `uvicorn` — ASGI server

---

## Phase 1 — Graph Visualisation

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/graph` | Full graph as Cytoscape.js JSON (nodes + edges) |
| `GET` | `/api/graph?tag=<tag>` | Filtered by tag |
| `GET` | `/api/graph?type=<type>` | Filtered by relationship type |
| `GET` | `/api/notes/{id}` | Single note metadata + body |
| `GET` | `/api/search?q=<query>` | Search notes by title/content |
| `GET` | `/` | Serve the frontend HTML |

### Frontend

- Single HTML page with embedded Cytoscape.js
- Force-directed layout
- Click node → side panel shows note content
- Filter controls: tag dropdown, relationship type dropdown, search box
- Edge labels show relationship type

### Cytoscape.js Graph Format

```json
{
  "nodes": [
    { "data": { "id": "20260409221400", "label": "My Note Title", "tags": ["rdf"] } }
  ],
  "edges": [
    { "data": { "source": "20260409221400", "target": "20260101120000", "label": "related" } }
  ]
}
```

---

## Phase 2 — SPARQL Interface

- `POST /api/sparql` — accepts SPARQL query string, returns results as JSON table
- Frontend: text input area, execute button, results table below the graph

---

## Open Questions

- Serve frontend as static files or inline in a single HTML template?
- Whether to use WebSocket for live graph updates

---

## Build Order

Built last. Tests use FastAPI `TestClient` for API endpoints. Frontend tested manually.
