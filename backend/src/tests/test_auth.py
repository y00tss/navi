from tests.conftest import client, override_get_async_session
from database import get_async_session
from sqlalchemy import select, insert
from auth.models import role


async def test_add_role():
    async with override_get_async_session() as session:
        stmt = insert(role).values(id=1, name="admin", permissions=["admin"])
        await session.execute(stmt)
        await session.commit()
        query = select(role)
        result = await session.execute(query)
        roles = result.scalars().all()
        assert result.all() == [(1, "admin", ["admin"])]

