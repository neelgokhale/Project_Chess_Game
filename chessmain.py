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
    load_images()

    running = True
    sq_selected = ()
    player_click = []

    while running:

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
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
                            sq_selected = ()
                            player_click = []
                    if not move_made:
                        player_click = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_board(screen):
    """
    draw squares on board
    """

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


def draw_game_state(screen, gs):
    """
    responsible for all graphics in current gamestates
    """

    draw_board(screen)
    draw_pieces(screen, gs.board)


if __name__ == "__main__":
    main()


















