from pydantic import BaseModel


class PostCreateRequest(BaseModel):
    title: str
    content: str
    auto_answer: bool = False
    delay_answer: int = 30


class PostUpdateRequest(BaseModel):
    title: str
    content: str
    auto_answer: bool = False
    delay_answer: int = 30
