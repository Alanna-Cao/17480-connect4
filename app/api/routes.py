from fastapi import APIRouter, HTTPException
from app.models.models import GameLogic, Game
from uuid import uuid4
from typing import List

router = APIRouter()
games = {}

# Game Management Endpoints
@router.get("/games", response_model=List[Game], tags=["Game Management"])
def list_games():
    """Get a list of all games."""
    return [game.to_dict() for game in games.values()]

@router.post("/games", response_model=Game, tags=["Game Management"])
def create_game(player1_name: str, player2_name: str, num_human_players: int):
    """Create a new game with zero, one or two human players."""
    player1_type = "human" if num_human_players > 0 else "computer"
    player2_type = "human" if num_human_players > 1 else "computer"
    game_logic = GameLogic(player1_name, player2_name, player1_type, player2_type, num_human_players)
    games[game_logic.game.id] = game_logic  # Store the GameLogic instance
    return game_logic.to_dict()

@router.get("/games/{game_id}", response_model=Game, tags=["Game Management"])
def get_game(game_id: str):
    """Get the current state of a specific game."""
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_logic.to_dict()

@router.post("/games/{game_id}/restart", response_model=Game, tags=["Game Management"])
def restart_game(game_id: str):
    """Restart the game; resetting the board while keeping existing player information."""
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_logic.game.board = [[None for _ in range(7)] for _ in range(6)]  # Reset the board
    game_logic.game.winner = None
    game_logic.game.status = "in-progress"
    game_logic.game.current_turn = "p1"  # Reset to player 1's turn

    return game_logic.to_dict()

@router.post("/games/{game_id}/quit", tags=["Game Management"])
def quit_game(game_id: str):
    """Quit the game"""
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")

    return {"message": "Game has been quit.", "game_id": game_id}

# Gameplay Endpoints
@router.post("/games/{game_id}/moves", response_model=Game, tags=["Gameplay"])
def make_move(game_id: str, player_id: str, column: int):
    """Make a move by dropping a piece in a column."""
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")

    result = game_logic.make_move(player_id, column)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return game_logic.to_dict()

@router.post("/games/{game_id}/next_move", tags=["Gameplay"])
def get_next_move(game_id: str):
    """Get the next move for the computer player."""
    game_logic = games.get(game_id)
    if not game_logic:
        raise HTTPException(status_code=404, detail="Game not found")

    next_move = game_logic.get_next_move()
    if next_move is None:
        raise HTTPException(status_code=400, detail="No valid moves available")
    
    return {"message": "Next move calculated.", "next_move": next_move}