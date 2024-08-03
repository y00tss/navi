from datetime import datetime

from sqlalchemy import (
    Table, Column,
    Integer, String,
    TIMESTAMP, ForeignKey,
    Boolean, MetaData,
)

from auth.models import User

metadata = MetaData()

Post = Table(
    'post',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String, nullable=False),
    Column('content', String, nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('updated_at', TIMESTAMP, default=datetime.utcnow),
    Column('user_id', ForeignKey(User.id)),
    Column('friendly', Boolean, default=False, nullable=False),
    Column('auto_answer', Boolean, default=False, nullable=False),
    Column('delay_answer', Integer, default=30, nullable=True),
)
