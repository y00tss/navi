from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session

from comments.models import Comment


async def create_comment(
        comment_id: int,
        post_id: int,
        author_id: int,
        answer: str,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    the function implements the creation of a comment in the database
    """
    try:
        result = await session.execute(
            insert(Comment).values(
                content=answer,
                user_id=author_id,
                post_id=post_id,
                friendly=True,
                parent_id=comment_id
            ).returning(Comment.c.id)
        )
        new_comment_id = result.scalar()
        await session.commit()
        return new_comment_id
    except Exception as e:
        await session.rollback()
        raise e
