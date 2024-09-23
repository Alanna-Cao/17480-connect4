from fastapi import APIRouter, HTTPException, Query
from app.models.models import GameLogic, Game, NumHumanPlayers, ErrorResponse
from uuid import uuid4
from typing import List

router = APIRouter()
games = {}

# Game Management Endpoints
@router.get(
    "/games", 
    response_model=List[Game], 
    tags=["Game Management"],
    summary="List all games",
    responses={
        200: {
            "description": "A list of all games, including game ID, players, board state, and status for each game.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "game_id_1",
                            "players": {
                                "p1": {"name": "Alice", "type": "human"},
                                "p2": {"name": "Bob", "type": "human"}
                            },
                            "board": [[None, None, None, None, None, None, None] for _ in range(6)],
                            "status": "in-progress"
                        }
                    ]
                }
            }
        }
    })
def list_games() -> List[Game]:
    """
    Get a list of all games.
    """
    return [game.to_dict() for game in games.values()]

@router.post(
    "/games",
    response_model=Game,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid number of human players or missing player names"}
    },
    tags=["Game Management"],
    summary="Create a new game",
    description=(
        "Creates a new game with zero, one, or two human players. If a player name is not provided, the game will automatically initialize a computer player. "
        "If no player names are specified, the game will be created with two computer players."
    )
)
def create_game(
    player1_name: str = Query(None, description="Name of player 1 (required for human players)"),
    player2_name: str = Query(None, description="Name of player 2 (required for two human players)"),
    num_human_players: NumHumanPlayers = Query(..., description="Number of human players (0, 1, or 2)")
) -> Game:
    """
    Creates a new game with zero, one, or two human players.

    If a player name is not provided, the game will automatically initialize a computer player. If no player names are specified, the game will be created with two computer players.
    """
    if num_human_players not in NumHumanPlayers:
        raise HTTPException(status_code=400, detail="Invalid number of human players. Must be 0, 1, or 2.")
    
    if num_human_players == 1 and not player1_name:
        raise HTTPException(status_code=400, detail="Player 1 name is required for one human player.")
    
    if num_human_players == 2:
        if not player1_name or not player2_name:
            raise HTTPException(status_code=400, detail="Both player names are required for two human players.")
    
    player1_type = "human" if num_human_players > 0 else "computer"
    player2_type = "human" if num_human_players > 1 else "computer"
    
    game_logic = GameLogic(player1_name, player2_name, player1_type, player2_type, num_human_players)
    games[game_logic.game.id] = game_logic  # Store the GameLogic instance
    return game_logic.to_dict()

@router.get(
    "/games/{game_id}",
    response_model=Game,
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"}
    },
    tags=["Game Management"],
    summary="Get a specific game",
    description=(
        "Retrieve the current state of a specific game by its unique game ID."
        "The response includes the game ID, players, board state, and current status."
    )
)
def get_game(game_id: str) -> Game:
    """
    Get the current state of a specific game.
    """
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_logic.to_dict()

@router.post(
    "/games/{game_id}/restart",
    response_model=Game,
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"}
    },
    tags=["Game Management"],
    summary="Restart a game",
    description="Reset the game board while keeping existing player information."
)
def restart_game(game_id: str) -> Game:
    """
    Restart the game; resetting the board while keeping existing player information.
    """
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_logic.game.board = [[None for _ in range(7)] for _ in range(6)]  # Reset the board
    game_logic.game.winner = None
    game_logic.game.status = "in-progress"
    game_logic.game.current_turn = "p1"  # Reset to player 1's turn

    return game_logic.to_dict()

@router.post(
    "/games/{game_id}/quit",
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"}
    },
    tags=["Game Management"],
    summary="Quit a game",
    description="Remove the specified game from the list of active games."
)
def quit_game(game_id: str) -> dict:
    """
    Quit the game. The game will be removed from the list of games.
    """
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")

    del games[game_id]  # Remove the game from the dictionary
    return {"message": "Game has been quit.", "game_id": game_id}

# Gameplay Endpoints
@router.post(
    "/games/{game_id}/moves",
    response_model=Game,
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"},
        400: {"model": ErrorResponse, "description": "Invalid move"}
    },
    tags=["Gameplay"],
    summary="Make a move in the game",
    description="Drop a piece in the specified column for the given game."
)
def make_move(
    game_id: str,
    player_id: str = Query(..., description="ID of the player making the move"),
    column: int = Query(..., description="Column to drop the piece in")
) -> Game:
    """
    Make a move by dropping a piece in a column.
    """
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")

    result = game_logic.make_move(player_id, column)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return game_logic.to_dict()

@router.post(
    "/games/{game_id}/next_move",
    responses={
        404: {"model": ErrorResponse, "description": "Game not found"},
        400: {"model": ErrorResponse, "description": "No valid moves available"}
    },
    tags=["Gameplay"],
    summary="Get the next move for the computer player",
    description="Calculate the next move for the computer player in the specified game."
)
def get_next_move(game_id: str) -> dict:
    """
    Get the next move for the computer player. Currently, this is a random move.
    """
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")

    next_move = game_logic.get_next_move()
    if next_move is None:
        raise HTTPException(status_code=400, detail="No valid moves available")
    
    return {"message": "Next move calculated.", "next_move": next_move}
