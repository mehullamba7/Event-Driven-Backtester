from pydantic import BaseModel, Field
from typing import Literal, Optional

Timeframe = Literal["1m","5m","1h","1d"]

class PageMeta(BaseModel):
    next_page_token: Optional[str] = Field(default=None)