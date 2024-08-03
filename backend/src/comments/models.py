from datetime import datetime
from database import metadata

from sqlalchemy import (
    Table, Column,
    Integer, String,
    TIMESTAMP, ForeignKey,
    Boolean, MetaData,
)

from auth.models import User
from posts.models import Post


Comment = Table(
    'comment',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('content', String, nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow),
    Column('user_id', ForeignKey(User.id)),
    Column('post_id', ForeignKey(Post.c.id)),
    Column('parent_id', ForeignKey('comment.id'), nullable=True),
    Column('friendly', Boolean, default=False, nullable=False),
)
