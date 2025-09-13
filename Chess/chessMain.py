import pygame as p
from chessEngine import GameState

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
                    move = GameState.Move(playerClicks[0],playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    makeMove(move)
                    sqSelected = ()
                    playerClicks = []
                
        
        drawGameState(screen, gs)        
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs):
    drawBoard(screen)#draw squares on the board
    #add in piece highlighting or move suggestions
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
                

        
if __name__ == "__main__":
        main()
    
  
    
