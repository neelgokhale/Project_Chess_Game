"""
Created by Neel Gokhale at 2020-07-20
File chessmain.py from project Project_Chess_Game
Built using PyCharm

"""

# Main driver file: responsible for handeling user input and current Gamestate object


import pygame as p
import chessengine

# Consts

WIDTH = HEIGHT = 512
DIMENSIONS = 8
SQ_SIZE = HEIGHT // DIMENSIONS
MAX_FPS = 15
IMAGES = {}


def load_images():
    """
    initialize global image dictionary
    """

    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("img/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    """
    main game function
    """

    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessengine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag var for when a valid move is made by user
    animate = False  # flag var for enabling anims
    game_over = False  # game over

    load_images()

    running = True
    sq_selected = ()
    player_click = []

    while running:

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_click = []
                    else:
                        sq_selected = (row, col)
                        player_click.append(sq_selected)
                    if len(player_click) == 2:
                        move = chessengine.Move(player_click[0], player_click[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_click = []
                        if not move_made:
                            player_click = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo
                    gs.undo_move()
                    move_made = True
                    animate = False
                if e.key == p.K_r:  # reset
                    gs = chessengine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_click = []
                    move_made = False
                    animate = False

        if move_made:
            if animate:
                animate_move(gs.movelog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.check_mate:
            game_over = True
            if gs.whitetomove:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, "White wins by checkmate")
        elif gs.stale_mate:
            game_over = True
            draw_text(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


def draw_board(screen):
    """
    draw squares on board
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]

    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    """
    draw pieces on board
    """

    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):

            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whitetomove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    """
    responsible for all graphics in current gamestates
    """

    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_sq = 10  # frames per square
    frame_count = (abs(dR) + abs(dC)) * frames_per_sq
    for frame in range(frame_count + 1):
        r, c = ((move.start_row + dR * (frame / frame_count),
                 move.start_col + dC * (frame / frame_count)))
        draw_board(screen)
        draw_pieces(screen, board)
        # erase piece moved from ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece into rect
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_text(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    text_obj = font.render(text, 0, p.Color('white'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_obj.get_width() / 2,
                                                     HEIGHT / 2 - text_obj.get_height() / 2)
    screen.blit(text_obj, text_location)
    text_obj = font.render(text, 0, p.Color('black'))
    screen.blit(text_obj, text_location.move(2, 2))


if __name__ == "__main__":
    main()
