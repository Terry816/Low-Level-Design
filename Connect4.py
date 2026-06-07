"""
Taken with Open notes and I watched video solution

Design Connect4
Requirements:
    -Primary capabilities - Game should support 2 players who alternatively take turns making one move. Move is defined as putting a piece into a lot in a 6 x7 board
    -Rules and completion - Player with 4 in a row, horizontally, vertically, diagonally wins WINS. If board is full - DRAW. Else - IN_PROGRESS
    -Error Handling - piece out-of-bounds, player cannot go twice in a row, player cannot override another piece 
    -Out of Scope - No UI. No concurrency just a 1 on 1 game, players wait for the other before they can go

Entities:
    Game - orchestrator
    Board - hold the state of the board
    Player
    GAME_STATUS (ENUM) - WIN | DRAW | IN_PROGRESS
    COLOR (ENUM) - RED | BLUE

Design:

class Game:
    state:
    - Player1 : Player
    - Player2: Player
    - Board: Board
    - Current_Turn: Player

    behaviors:
    + makeMove(column) -> bool (True if it works, Raise an Error if invalid)
    + determineStatus() -> GAME_STATUS
    + getCurrentTurn() -> Player

class Board:
    state:
    - row: int
    - column: int
    - grid[row][col]:  # hardcoded as 6 x 7
    [[None] * column for _ in range(row)]

    + placePiece(column) -> row -1 if not valid move
    + checkWinner(row, column) -> bool
    from that recent piece check horizontal, vertical, diagonal for winner
    + checkDraw() -> checks if all pieces on the top are full
    + getColumn()
    + getRow()

class Player:
    state:
    - name: str
    - color: COLOR

    + getColor()
    
"""
from enum import Enum

class Color(Enum):
    RED = 1
    BLUE = 2

class OutofBoundsError(Exception):
    pass

class GameFinishError(Exception):
    pass

class Game:
    def __init__(self, player1: Player, player2: Player, board: Board):
        self.player1 = player1
        self.player2 = player2
        self.board = board
        self.current_player = player1
        self.game_status = "IN_PROGRESS"
        self.winner = None
    
    #+ makeMove(column) -> bool (True if it works, Raise an Error if invalid)
    def makeMove(self, column):
        if self.determineStatus() == "WINNER":
            raise GameFinishError("Game is Finished")
        if not self.board.isValidMove():
            raise OutofBoundsError("Invalid column")
        
        column -= 1 #users will see columns, but this is used for index

        row = self.board.placePiece(column, self.current_player.color)
        if self.board.checkWinner(row, column):
            self.game_status = "WINNER"
            self.winner = self.current_player
        elif self.board.checkDraw():
            self.game_status = "DRAW"
        else:
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        return True
    
    def determineStatus(self):
        return self.game_status

    def getCurrentTurn(self):
        return self.current_player.name

class Board:
    def __init__(self, row=6, column=7):
        self.row = row
        self.column = column
        self.grid = [[None] * column for _ in range(row)]
    
    def placePiece(self, column, color):
        if column < 0 or column >= self.column:
            return -1
        
        for i in range(len(self.row)-1, -1, -1):
            if not self.grid[i][column]:
                self.grid[i][column] = color
                return i
        return -1
    
    def checkDraw(self):
        return True if all(self.grid[0]) else False
    
    def checkWinner(self, column, row) -> bool:
        directions = [[0,1], [1,0], [1,1], [1, -1]]

        for dr, dc in directions:
            count = 1
            count += self.countColors(row+dr, column+dc, dr, dc) 
            count += self.countColors(row-dr, column-dc, -dr, -dc)
            if count >= 4:
                return True
        return False

    def countColors(self, row, col, dr, dc, color):
        if row < 0 or row >= self.row or col < 0 or col > self.column:
            return 0
        if self.grid[row][col] == color:
            return 1 + self.countColors(row +dr, col + dc, dr, dc)
        else: return 0

    
class Player:
    def __init__(self, name, color: Color):
        self.name = name
        self.color = color




