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
            "description": "A list of all games, including game ID, players, board state, current turn, and status for each game.",
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
                            "status": "in-progress",
                            "current_turn": "p1"
                        }
                    ]
                }
            }
        }
    })
def list_games() -> List[Game]:
    """
    Get a list of all games, including key details such as game ID, player names, board state, and game status (e.g., in-progress, won, draw).
    """
    return [game.to_dict() for game in games.values()]

@router.post(
    "/games",
    response_model=Game,
    responses={
        200: {
            "description": "Game created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "game_id_1",
                        "players": {
                            "p1": {"name": "Alice", "type": "human"},
                            "p2": {"name": "Computer", "type": "computer"}
                        },
                        "board": [[None, None, None, None, None, None, None] for _ in range(6)],
                        "status": "in-progress",
                        "current_turn": "p1"
                    }
                }
            }
        },
        400: {
            "description": "Invalid number of human players or missing player names",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Player 1 name is required for one human player."
                    }
                }
            }
        }
    },
    tags=["Game Management"],
    summary="Create a new game"
)
def create_game(
    player1_name: str = Query(None, description="Name of player 1 (required for human players)"),
    player2_name: str = Query(None, description="Name of player 2 (required for two human players)"),
    num_human_players: NumHumanPlayers = Query(..., description="Number of human players (0, 1, or 2)")
) -> Game:
    """
    Creates a new game with a specified number of human players. 
    - If `num_human_players` is 0, both players will be computer players.
    - If `num_human_players` is 1, player 1 must provide a name, and player 2 will be a computer player.
    - If `num_human_players` is 2, both player names are required.

    If the player names are not provided according to the specified number of human players, appropriate HTTP exceptions will be raised.    """
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
        200: {
            "description": "Game retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "game_id_1",
                        "players": {
                            "p1": {
                                "id": "p1",
                                "name": "Alice",
                                "color": "red",
                                "type": "human"
                            },
                            "p2": {
                                "id": "p2",
                                "name": "Computer",
                                "color": "yellow",
                                "type": "computer"
                            }
                        },
                        "board": [[None, None, None, None, None, None, None] for _ in range(6)],
                        "status": "in-progress",
                        "current_turn": "p1",
                        "winner": None,
                        "num_players": 2
                    }
                }
            }
        },
        404: {
            "description": "Game not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Game not found"}
                }
            }
        }
    },
    tags=["Game Management"],
    summary="Get the current state of a specific game."
)
def get_game(game_id: str) -> Game:
    """
    Get the current state of a specific game identified by the `game_id`. 
    The status field indicates whether the game is in progress, won, or drawn.
    The `winner` field indicates the id of the player who has won the game. For games in progress or drawn, this field is `None` (will not appear in output dicts).
    """
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_logic.to_dict()

@router.post(
    "/games/{game_id}/restart",
    response_model=Game,
    responses={
        200: {
            "description": "Game restarted successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "game_id_1",
                        "players": {
                            "p1": {"name": "Alice", "type": "human"},
                            "p2": {"name": "Computer", "type": "computer"}
                        },
                        "board": [[None, None, None, None, None, None, None] for _ in range(6)],
                        "status": "in-progress",
                        "current_turn": "p1",
                        "winner": None
                    }
                }
            }
        },
        404: {
            "description": "Game not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Game not found"}
                }
            }
        }
    },
    tags=["Game Management"],
    summary="Restart a game"
)
def restart_game(game_id: str) -> Game:
    """
    Restarts the specified game by resetting the game board and status, while preserving the original player details (names and types). This is useful if players want to start a new round without creating a new game from scratch.
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
        200: {
            "description": "Game has been quit successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Game has been quit.",
                        "game_id": "game_id_1"
                    }
                }
            }
        },
        404: {
            "description": "Game not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Game not found"}
                }
            }
        }
    },
    tags=["Game Management"],
    summary="Quit a game"
)
def quit_game(game_id: str) -> dict:
    """
    Remove the game from the in-memory storage. This effectively "quits" the game and deletes all associated data, freeing up resources. Quitting a game is irreversible, and the game cannot be recovered after quitting.
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
        200: {
            "description": "Move made successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "game_id_1",
                        "players": {
                            "p1": {"name": "Alice", "type": "human"},
                            "p2": {"name": "Computer", "type": "computer"}
                        },
                        "board": [
                            [None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None], 
                            [None, None, None, None, None, None, None], 
                            [None, None, None, None, None, None, None], 
                            [None, None, None, None, None, None, None],  
                            [None, None, None, "p1", None, None, None] 
                        ],
                        "status": "in-progress",
                        "current_turn": "p2",
                        "winner": None
                    }
                }
            }
        },
        400: {
            "description": "Invalid move",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid move."}
                }
            }
        },
        404: {
            "description": "Game not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Game not found"}
                }
            }
        }
    },
    tags=["Gameplay"],
    summary="Make a move in the game"
)
def make_move(
    game_id: str,
    player_id: str = Query(..., description="ID of the player making the move"),
    column: int = Query(..., description="Column to drop the piece in")
) -> Game:
    """
    Make a move by specifying the column in which to drop their piece. This checks that the move is valid by ensuring it's the correct player's turn, the column is within bounds, and the column is not full. If any condition fails, an appropriate error response is returned.
    Potential error responses include:
    - "Game already won": The game has already been won, and no more moves can be made.
    - "It's not your turn": The move was made by a player who is not currently allowed to make a move.
    - "Column out of bounds": The specified column is not within the valid range.
    - "Column is full": The specified column is already full, and no more pieces can be dropped in it.
    - "Invalid move": A generic catch-all error indicating that the move was not successful.
    - "Game not found": The specified game ID does not correspond to an active game.
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
        200: {
            "description": "Next move calculated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Next move calculated.",
                        "next_move": 4
                    }
                }
            }
        },
        400: {
            "description": "No valid moves available",
            "content": {
                "application/json": {
                    "example": {"detail": "No valid moves available"}
                }
            }
        },
        404: {
            "description": "Game not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Game not found"}
                }
            }
        }
    },
    tags=["Gameplay"],
    summary="Get the next move for the computer player"
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
    
    return {"message": "Next move calculated.", "next_move": next_move["next_move"]}
