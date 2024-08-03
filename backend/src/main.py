import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as router_auth
from posts.router import router as router_posts
from comments.router import router as router_comments
from management.router import router as router_management


app = FastAPI(
    title="Navi",
    description="API for the StarNavi company"
)

current_dir = os.path.join(os.path.dirname(__file__))

# Authorizations
app.include_router(
    router_auth,
    prefix="/auth",
    tags=["Auth"],
)

# Posts
app.include_router(
    router_posts,
    prefix="/posts",
    tags=["Posts"],
)

# Comments
app.include_router(
    router_comments,
    prefix="/comments",
    tags=["Comments"],
)

# Management
app.include_router(
    router_management,
    prefix="/management",
    tags=["Management"],
)

origins = [
    'http://localhost:3000',
]

# Настройки CORS и конфигурации
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"],
)
