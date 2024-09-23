from fastapi import FastAPI
from app.api.routes import router

# API Tags metadata
tags_metadata = [
    {
        "name": "Game Management",
        "description": "Operations for managing Connect 4 games: create, view, restart, quit."
    },
    {
        "name": "Gameplay",
        "description": "Operations for making moves and calculating the next move."
    },
]

description = """
The Connect 4 API allows users to create and play the classic Connect 4 game.

- **Game creation** for two human players, a human vs. a computer, or two computers.
- **Gameplay** for making moves, checking the game state, and calculating the computer's next move.
- **Game state management** including restarting and quitting a game.
"""

# FastAPI application setup with metadata
app = FastAPI(
    title="Connect 4 API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Connect 4 API! For more information, visit /docs."}

app.include_router(router)

# POST /games to create a new game
# GET /games/{game_id} to get the current state of a game
# POST /games/{game_id}/move to make a move in a game