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

- **Game creation**: Create a game for two human players, a human vs. a computer, or two computers.
- **Gameplay**: Make moves, check the game state, and calculate the computer's next move.
- **Game state management**: Restart and quit games.

### Example Usage
To create a new game, send a POST request to `/games` with player names and the number of human players. For instance:

```bash
curl -X POST "http://127.0.0.1:8000/games?player1_name=Alice&player2_name=Bob&num_human_players=2
```

This will create a game with two human players named Alice and Bob.
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

@app.get("/", response_model=dict, tags=["Root"])
def read_root():
    return {"message": "Welcome to the Connect 4 API! For more information, visit /docs."}

app.include_router(router)
