# Ledger

Ledger is a lightweight expense and settlement manager that helps individuals track personal spending and split costs across shared ledgers. The project ships with a FastAPI backend and a SvelteKit frontend so you can stand up the full stack quickly and grow it over time.

## Repository layout

```
backend/
  app/            # FastAPI application package
  pyproject.toml  # Python project configuration (uv / pip install .)
  tests/          # pytest-based API tests
frontend/
  package.json    # SvelteKit client
  src/            # UI routes, components, and stores
```

## Backend (FastAPI)

### Prerequisites
- Python 3.11+
- `uv` or `pip`

### Installation
```bash
cd backend
uv pip install -r <(uv pip compile pyproject.toml)  # or: pip install -e .[dev]
```

Create a local environment file if you need to override defaults:
```bash
cp .env.example .env
```

### Running the API
```bash
cd backend
uvicorn app.main:app --reload
```
The API boots with a SQLite database (`ledger.db`) by default and auto-creates tables on first run.

### Tests
```bash
cd backend
pytest
```

## Frontend (SvelteKit)

### Prerequisites
- Node.js 18+
- pnpm / npm / yarn

### Installation & development server
```bash
cd frontend
npm install
npm run dev
```
The dev server proxies `/api` requests to `http://localhost:8000`, so start the FastAPI app before using the UI.

## Key Features
- User registration, login, and profile management.
- Ledger creation with membership management.
- Expense capture with configurable splits per participant.
- Balance calculation and settlement tracking.
- Simple SvelteKit dashboard for ledgers, expenses, and settlements.

## API Reference
Once the API is running you can explore interactive docs at `http://localhost:8000/docs`.

## License
Licensed under the Apache 2.0 License. See [LICENSE](LICENSE).
