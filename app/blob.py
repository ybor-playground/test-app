from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from app.config import settings

_AZURITE_ACCOUNT_KEY = (
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq"
    "/K1SZFPTOtr/KBHBeksoGMGw=="
)


def _is_local_emulator(url: str) -> bool:
    return "localhost" in url or "127.0.0.1" in url


if _is_local_emulator(settings.blob_account_url):
    blob_service = BlobServiceClient(
        account_url=settings.blob_account_url,
        credential=_AZURITE_ACCOUNT_KEY,
    )
else:
    blob_service = BlobServiceClient(
        account_url=settings.blob_account_url,
        credential=DefaultAzureCredential(),
    )


def upload_blob(blob_name: str, data: str) -> str:
    blob_client = blob_service.get_blob_client(
        container=settings.blob_container,
        blob=f"{settings.blob_prefix}{blob_name}",
    )
    blob_client.upload_blob(data, overwrite=True)
    return blob_client.url
