# test-app

Hello World CRUD app built with FastAPI, PostgreSQL, and Azure Blob Storage.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Hello World |
| `GET` | `/healthz` | Liveness probe |
| `GET` | `/readyz` | Readiness probe (checks DB) |
| `POST` | `/items` | Create an item |
| `GET` | `/items` | List all items |
| `GET` | `/items/{id}` | Get an item |
| `PUT` | `/items/{id}` | Update an item |
| `DELETE` | `/items/{id}` | Delete an item |
| `POST` | `/items/dump` | Dump all items as CSV to Azure Blob Storage |

## Local Testing

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker (for Azurite)
- Azure CLI (`az`) for blob verification

### 1. Start PostgreSQL and Azurite

```bash
# PostgreSQL (if not already running)
brew services start postgresql@16
createdb test_app

# Azurite (Azure Blob emulator)
docker run -d -p 10000:10000 --name azurite mcr.microsoft.com/azure-storage/azurite

# Create the blob container in Azurite
az storage container create -n exports \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1"
```

### 2. Install and configure

```bash
python -m venv .venv
source .venv/bin/activate
cp .env.example .env    # edit if your PostgreSQL uses different credentials
pip install -e .
```

### 3. Start the app

```bash
uvicorn app.main:app --reload
```

### 4. Test the endpoints

```bash
# Health probes
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz

# Hello
curl http://localhost:8000/

# Create items
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "description": "Test widget"}'

curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Gadget", "description": "Another item"}'

# List all items
curl http://localhost:8000/items

# Get a single item (replace <id> with an actual id)
curl http://localhost:8000/items/<id>

# Update an item
curl -X PUT http://localhost:8000/items/<id> \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Widget", "description": "Changed"}'

# Delete an item
curl -X DELETE http://localhost:8000/items/<id>

# Dump all items to Azure Blob (Azurite)
curl -X POST http://localhost:8000/items/dump
```

### 5. Verify the blob was written

```bash
az storage blob list -c exports \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1" \
  --output table
```

### Swagger UI

Interactive API docs are available at `http://localhost:8000/docs`.

## Configuration

All settings are loaded from environment variables (or a `.env` file). See `.env.example` for the full list.

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `BLOB_ACCOUNT_URL` | Yes | Azure Blob Storage account URL |
| `BLOB_CONTAINER` | Yes | Blob container name |
| `BLOB_PREFIX` | No | Key prefix for blobs (default: `dumps/`) |
| `DB_POOL_SIZE` | No | SQLAlchemy connection pool size (default: `5`) |
| `DB_MAX_OVERFLOW` | No | Max overflow connections (default: `10`) |
