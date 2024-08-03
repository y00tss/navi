from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    content: str = Field(..., description="Content of the comment")
    post_id: int = Field(..., description="ID of the post the comment is related to")


class CommentReplyRequest(BaseModel):
    content: str = Field(..., description="Content of the reply comment")
    parent_id: int = Field(..., description="ID of the parent comment")


class CommentUpdateRequest(BaseModel):
    content: str = Field(..., description="Updated content of the comment")
