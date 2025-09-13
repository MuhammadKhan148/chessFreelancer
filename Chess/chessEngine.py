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
        # king locations to check checks quickly
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        # en passant target square (row, col) or None
        self.enPassantPossible = None
        # castling rights: wk/ wq / bk / bq
        self.castleRights = {
            'wks': True,
            'wqs': True,
            'bks': True,
            'bqs': True,
        }
        self.castleRightsLog = [self.castleRights.copy()]
    def makeMove(self, move):
        # move piece on board (very basic)
        self.board[move.startRow][move.startCol]= "--"
        # en passant capture remove the pawn behind
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # update king position
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # castling rook move
        if move.isCastleMove:
            if move.endCol == 6: # king side
                self.board[move.endRow][5] = self.board[move.endRow][7]
                self.board[move.endRow][7] = "--"
            else: # queen side
                self.board[move.endRow][3] = self.board[move.endRow][0]
                self.board[move.endRow][0] = "--"
        # promotion (auto queen)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        # update en passant target
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = None
        # update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(self.castleRights.copy())
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) == 0:
            return
        move = self.moveLog.pop()
        self.board[move.startRow][move.startCol] = move.pieceMoved
        # undo promotion restores pawn
        moved = move.pieceMoved
        if move.isPawnPromotion:
            moved = moved[0] + 'p'
            self.board[move.startRow][move.startCol] = moved
        # restore captured piece (en passant handled specially)
        if move.isEnPassantMove:
            self.board[move.endRow][move.endCol] = "--"
            self.board[move.startRow][move.endCol] = move.pieceCaptured
        else:
            self.board[move.endRow][move.endCol] = move.pieceCaptured
        # undo king pos
        if moved == 'wK':
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif moved == 'bK':
            self.blackKingLocation = (move.startRow, move.startCol)
        # undo castle rook move
        if move.isCastleMove:
            if move.endCol == 6:
                self.board[move.endRow][7] = self.board[move.endRow][5]
                self.board[move.endRow][5] = "--"
            else:
                self.board[move.endRow][0] = self.board[move.endRow][3]
                self.board[move.endRow][3] = "--"
        # restore castle rights and en passant
        self.castleRightsLog.pop()
        self.castleRights = self.castleRightsLog[-1].copy()
        self.enPassantPossible = move.enPassantPossibleBefore
        self.whiteToMove = not self.whiteToMove

    # simple legal moves (no checks/castling/en passant/promotion yet)
    def getValidMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == "--":
                    continue
                if (piece[0] == 'w') != self.whiteToMove:
                    continue
                self.moveFunctions[piece[1]](r, c, moves)
        # add castle
        self.addCastleMoves(moves)
        # filter out moves that leave king in check
        legal = []
        for m in moves:
            m.enPassantPossibleBefore = self.enPassantPossible
            self.makeMove(m)
            in_check = self.isInCheck(not self.whiteToMove)
            self.undoMove()
            if not in_check:
                legal.append(m)
        return legal

    def squareInBounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def getPawnMoves(self, r, c, moves):
        piece = self.board[r][c]
        direction = -1 if piece[0] == 'w' else 1
        startRow = 6 if piece[0] == 'w' else 1
        # forward 1
        if self.squareInBounds(r + direction, c) and self.board[r + direction][c] == "--":
            mv = Move((r, c), (r + direction, c), self.board)
            moves.append(mv)
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
        # en passant
        if self.enPassantPossible is not None:
            ep_r, ep_c = self.enPassantPossible
            if (r + direction, c - 1) == (ep_r, ep_c) and self.board[r][c-1] != "--" and self.board[r][c-1][0] != piece[0]:
                mv = Move((r, c), (ep_r, ep_c), self.board, isEnPassant=True)
                moves.append(mv)
            if (r + direction, c + 1) == (ep_r, ep_c) and self.board[r][c+1] != "--" and self.board[r][c+1][0] != piece[0]:
                mv = Move((r, c), (ep_r, ep_c), self.board, isEnPassant=True)
                moves.append(mv)

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
        # castling added in addCastleMoves

    def isInCheck(self, forWhite=None):
        if forWhite is None:
            forWhite = self.whiteToMove
        king_r, king_c = self.whiteKingLocation if forWhite else self.blackKingLocation
        return self.squareAttacked(king_r, king_c, byWhite=not forWhite)

    def squareAttacked(self, r, c, byWhite):
        attackerColor = 'w' if byWhite else 'b'
        # pawns
        dr = -1 if byWhite else 1
        for dc in (-1, 1):
            rr, cc = r + dr, c + dc
            if self.squareInBounds(rr, cc) and self.board[rr][cc] == attackerColor + 'p':
                return True
        # knights
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr, cc = r + dr, c + dc
            if self.squareInBounds(rr, cc) and self.board[rr][cc] == attackerColor + 'N':
                return True
        # bishops/queens diagonals
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            rr, cc = r + dr, c + dc
            while self.squareInBounds(rr, cc):
                piece = self.board[rr][cc]
                if piece != "--":
                    if piece[0] == attackerColor and (piece[1] == 'B' or piece[1] == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        # rooks/queens straight
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            rr, cc = r + dr, c + dc
            while self.squareInBounds(rr, cc):
                piece = self.board[rr][cc]
                if piece != "--":
                    if piece[0] == attackerColor and (piece[1] == 'R' or piece[1] == 'Q'):
                        return True
                    break
                rr += dr
                cc += dc
        # king
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            rr, cc = r + dr, c + dc
            if self.squareInBounds(rr, cc) and self.board[rr][cc] == attackerColor + 'K':
                return True
        return False

    def addCastleMoves(self, moves):
        if self.whiteToMove:
            r = 7; color='w'
            in_check = self.isInCheck(True)
            if not in_check:
                # king side
                if self.castleRights['wks'] and self.board[r][5] == "--" and self.board[r][6] == "--":
                    if not self.squareAttacked(r, 5, byWhite=False) and not self.squareAttacked(r, 6, byWhite=False):
                        moves.append(Move((r,4),(r,6), self.board, isCastle=True))
                # queen side
                if self.castleRights['wqs'] and self.board[r][1] == "--" and self.board[r][2] == "--" and self.board[r][3] == "--":
                    if not self.squareAttacked(r, 2, byWhite=False) and not self.squareAttacked(r,3, byWhite=False):
                        moves.append(Move((r,4),(r,2), self.board, isCastle=True))
        else:
            r = 0; color='b'
            in_check = self.isInCheck(False)
            if not in_check:
                if self.castleRights['bks'] and self.board[r][5] == "--" and self.board[r][6] == "--":
                    if not self.squareAttacked(r,5, byWhite=True) and not self.squareAttacked(r,6, byWhite=True):
                        moves.append(Move((r,4),(r,6), self.board, isCastle=True))
                if self.castleRights['bqs'] and self.board[r][1] == "--" and self.board[r][2] == "--" and self.board[r][3] == "--":
                    if not self.squareAttacked(r,2, byWhite=True) and not self.squareAttacked(r,3, byWhite=True):
                        moves.append(Move((r,4),(r,2), self.board, isCastle=True))

    def updateCastleRights(self, move):
        # moving king revokes both sides; moving rook revokes that side
        if move.pieceMoved == 'wK':
            self.castleRights['wks'] = False
            self.castleRights['wqs'] = False
        elif move.pieceMoved == 'bK':
            self.castleRights['bks'] = False
            self.castleRights['bqs'] = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0:
                self.castleRights['wqs'] = False
            elif move.startRow == 7 and move.startCol == 7:
                self.castleRights['wks'] = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0:
                self.castleRights['bqs'] = False
            elif move.startRow == 0 and move.startCol == 7:
                self.castleRights['bks'] = False
        # capturing a rook on its start square also revokes
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 0:
            self.castleRights['wqs'] = False
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 7:
            self.castleRights['wks'] = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 0:
            self.castleRights['bqs'] = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 7:
            self.castleRights['bks'] = False
class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4":4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board, isEnPassant=False, isCastle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnPassantMove = isEnPassant
        if self.isEnPassantMove:
            # capture the pawn behind end square
            self.pieceCaptured = 'bp' if self.pieceMoved[0] == 'w' else 'wp'
        self.isCastleMove = isCastle
        self.isPawnPromotion = (self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7))
        self.enPassantPossibleBefore = None
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



            


    
        

    

            
