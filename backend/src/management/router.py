from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from auth.base_config import current_user
from database import get_async_session
from sqlalchemy import select, func
from datetime import datetime

from auth.models import User
from comments.models import Comment

from services.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True, log_dir='logger',
                filename='management.log').get_logger()

router = APIRouter()


@router.get("/analysis")
async def get_full_analysis_for_a_period(
        date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),
        date_to: str = Query(..., description="End date in YYYY-MM-DD format"),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get daily breakdown of comment counts between two dates in YYYY-MM-DD format.
    """
    try:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")

        friendly = await session.execute(
            select(func.count()).where(
                Comment.c.created_at >= start_date
            ).where(
                Comment.c.created_at <= end_date
            ).where(
                Comment.c.friendly
            )
        )
        unfriendly = await session.execute(
            select(func.count()).where(
                Comment.c.created_at >= start_date
            ).where(
                Comment.c.created_at <= end_date
            ).where(
                ~Comment.c.friendly
            )
        )

        friendly_count = friendly.scalar()
        unfriendly_count = unfriendly.scalar()

        return {"status": 200, "description": "Success",
                "data": {"friendly": friendly_count, "unfriendly": unfriendly_count}}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/toxic_user")
async def get_most_toxic_user(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get user with the most unfriendly comments
    """
    try:
        stmt = select(Comment.c.user_id).where(
            ~Comment.c.friendly
        ).group_by(Comment.c.user_id).order_by(func.count().desc()).limit(1)
        result = await session.execute(stmt)
        user_id = result.scalar()

        return {"status": 200, "description": "Success", "user_id": user_id}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/count_friendly")
async def get_friendly_comments_count(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get count of friendly comments
    """
    try:
        stmt = select(func.count()).where(
            Comment.c.friendly
        )
        result = await session.execute(stmt)
        count = result.scalar()

        return {"status": 200, "description": "Success", "count": count}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/count_unfriendly")
async def get_unfriendly_comments_count(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get count of unfriendly comments
    """
    try:
        stmt = select(func.count()).where(
            Comment.c.friendly
        )
        result = await session.execute(stmt)
        count = result.scalar()

        return {"status": 200, "description": "Success", "count": count}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": 500, "description": f"{e}"}


@router.get("/user_activity")
async def get_user_activity(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Get user activity by user ID: count of friendly and unfriendly comments
    """
    try:
        stmt_friendly = select(func.count()).where(
            Comment.c.user_id == user_id
        ).where(
            Comment.c.friendly
        )
        stmt_unfriendly = select(func.count()).where(
            Comment.c.user_id == user_id
        ).where(
            Comment.c.friendly
        )

        result_friendly = await session.execute(stmt_friendly)
        result_unfriendly = await session.execute(stmt_unfriendly)

        count_friendly = result_friendly.scalar()
        count_unfriendly = result_unfriendly.scalar()

        return {"status": 200, "description": "Success",
                "data": {"friendly": count_friendly, "unfriendly": count_unfriendly}}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": 500, "description": f"{e}"}
