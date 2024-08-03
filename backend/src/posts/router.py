from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from auth.base_config import current_user
from database import get_async_session
from sqlalchemy import insert, select, update, delete

from auth.models import User
from posts.models import Post

from services.openai import OpenAI
from services.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True, log_dir='logger',
                filename='posts.log').get_logger()

router = APIRouter()


@router.get("/all")
async def get_all_posts(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all posts
    """
    try:
        posts = await session.execute(select(Post))

        return posts.mappings().all()
    except Exception as e:
        logger.error(f"Error getting all posts: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/all_friendly")
async def get_all_friendly_posts(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all only friendly posts
    """
    try:
        posts = await session.execute(select(Post).where(
            Post.c.friendly
        ))

        return posts.mappings().all()
    except Exception as e:
        logger.error(f"Error getting all posts: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/user")
async def get_posts_by_user(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get post by user
    """
    try:
        posts = await session.execute(select(Post).where(Post.c.user_id == user.id))
        return posts.mappings().all()
    except Exception as e:
        logger.error(f"Error getting posts by user: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/user_friendly")
async def get_friendly_posts_by_user(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get all only friendly posts by user
    """
    try:
        posts = await session.execute(select(Post).where(
            Post.c.user_id == user.id
        ).where(
            Post.c.friendly
        ))
        return posts.mappings().all()
    except Exception as e:
        logger.error(f"Error getting posts by user: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/{post_id}")
async def get_post_by_id(
        post_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get post by id
    """
    try:
        post = await session.execute(select(Post).where(Post.c.id == post_id))
        return post.mappings().all()[0]
    except Exception as e:
        logger.error(f"Error getting post by id: {e}")
        return {"status": 500, "description": f"{e}"}


@router.post("/")
async def create_post(
        title: str,
        content: str,
        auto_answer: bool = Query(False, description="Auto_answer"),
        delay_answer: int = Query(30, description="Delay_answer in seconds"),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Create post
    """
    try:
        ai = OpenAI()
        result = await ai.check_text(content)
        await session.execute(insert(Post).values(
            title=title,
            content=content,
            user_id=user.id,
            auto_answer=auto_answer,
            delay_answer=delay_answer,
            friendly=result
        ))
        await session.commit()
        await session.close()
        logger.info(f"Post created by user: {user.username}")
        return {
            "status": 201,
            "description": "Post created successfully" if result
            else "Post was created but it is not friendly, change the content"
        }

    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating post: {e}")
        return {"status": 500, "description": f"{e}"}


@router.patch("/{post_id}")
async def update_post(
        post_id: int,
        title: str,
        content: str,
        auto_answer: bool = Query(False, description="Auto_answer"),
        delay_answer: int = Query(30, description="Delay_answer in seconds"),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Update post
    """
    try:
        ai = OpenAI()
        result = await ai.check_text(content)
        await session.execute(update(Post).where(Post.c.id == post_id).values(
            title=title,
            content=content,
            auto_answer=auto_answer,
            delay_answer=delay_answer,
            friendly=result
        ))
        await session.commit()
        logger.info(f"Post updated by user: {user.username}")
        return {
            "status": 201,
            "description": "Post changed successfully" if result
            else "Post was updated but it is not friendly, change the content"
        }
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating post: {e}")
        return {"status": 500, "description": f"{e}"}


@router.delete("/{post_id}")
async def delete_post(
        post_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Delete post
    """
    try:
        await session.execute(delete(Post).where(Post.c.id == post_id))
        await session.commit()
        logger.info(f"Post deleted by user: {user.username}")
        return {"status": 200, "description": "Post deleted successfully"}
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting post: {e}")
        return {"status": 500, "description": f"{e}"}
