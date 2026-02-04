# Copilot Instructions for Backend Codebase

## Overview
This is a Python backend project organized for clarity and modularity. The main application logic resides in the `app/` directory, which is subdivided into API and database layers. The project is intended for containerized deployment (see `dockerfile`).

## Architecture
- **app/main.py**: Entry point for the backend service. Orchestrates API and DB modules.
- **app/api/**: Contains API logic (e.g., `apollo.py`). Follows a modular approach for endpoints and handlers.
- **app/db/**: Handles database connections and schema definitions. `connection.py` manages DB connectivity; `schema.py` defines models or schema logic.
- **pyproject.toml**: Manages Python dependencies and build configuration. Use this for adding/removing packages.
- **dockerfile**: Defines container build steps. The app is designed to run in Docker for consistency.

## Developer Workflows
- **Run Locally**: Start with `python app/main.py` from the project root.
- **Build Container**: Use `docker build -t backend .` and run with `docker run -p 8000:8000 backend`.
- **Dependencies**: Add packages to `pyproject.toml` and run `pip install -r requirements.txt` if requirements are generated.
- **Debugging**: Debug entry point in `app/main.py`. API and DB modules are imported and can be traced from there.

## Patterns & Conventions
- **Modular Structure**: API and DB logic are separated for maintainability.
- **Explicit Imports**: Avoid wildcard imports; use explicit module references.
- **Configuration**: Centralize config in `pyproject.toml` and environment variables (if used).
- **No tests detected**: Add tests in `app/tests/` if expanding. Follow the same modular pattern.

## Integration Points
- **Database**: Connection logic in `app/db/connection.py`. Schema in `app/db/schema.py`.
- **API**: Endpoints in `app/api/`. Extend by adding new modules per endpoint.
- **Containerization**: All deployment logic is in `dockerfile`.

## Examples
- To add a new API endpoint: Create a new file in `app/api/`, define the handler, and import it in `main.py`.
- To add a new DB model: Update `app/db/schema.py` and ensure connection logic in `connection.py` supports it.

## Key Files
- `app/main.py`: Application entry and orchestration
- `app/api/`: API endpoints and logic
- `app/db/`: Database connection and schema
- `dockerfile`: Container build and run instructions
- `pyproject.toml`: Dependency and build config

---
_If any section is unclear or missing, please provide feedback for improvement._
