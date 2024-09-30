from uuid import uuid4
from pydantic import BaseModel
from typing import List, Optional
import random
from enum import Enum

class ErrorResponse(BaseModel):
    detail: str

# Define the Player model
class Player(BaseModel):
    id: str
    name: str
    color: str
    type: str

class NumHumanPlayers(int, Enum):
    zero = 0
    one = 1
    two = 2

class GameStatus(str, Enum):
    IN_PROGRESS = "in-progress"
    WON = "won"
    DRAW = "draw"

# Define the Game model
class Game(BaseModel):
    id: str
    board: List[List[Optional[str]]]
    players: dict
    current_turn: str
    status: GameStatus
    winner: Optional[str] = None
    num_players: NumHumanPlayers # 0, 1, or 2 of the players are human

    class Config:
        orm_mode = True

# Game logic class
class GameLogic:
    def __init__(self, player1_name: str, player2_name: str, player1_type: str = "human", player2_type: str = "human", num_human_players: NumHumanPlayers = NumHumanPlayers.two):
        self.game = Game(
            id=str(uuid4()),
            board=[[None for _ in range(7)] for _ in range(6)],
            players={
                "p1": Player(id="p1", name=player1_name, color="red", type=player1_type),
                "p2": Player(id="p2", name=player2_name, color="yellow", type=player2_type),
            },
            current_turn="p1",
            status=GameStatus.IN_PROGRESS,
            num_players=num_human_players
        )
    
    def make_move(self, player_id: str, column: int):
        if self.game.winner:
            return {"error": "Game already won."}

        if self.game.current_turn != player_id:
            return {"error": "It's not your turn."}

        if column < 0 or column >= 7:
            return {"error": "Column out of bounds."}

        if self.game.board[0][column] is not None:
            return {"error": "Column is full."}

        for row in reversed(range(6)):
            if self.game.board[row][column] is None:
                self.game.board[row][column] = player_id
                if self.check_winner(row, column):
                    self.game.winner = player_id
                    self.game.status = GameStatus.WON
                elif all(cell is not None for row in self.game.board for cell in row):
                    self.game.status = GameStatus.DRAW
                else:
                    self.game.current_turn = "p2" if self.game.current_turn == "p1" else "p1"
                return self.game

        return {"error": "Invalid move."}

    def check_winner(self, row: int, column: int):
        player_id = self.game.board[row][column]
        return (self.check_direction(row, column, 1, 0, player_id) or
                self.check_direction(row, column, 0, 1, player_id) or
                self.check_direction(row, column, 1, 1, player_id) or
                self.check_direction(row, column, 1, -1, player_id))

    def check_direction(self, row: int, column: int, row_dir: int, col_dir: int, player_id: str):
        count = 0
        for delta in range(-3, 4):
            r = row + delta * row_dir
            c = column + delta * col_dir
            if 0 <= r < 6 and 0 <= c < 7 and self.game.board[r][c] == player_id:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
        return False

    def to_dict(self):
        return self.game.dict()  # Use Pydantic's dict method to get a dict representation

    def get_next_move(self):
        if self.game.winner:
            return {"error": "Game already won."}

        if all(cell is not None for row in self.game.board for cell in row):
            return {"error": "Board is full."}

        # Collect all empty columns
        empty_columns = [col for col in range(7) if self.game.board[0][col] is None]

        if not empty_columns:
            return {"error": "No valid moves available"}

        # Choose a random empty column
        next_move = random.choice(empty_columns)
        return next_move