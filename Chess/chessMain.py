import pygame as p
from chessEngine import GameState, Move

Width = Height = 512
Dimension = 8
SQ_SIZE = Height // Dimension
MAX_FPS = 15
IMAGES = {}
#Make a global dictionary to store the images from files of images
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
          IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
#This will handle/drive most of the code. This will handles input and update screen/GUI that the player see.
          
def main():
    p.init()
    screen = p.display.set_mode((Width, Height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = GameState()
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    validMoves = gs.getValidMoves()
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                    
                sqSelected = (row, col)
                
                if len(playerClicks) == 2:
                    move = Move(playerClicks[0],playerClicks[1], gs.board)
                    # only make move if legal
                    if move in validMoves:
                        gs.makeMove(move)
                        validMoves = gs.getValidMoves()
                        print(move.getChessNotation())
                    sqSelected = ()
                    playerClicks = []
                
        
        drawGameState(screen, gs, sqSelected, validMoves)        
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs, sqSelected, validMoves):
    drawBoard(screen)#draw squares on the board
    drawHighlights(screen, sqSelected, validMoves)
    drawPieces(screen, gs.board) # draw the pieces take from images files on top of the squares being draws.
#Draw squares on the boards
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(Dimension):
        for c in range (Dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                      

def drawPieces(screen, board):
    for r in range (Dimension):
        for c in range (Dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawHighlights(screen, sqSelected, validMoves):
    if sqSelected == ():
        return
    r, c = sqSelected
    # highlight selected square
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(p.Color('yellow'))
    screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
    # highlight legal moves for that square
    for m in validMoves:
        if (m.startRow, m.startCol) == (r, c):
            center = (m.endCol*SQ_SIZE + SQ_SIZE//2, m.endRow*SQ_SIZE + SQ_SIZE//2)
            p.draw.circle(screen, p.Color('red'), center, SQ_SIZE//8)
                

        
if __name__ == "__main__":
        main()
    
  
    
