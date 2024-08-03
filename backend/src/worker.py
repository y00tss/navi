import os
import asyncio
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

from comments.utils import create_comment

from services.openai import OpenAI
from services.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True, log_dir='logger/',
                filename='worker.log').get_logger()

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")  # noqa

# Database
engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery.task(name="create_task")
def reply_to_comment(
        comment_id: int,
        post_id: int,
        author_id: int,
        content: str,  # post content
        comment: str  # comment content
):
    """Celery task to reply to a comment with an AI-generated response."""
    async def get_reply():
        async with async_session_maker() as session:
            ai = OpenAI()
            answer = await ai.reply_to_comment(content, comment)
            try:
                new_comment_id = await create_comment(
                    comment_id, post_id, author_id, answer, session
                )
                logger.info(f"Successfully created comment with ID: {new_comment_id}")
            except Exception as e:
                logger.error(f"Error inserting comment: {e}")

    asyncio.run(get_reply())
