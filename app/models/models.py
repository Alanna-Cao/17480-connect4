from uuid import uuid4
from pydantic import BaseModel
from typing import List, Optional

# Define the Player model
class Player(BaseModel):
    id: str
    name: str
    color: str

# Define the Game model
class Game(BaseModel):
    id: str
    board: List[List[Optional[str]]]
    players: dict
    current_turn: str
    status: str
    winner: Optional[str] = None

    class Config:
        orm_mode = True

# Game logic class
class GameLogic:
    def __init__(self, player1_name: str, player2_name: str):
        self.game = Game(
            id=str(uuid4()),
            board=[[None for _ in range(7)] for _ in range(6)],
            players={
                "p1": Player(id="p1", name=player1_name, color="red"),
                "p2": Player(id="p2", name=player2_name, color="yellow"),
            },
            current_turn="p1",
            status="in-progress"
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
                    self.game.status = "won"
                elif all(cell is not None for row in self.game.board for cell in row):
                    self.game.status = "draw"
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
