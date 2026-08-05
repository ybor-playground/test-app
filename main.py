import json
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Hello World CRUD")

DATA_FILE = Path(__file__).parent / "data.json"


class ItemCreate(BaseModel):
    name: str
    description: str = ""


class Item(ItemCreate):
    id: str


def _read_items() -> dict[str, dict]:
    if not DATA_FILE.exists():
        return {}
    return json.loads(DATA_FILE.read_text())


def _write_items(items: dict[str, dict]) -> None:
    DATA_FILE.write_text(json.dumps(items, indent=2))


@app.get("/")
def hello():
    return {"message": "Hello, World!"}


@app.post("/items", response_model=Item, status_code=201)
def create_item(payload: ItemCreate):
    items = _read_items()
    item_id = uuid4().hex[:8]
    items[item_id] = {"id": item_id, **payload.model_dump()}
    _write_items(items)
    return items[item_id]


@app.get("/items", response_model=list[Item])
def list_items():
    return list(_read_items().values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: str):
    items = _read_items()
    if item_id not in items:
        raise HTTPException(404, "Item not found")
    return items[item_id]


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, payload: ItemCreate):
    items = _read_items()
    if item_id not in items:
        raise HTTPException(404, "Item not found")
    items[item_id] = {"id": item_id, **payload.model_dump()}
    _write_items(items)
    return items[item_id]


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str):
    items = _read_items()
    if item_id not in items:
        raise HTTPException(404, "Item not found")
    del items[item_id]
    _write_items(items)
