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
The Connect 4 API allows users to create, play, and manage Connect 4 games programmatically. 
It supports three game modes: two human players, one human versus a computer, and two computer players. 
To interact with the API, you first need to create a game by specifying the number of human players (zero, one, or two) 
and, if applicable, providing names for the human players. Once a game is created, you can perform various operations 
such as listing all games, viewing the state of a specific game, restarting a game while keeping the player information intact, or quitting a game to remove it from the system.

When playing a game, players can make moves by dropping pieces into specified columns. 
The API ensures that moves are valid by checking if it is the correct player's turn, 
whether the column is within bounds, and whether the column is full. If a move is invalid, 
an error response will be returned. For games involving the computer, you can use the 
endpoint for calculating the next move, which will return a random valid move for the computer to make.

It is important to follow the proper sequence of API calls. A game must be created before making moves or viewing its state. 
Moves can only be made if it is the correct player's turn, and the game must not have been won or ended in a draw. 
If you want to start a new round but keep the same players, you can restart the game. If the game is no longer needed, 
you can quit the game to remove it from the list of games.

### Data Persistence
The Connect 4 API stores game data in memory, meaning that games only persist for the duration of the current server session. 
Once the server is restarted or crashes, all games and their states will be lost. 
This approach is suitable for environments where games do not need to be persisted long-term.
If persistence across sessions or server restarts is required, you may need to modify the implementation to store 
game data in a more durable storage solution, such as a database.


### Thread-safety
This API does not impose any thread-safety requirements. Implementations should handle any necessary synchronization 
if the game is to be used in a concurrent environment. Mutable game state, such as player moves and board updates, 
must ensure consistent state management and retrieval to prevent race conditions or invalid game states.

### Example Usage
- **Creating a Game**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/games?player1_name=Alice&player2_name=Bob&num_human_players=2"
    ```
    This will create a game with two human players named Alice and Bob.

- **Making a Move**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/games/{game_id}/moves?player_id=p1&column=3"
    ```
    Player 1 drops a piece into column 3.

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
