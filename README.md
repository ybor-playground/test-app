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

# Azurite (Azure Blob emulator) — --skipApiVersionCheck avoids
# errors when the SDK's API version is newer than Azurite supports
docker run -d -p 10000:10000 --name azurite mcr.microsoft.com/azure-storage/azurite \
  azurite-blob --blobHost 0.0.0.0 --skipApiVersionCheck

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
# List blobs in the exports container
az storage blob list -c exports \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1" \
  --output table

# Download and print the CSV to stdout (replace the blob name with the one from the dump response)
az storage blob download -c exports -n dumps/items_<timestamp>.csv \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1" \
  --file -
```

You should see a CSV with columns `id`, `name`, `description`, `created_at` and one row per item you created in step 4.

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

## Appendix: Azurite Connection String Explained

The `az storage container create` command used during local setup:

```bash
az storage container create -n exports \
  --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1"
```

### Command breakdown

| Part | What it does |
|------|-------------|
| `az storage container create` | Creates a blob container (like a folder/bucket) in Azure Storage |
| `-n exports` | Names the container `exports` — matches `BLOB_CONTAINER=exports` in `.env` |
| `--connection-string "..."` | Tells the CLI how to connect to the Azurite emulator |

### Connection string breakdown

| Key | Value | Meaning |
|-----|-------|---------|
| `DefaultEndpointsProtocol` | `http` | No TLS — Azurite runs plain HTTP locally |
| `AccountName` | `devstoreaccount1` | Azurite's well-known default account name |
| `AccountKey` | `Eby8vdM02x...` | Azurite's well-known default key (same for everyone, not a secret) |
| `BlobEndpoint` | `http://localhost:10000/devstoreaccount1` | Where the Blob service is running — port 10000 on your machine |

The account name and key are hardcoded defaults that ship with every Azurite instance. They are not secrets — they are publicly documented by Microsoft and identical across all installations. The app code in `app/blob.py` auto-detects localhost URLs and uses these credentials for local dev, while production uses `DefaultAzureCredential` (managed identity, service principal, etc.).

### Common pitfalls

**Port mapping is required.** When starting Azurite via Docker, you must map port 10000 to the host. Without `-p 10000:10000`, the container runs but localhost can't reach it:

```bash
# Wrong — no port mapping, localhost:10000 won't connect
docker run -d --name azurite mcr.microsoft.com/azure-storage/azurite

# Correct — maps host port 10000 to container port 10000
docker run -d -p 10000:10000 --name azurite mcr.microsoft.com/azure-storage/azurite \
  azurite-blob --blobHost 0.0.0.0 --skipApiVersionCheck
```

To verify ports are mapped, check `docker ps` output — you should see `0.0.0.0:10000->10000/tcp`, not just `10000-10002/tcp`.

**If Docker Desktop was used without port mapping**, stop and remove the container, then recreate it:

```bash
docker stop <container_name> && docker rm <container_name>
docker run -d -p 10000:10000 --name azurite mcr.microsoft.com/azure-storage/azurite \
  azurite-blob --blobHost 0.0.0.0 --skipApiVersionCheck
```

**API version mismatch.** If you see `InvalidHeaderValue` / "The API version X is not supported by Azurite", the Python SDK is sending a newer API version than Azurite recognizes. The `--skipApiVersionCheck` flag (included in the Docker commands above) resolves this. If you started Azurite without it, recreate the container with the flag.

**Verify the container was created.** After `az storage container create`, confirm with:

```bash
az storage container list --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://localhost:10000/devstoreaccount1" --output table
```

You should see `exports` listed. If no output appears, the create command failed silently — check that Azurite is running with ports mapped.
