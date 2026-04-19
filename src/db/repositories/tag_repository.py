import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tag import Tag


def parse_tags(raw: str) -> list[str]:
    tokens = re.findall(r"#?(\w+)", raw)
    seen: dict[str, None] = {}
    for t in tokens:
        key = t.lower()
        if key:
            seen[key] = None
    return list(seen)


class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_many(self, names: list[str]) -> list[Tag]:
        tags: list[Tag] = []
        for name in names:
            result = await self.db.execute(select(Tag).where(Tag.name == name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=name)
                self.db.add(tag)
                await self.db.flush()
            tags.append(tag)
        return tags
