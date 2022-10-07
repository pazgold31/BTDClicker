from typing import List

from pydantic import BaseModel


class KnowledgeCategory(BaseModel):
    name: str
    entries: List[BaseModel]


class KnowledgeEntry(BaseModel):
    name: str
    purchased: bool
