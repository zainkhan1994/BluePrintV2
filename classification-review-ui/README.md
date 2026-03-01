# Classification Review UI

Small standalone static app that reads from the running backend at http://localhost:8100 and
lets you review and approve classifications marked `needs_review`.

Key properties:
- Runs independently of the backend.
- Does not modify backend code, schema, or endpoints.
- Uses the existing API: `GET /classification/needs-review`, `GET /items/{id}`, `GET /items/{id}/classification`, and `POST /items/{id}/classification/override`.

How to run:

1. Ensure the backend is running at http://localhost:8100.
2. From the repo root open the UI (simple options):

  - Open the file directly in your browser:

    file:///<repo-root>/classification-review-ui/index.html

  - Or serve the folder with a simple static server (recommended):

    python -m http.server 8085 --directory classification-review-ui

    Then open: http://localhost:8085

Notes:
- Deleting this `classification-review-ui/` directory has no effect on the backend.
- The UI is intentionally tiny and read-only (except it calls the classification override endpoint to approve items).
