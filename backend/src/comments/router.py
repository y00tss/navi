from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.base_config import current_user
from database import get_async_session
from sqlalchemy import insert, select, update, delete

from comments.models import Comment
from posts.models import Post
from auth.models import User

from worker import reply_to_comment

from services.openai import OpenAI
from services.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True, log_dir='logger',
                filename='comments.log').get_logger()

router = APIRouter()


@router.get("/all")
async def get_all_comments(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all comments
    """
    try:
        posts = await session.execute(select(Comment))
        return posts.mappings().all()
    except Exception as e:
        logger.error(f"Error getting all comments: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/all_friendly")
async def get_all_friendly_comments(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all friendly comments
    """
    try:
        posts = await session.execute(select(Comment).where(
            Comment.c.friendly
        ))
        return posts.mappings().all()
    except Exception as e:
        logger.error(f"Error getting all comments: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/user")
async def get_user_comments(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get comments created by the user
    """
    try:
        posts = await session.execute(select(Comment).where(Post.c.user_id == user.id))
        return posts.mappings().all()
    except Exception as e:
        return {"status": 500, "description": f"{e}"}


@router.get("/user_friendly")
async def get_user_friendly_comments(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all friendly comments created by the user
    """
    try:
        posts = await session.execute(select(Comment).where(
            Post.c.user_id == user.id
        ).where(
            Comment.c.friendly
        ))
        return posts.mappings().all()
    except Exception as e:
        return {"status": 500, "description": f"{e}"}


@router.get("/{post_id}", description="Get all friendly comments related to a post")
async def get_post_comments(
        post_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all comments related to a post
    """
    try:
        post = await session.execute(select(Comment).where(
            Post.c.id == post_id
        ).where(
            Comment.c.friendly
        ))
        return post.mappings().all()
    except Exception as e:
        logger.error(f"Error getting post by id: {e}")
        return {"status": 500, "description": f"{e}"}


@router.post("/")
async def create_comment(
        post_id: int,
        content: str,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Create comment for a post
    """
    try:
        ai = OpenAI()
        result = await ai.check_text(text=content)
        comment = await session.execute(insert(Comment).values(
            content=content,
            user_id=user.id,
            post_id=post_id,
            friendly=result
        ).returning(Comment.c.id))
        comment_id = comment.scalar()

        await session.commit()

        logger.info(f"Comment created for post id: {post_id} by user: {user.username}")

        post_result = await session.execute(select(Post).where(Post.c.id == post_id))
        post = post_result.fetchone()

        await session.close()

        if post.auto_answer and result:
            reply_to_comment.apply_async(
                (comment_id, post_id, post.user_id, post.content, content),
                countdown=post.delay_answer)

        return {
            "status": 201,
            "description": "Comment created successfully" if result
            else "Comment was created but not friendly, change the content"
        }

    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating comment: {e}")
        return {"status": 500, "description": f"{e}"}


@router.post("/reply")  # TODO: check relationship
async def reply_comment(
        parent_id: int,
        content: str,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Reply comment for a comment
    """
    try:
        ai = OpenAI()
        result = await ai.check_text(content)
        parent_comment = await session.execute(select(Comment).where(
            Comment.c.id == parent_id
        ))
        parent = parent_comment.fetchone()
        post = parent[0].post_id

        await session.execute(insert(Comment).values(
            content=content,
            user_id=user.id,
            parent_id=parent_id,
            post_id=post,
            friendly=result
        ))
        await session.commit()
        await session.close()
        logger.info(f"Reply to comment created by user: {user.username}")
        return {
            "status": 201,
            "description": "Comment created successfully" if result
            else "Comment was created but not friendly, change the content"
        }

    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating reply to comment: {e}")
        return {"status": 500, "description": f"{e}"}


@router.patch("/{comment_id}")
async def update_comment(
        comment_id: int,
        content: str,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Update comment
    """
    try:
        ai = OpenAI()
        result = await ai.check_text(content)
        await session.execute(update(Comment).where(Comment.c.id == comment_id).values(
            content=content,
            friendly=result
        ))
        await session.commit()
        logger.info(f"Comment id: {comment_id} updated by user: {user.username}")
        return {
            "status": 201,
            "description": "Comment updated successfully" if result
            else "Comment was updated but not friendly, change the content"
        }
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating comment: {e}")
        return {"status": 500, "description": f"{e}"}


@router.delete("/{comment_id}")
async def delete_comment(
        post_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Delete comment
    """
    try:
        await session.execute(delete(Post).where(Post.c.id == post_id))
        await session.commit()
        logger.info(f"Comment id: {post_id} deleted by user: {user.username}")
        return {"status": 200, "description": "Comment deleted successfully"}
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting comment: {e}")
        return {"status": 500, "description": f"{e}"}
