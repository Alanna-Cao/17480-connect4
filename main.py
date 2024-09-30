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
The Connect 4 Game Hub API allows users to create, play, and manage multiple Connect 4 games programmatically. 
It supports three game modes: two human players, one human versus a computer, and two computer players. 

### Class and Instance Representation
The primary class representing the API is `Game`. An instance of the `Game` class represents a single game of Connect 4, encapsulating the game state, players, and the current board configuration. This class is used to manage the lifecycle of a game, including creating the game, making moves, checking win conditions, and handling game resets.

### Structure of Methods
The `Game` class provides several key methods organized into logical groupings:
- **Game Management Methods**:
    - `create_game()`: Initializes a new game instance.
    - `restart_game()`: Resets the game board while preserving player information.
    - `quit_game()`: Terminates the game and removes it from the active games list.

- **Gameplay Methods**:
    - `make_move(player_id, column)`: Updates the board based on the player's move.
    - `get_game_state()`: Returns the current state of the game, including the board and player information.

### Underlying Data Structures
The API relies on the following basic data structures to support its functionality:
- **Game Board Representation**: The board is structured as a grid, where each cell's state (None or occupied by 1 specific player) is tracked to determine the game's progress. The specific implementation details (like using integers or symbols) may vary, but the grid layout remains consistent across all game instances.
- **Player Information**: Players are identified by unique identifiers, specifically `p1` for Player 1 and `p2` for Player 2. Each player’s identifier is associated with attributes such as their name and current score, allowing the API to manage interactions and enforce turn-taking effectively.
- **Game State Management**: The API maintains a registry of active games, enabling efficient access and modification of ongoing game sessions.

### State Transitions
The API follows a structured sequence of method calls to manage the game state effectively:

- **Create a Game**: Call the `create_game` endpoint to initialize a game. This sets up the game state and all relevant game logic (number of players, names, types, etc.). Player 1 (p1) always starts the game.
- **Make Moves**: Players can make moves by calling the `make_move` endpoint. Each move updates the game board. Players must take turns making moves; if it's not the correct player's turn, an error will be returned.
- **Game Validations**: Before a move is processed, the API checks:
  - If it is the correct player's turn.
  - Whether the specified column is within bounds.
  - If the column is not already full. If any of these checks fail, an error response is returned, indicating the reason for the invalid move.
- **Viewing State**: You can view the current game state by calling the `get_game` endpoint, which returns the board layout and player information.
- **Restarting a Game**: If players want to reset the board without changing player information, they can use the `restart_game` endpoint, which resets the game state while retaining players.
- **Quitting a Game**: Use the `quit_game` endpoint to remove a game from the active games list, effectively terminating the game session.

### Data Persistence
The Connect 4 Game Hub API stores game data in memory, meaning that games only persist for the duration of the current server session. 
Once the server is restarted or crashes, all games and their states will be lost. 
This approach is suitable for environments where games do not need to be persisted long-term. If persistence across sessions or server restarts is required, you may need to modify the implementation to store game data in a more durable storage solution, such as a database.

### Thread-safety
This API does not impose any thread-safety requirements. Implementations should handle any necessary synchronization if the game is to be used in a concurrent environment. Mutable game state, such as player moves and board updates, must ensure consistent state management and retrieval to prevent race conditions or invalid game states.

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

For more details on available endpoints and their usage, refer to the API endpoint documentation as well as their sample response objects below.
"""

# FastAPI application setup with metadata
app = FastAPI(
    title="Connect 4 Game Hub API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/", response_model=dict, tags=["Root"])
def read_root():
    return {"message": "Welcome to the Connect 4 Game Hub API! For more information, visit /docs."}

app.include_router(router)
