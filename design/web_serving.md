# web_serving — Design

## Purpose

Local web interface for exploring the knowledge graph visually. FastAPI backend serving a Cytoscape.js frontend.

---

## Dependencies

- `note_modeling` — value objects
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

- Static files: `index.html`, `app.js`, `styles.css` served from `static/`
- Force-directed layout
- Click node → side panel shows note content
- Filter controls: tag dropdown, relationship type dropdown, search box
- Edge labels show relationship type
- Refresh button — reloads graph data from server without full page reload

### Cytoscape.js Payload

`build_cytoscape_payload(graph: Graph, tag: str | None, link_type: str | None) -> dict` — lives in `web_serving`, converts `Graph` into Cytoscape.js JSON format, applies tag and relationship type filters if provided.

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

## Frontend Delivery

Static files served from a `static/` directory mounted in FastAPI:

```
web_serving/
└── static/
    ├── index.html
    ├── app.js
    └── styles.css
```

## Phase 3 — Live Graph Updates

WebSocket + file watching for automatic graph updates when notes change on disk.

- `watchfiles` monitors the `notes/` directory
- On change, server rebuilds the graph and pushes update via WebSocket
- Frontend re-renders Cytoscape.js on receipt

Phase 1 ships with a manual "Refresh" button instead. Phase 3 is additive — no rework of existing REST API.

---

## Build Order

Built last. Tests use FastAPI `TestClient` for API endpoints. Frontend tested manually.
