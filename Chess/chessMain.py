import pygame as p
import tkinter as tk
from tkinter import messagebox
import os
from chessEngine import GameState, Move

Width = Height = 1080
Dimension = 8
SQ_SIZE = Height // Dimension
MAX_FPS = 15
IMAGES = {}
PIECE_SIZE = 100
#Make a global dictionary to store the images from files of images
def loadImages():
    # load images next to this file so paths always work
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, "images")
    for piece in pieces:
          path = os.path.join(img_dir, piece + ".png")
          IMAGES[piece] = p.transform.scale(p.image.load(path), (PIECE_SIZE, PIECE_SIZE))
#This will handle/drive most of the code. This will handles input and update screen/GUI that the player see.
          
def main():
    user = login_window()
    if not user:
        return
    settings = settings_window()
    if settings is None:
        return
    base_seconds, increment_seconds, player_side = settings
    orientationWhiteBottom = (player_side == 'white')
    p.init()
    # auto-fit board to screen, keep 1080 design ratio
    info = p.display.Info()
    max_fit = max(400, min(info.current_w, info.current_h) - 80)
    board_size = min(1080, max_fit)
    # update globals for drawing
    global Width, Height, SQ_SIZE, PIECE_SIZE
    Width = Height = board_size
    SQ_SIZE = Height // Dimension
    # keep piece ~100 on 135px squares ratio (~0.74)
    PIECE_SIZE = max(60, int(SQ_SIZE * (100/135)))
    screen = p.display.set_mode((Width, Height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    font = p.font.SysFont(None, 42)
    gs = GameState()
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    validMoves = gs.getValidMoves()
    white_time_ms = int(base_seconds * 1000)
    black_time_ms = int(base_seconds * 1000)
    increment_ms = int(increment_seconds * 1000)
    game_over_text = ""
    while running:
        dt = clock.tick(MAX_FPS)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not game_over_text:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                # map screen -> board based on orientation
                if not orientationWhiteBottom:
                    col = 7 - col
                    row = 7 - row
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = Move(playerClicks[0],playerClicks[1], gs.board)
                    if move in validMoves:
                        moved_white = gs.whiteToMove
                        gs.makeMove(move)
                        # add increment for the player who moved
                        if moved_white:
                            white_time_ms += increment_ms
                        else:
                            black_time_ms += increment_ms
                        validMoves = gs.getValidMoves()
                        print(move.getChessNotation())
                        # checkmate/stalemate after the move
                        if len(validMoves) == 0:
                            if gs.isInCheck(gs.whiteToMove):
                                game_over_text = "Checkmate - " + ("White" if not gs.whiteToMove else "Black") + " wins"
                            else:
                                game_over_text = "Stalemate"
                    else:
                        print("Illegal move")
                    sqSelected = ()
                    playerClicks = []
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u: # undo move
                    gs.undoMove()
                    validMoves = gs.getValidMoves()
        if not game_over_text:
            if gs.whiteToMove:
                white_time_ms -= dt
                if white_time_ms <= 0:
                    white_time_ms = 0
                    game_over_text = "White out of time - Black wins"
            else:
                black_time_ms -= dt
                if black_time_ms <= 0:
                    black_time_ms = 0
                    game_over_text = "Black out of time - White wins"
        drawGameState(screen, gs, sqSelected, validMoves, orientationWhiteBottom)
        drawClocks(screen, font, white_time_ms, black_time_ms)
        if game_over_text:
            drawGameOver(screen, font, game_over_text)
        p.display.flip()

def drawGameState(screen, gs, sqSelected, validMoves, whiteBottom):
    drawBoard(screen, whiteBottom) # squares
    drawHighlights(screen, sqSelected, validMoves, whiteBottom)
    drawPieces(screen, gs.board, whiteBottom) # pieces on top
    drawLabels(screen, whiteBottom)
#Draw squares on the boards
def drawBoard(screen, whiteBottom):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(Dimension):
        for c in range (Dimension):
            color = colors[((r+c) % 2)]
            dr = r if whiteBottom else 7 - r
            dc = c if whiteBottom else 7 - c
            p.draw.rect(screen, color, p.Rect(dc*SQ_SIZE, dr*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                      

def drawPieces(screen, board, whiteBottom):
    for r in range (Dimension):
        for c in range (Dimension):
            piece = board[r][c]
            if piece != "--":
                dr = r if whiteBottom else 7 - r
                dc = c if whiteBottom else 7 - c
                x = dc*SQ_SIZE + (SQ_SIZE - PIECE_SIZE)//2
                y = dr*SQ_SIZE + (SQ_SIZE - PIECE_SIZE)//2
                screen.blit(IMAGES[piece], (x, y))

def drawHighlights(screen, sqSelected, validMoves, whiteBottom):
    if sqSelected == ():
        return
    r, c = sqSelected
    # highlight selected square
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(p.Color('yellow'))
    dr = r if whiteBottom else 7 - r
    dc = c if whiteBottom else 7 - c
    screen.blit(s, (dc*SQ_SIZE, dr*SQ_SIZE))
    # highlight legal moves for that square
    for m in validMoves:
        if (m.startRow, m.startCol) == (r, c):
            dr2 = m.endRow if whiteBottom else 7 - m.endRow
            dc2 = m.endCol if whiteBottom else 7 - m.endCol
            center = (dc2*SQ_SIZE + SQ_SIZE//2, dr2*SQ_SIZE + SQ_SIZE//2)
            p.draw.circle(screen, p.Color('red'), center, SQ_SIZE//8)

def drawLabels(screen, whiteBottom):
    # a-h and 1-8 labels small
    small = p.font.SysFont(None, 24)
    files = ['a','b','c','d','e','f','g','h']
    ranks = ['1','2','3','4','5','6','7','8']
    for c in range(8):
        fileChar = files[c] if whiteBottom else files[7-c]
        text = small.render(fileChar, True, p.Color('black'))
        screen.blit(text, (c*SQ_SIZE + 4, Height - text.get_height() - 4))
    for r in range(8):
        rankChar = ranks[7-r] if whiteBottom else ranks[r]
        text = small.render(rankChar, True, p.Color('black'))
        screen.blit(text, (4, r*SQ_SIZE + 4))

def drawClocks(screen, font, white_ms, black_ms):
    def fmt(ms):
        total = max(0, ms//1000)
        m = total//60
        s = total%60
        return f"{m:02d}:{s:02d}"
    # top = black, bottom = white
    black_surf = font.render(f"Black: {fmt(black_ms)}", True, p.Color('black'))
    white_surf = font.render(f"White: {fmt(white_ms)}", True, p.Color('black'))
    screen.blit(black_surf, (10, 10))
    screen.blit(white_surf, (10, Height - 10 - white_surf.get_height()))

def drawGameOver(screen, font, text):
    s = p.Surface((Width, Height))
    s.set_alpha(140)
    s.fill(p.Color('white'))
    screen.blit(s, (0, 0))
    t = font.render(text, True, p.Color('red'))
    rect = t.get_rect(center=(Width//2, Height//2))
    screen.blit(t, rect)

def login_window():
    # simple login/register saved to users.txt
    path = "users.txt"
    users = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    users[parts[0]] = parts[1]
    except FileNotFoundError:
        pass
    result = {"user": None}
    root = tk.Tk()
    root.title("Login")
    tk.Label(root, text="Username").grid(row=0, column=0)
    tk.Label(root, text="Password").grid(row=1, column=0)
    u = tk.Entry(root)
    pwd = tk.Entry(root, show='*')
    u.grid(row=0, column=1)
    pwd.grid(row=1, column=1)
    def do_login():
        name = u.get().strip()
        pw = pwd.get().strip()
        if name in users and users[name] == pw:
            result["user"] = name
            root.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    def do_register():
        name = u.get().strip()
        pw = pwd.get().strip()
        if not name or not pw:
            messagebox.showerror("Error", "Please enter username and password")
            return
        if name in users:
            messagebox.showerror("Error", "User exists")
            return
        users[name] = pw
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"{name}:{pw}\n")
        messagebox.showinfo("OK", "Registered. You can log in now.")
    tk.Button(root, text="Login", command=do_login).grid(row=2, column=0, sticky='we')
    tk.Button(root, text="Register", command=do_register).grid(row=2, column=1, sticky='we')
    root.mainloop()
    return result["user"]

def settings_window():
    # choose side and time control
    result = {"done": False, "base": 180, "inc": 0, "side": 'white'}
    root = tk.Tk()
    root.title("Game Settings")
    tk.Label(root, text="Choose Side").pack(anchor='w')
    side_var = tk.StringVar(value='white')
    tk.Radiobutton(root, text='White', variable=side_var, value='white').pack(anchor='w')
    tk.Radiobutton(root, text='Black', variable=side_var, value='black').pack(anchor='w')
    tk.Label(root, text="Time Control").pack(anchor='w', pady=(8,0))
    time_var = tk.StringVar(value='blitz3+0')
    options = [
        ('Bullet 1+0', 'bullet1+0', 60, 0),
        ('Bullet 2+1', 'bullet2+1', 120, 1),
        ('Blitz 3+0', 'blitz3+0', 180, 0),
        ('Blitz 3+2', 'blitz3+2', 180, 2),
        ('Blitz 5+0', 'blitz5+0', 300, 0),
        ('Rapid 15+10', 'rapid15+10', 900, 10),
        ('Rapid 30+0', 'rapid30+0', 1800, 0),
        ('Classical 60+0', 'class60+0', 3600, 0),
    ]
    radios = []
    for label, key, base, inc in options:
        r = tk.Radiobutton(root, text=label, variable=time_var, value=key)
        r.pack(anchor='w')
        radios.append((r, base, inc))
    def start():
        key = time_var.get()
        base = 180
        inc = 0
        for r, b, i in radios:
            if r.cget('value') == key:
                base, inc = b, i
                break
        result["done"] = True
        result["base"] = base
        result["inc"] = inc
        result["side"] = side_var.get()
        root.destroy()
    tk.Button(root, text='Start', command=start).pack(fill='x', pady=(8,0))
    tk.Button(root, text='Cancel', command=root.destroy).pack(fill='x')
    root.mainloop()
    if not result["done"]:
        return None
    return (result["base"], result["inc"], result["side"])
                

        
if __name__ == "__main__":
        main()
    
  
    
