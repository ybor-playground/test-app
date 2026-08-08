import csv
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import ItemModel
from app.schemas import Item, ItemCreate

router = APIRouter()


@router.get("/")
async def hello():
    return {"message": "Hello, World!"}


@router.post("/items", response_model=Item, status_code=201)
async def create_item(payload: ItemCreate, db: AsyncSession = Depends(get_db)):
    item_id = uuid4().hex[:8]
    item = ItemModel(id=item_id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/items", response_model=list[Item])
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemModel))
    return result.scalars().all()


@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemModel, item_id)
    if item is None:
        raise HTTPException(404, "Item not found")
    return item


@router.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: str, payload: ItemCreate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(ItemModel, item_id)
    if item is None:
        raise HTTPException(404, "Item not found")
    item.name = payload.name
    item.description = payload.description
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemModel, item_id)
    if item is None:
        raise HTTPException(404, "Item not found")
    await db.delete(item)
    await db.commit()


@router.post("/items/dump")
async def dump_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemModel))
    items = result.scalars().all()

    dump_dir = Path(settings.blob_store_path)
    dump_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"items_{timestamp}.csv"
    filepath = dump_dir / filename

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "description"])
        for item in items:
            writer.writerow([item.id, item.name, item.description])

    return {"file": str(filepath), "count": len(items)}
