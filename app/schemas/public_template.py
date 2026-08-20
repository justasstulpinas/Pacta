from pydantic import BaseModel, ConfigDict
from typing import List


class PublicTemplateOut(BaseModel):
    name: str
    description: str | None
    content: str
    fields: List[str]
    logo_image: str | None = None
    logo_x: float = 5.0
    logo_y: float = 5.0
    logo_w: float = 15.0

    model_config = ConfigDict(from_attributes=True)

