# This class is reponsible for kickstart  all the information about current state of the chess game.
# This will also be responsible for check which move is valids.
# This will also keep move log.
class GameState():
    def __init__(self):
        #board is 2d 8x8 chess board, each elment of the list has 2 characters.
        #"b" or "w" which is first letter represent the color of the pieces.
        # The second letter will be which pieces "K","Q","R","B",..
        #"--" Represent empty space that had no pieces occupies.
        
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog =[]
        # map piece letter to function (simple legal moves, no check rules yet)
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
    def makeMove(self, move):
        # move piece on board (very basic)
        self.board[move.startRow][move.startCol]= "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    # simple legal moves (no checks/castling/en passant/promotion yet)
    def getValidMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == "--":
                    continue
                turnWhite = piece[0] == 'w'
                if turnWhite != self.whiteToMove:
                    continue
                pieceType = piece[1]
                self.moveFunctions[pieceType](r, c, moves)
        return moves

    def squareInBounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def getPawnMoves(self, r, c, moves):
        piece = self.board[r][c]
        direction = -1 if piece[0] == 'w' else 1
        startRow = 6 if piece[0] == 'w' else 1
        # forward 1
        if self.squareInBounds(r + direction, c) and self.board[r + direction][c] == "--":
            moves.append(Move((r, c), (r + direction, c), self.board))
            # forward 2 from start
            if r == startRow and self.board[r + 2*direction][c] == "--":
                moves.append(Move((r, c), (r + 2*direction, c), self.board))
        # captures
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            if not self.squareInBounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target != "--" and target[0] != piece[0]:
                moves.append(Move((r, c), (nr, nc), self.board))

    def getRookMoves(self, r, c, moves):
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        self._getSlidingMoves(r, c, moves, directions)

    def getBishopMoves(self, r, c, moves):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        self._getSlidingMoves(r, c, moves, directions)

    def getQueenMoves(self, r, c, moves):
        directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        self._getSlidingMoves(r, c, moves, directions)

    def _getSlidingMoves(self, r, c, moves, directions):
        ownColor = self.board[r][c][0]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self.squareInBounds(nr, nc):
                target = self.board[nr][nc]
                if target == "--":
                    moves.append(Move((r, c), (nr, nc), self.board))
                else:
                    if target[0] != ownColor:
                        moves.append(Move((r, c), (nr, nc), self.board))
                    break
                nr += dr
                nc += dc

    def getKnightMoves(self, r, c, moves):
        ownColor = self.board[r][c][0]
        jumps = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in jumps:
            nr, nc = r + dr, c + dc
            if not self.squareInBounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target == "--" or target[0] != ownColor:
                moves.append(Move((r, c), (nr, nc), self.board))

    def getKingMoves(self, r, c, moves):
        ownColor = self.board[r][c][0]
        steps = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if not self.squareInBounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target == "--" or target[0] != ownColor:
                moves.append(Move((r, c), (nr, nc), self.board))
class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4":4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
                                                                                
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # compare moves by squares only (good enough for UI selection)
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.startRow == other.startRow and
                self.startCol == other.startCol and
                self.endRow == other.endRow and
                self.endCol == other.endCol)



            


    
        

    

            
