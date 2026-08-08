from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str = ""


class Item(ItemCreate):
    id: str

    model_config = {"from_attributes": True}
