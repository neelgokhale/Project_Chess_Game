"""
Created by Neel Gokhale at 2020-07-20
File chessengine.py from project Project_Chess_Game
Built using PyCharm

"""


# Responsible for storing all information about current state of game and determine all valid moves with movelog


class GameState:

    def __init__(self):

        """
        - board is an `8 x 8` 2d list, each element has 2 chars
        - first char: color `(w, b)`
        - second char: type `(K, Q, B, N, R, p)`
        """

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.move_functions = {'p': self.get_pawn_moves,
                               'R': self.get_rook_moves,
                               'N': self.get_knight_moves,
                               'B': self.get_bishop_moves,
                               'K': self.get_king_moves,
                               'Q': self.get_queen_moves}

        self.whitetomove = True
        self.movelog = []

        # tracking king
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)

        self.check_mate = False
        self.stale_mate = False

        # enpassant
        self.enpassant_possible = ()

        # Castling rights
        self.current_castling_rights = CastlingRights(True, True, True, True)
        self.castle_rights_log = [CastlingRights(self.current_castling_rights.wks,
                                                 self.current_castling_rights.bks,
                                                 self.current_castling_rights.wqs,
                                                 self.current_castling_rights.bqs)]

    def make_move(self, move):

        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move)
        self.whitetomove = not self.whitetomove

        # update kings location
        if move.piece_moved == 'wK':
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # enpassant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'

        # update enpassant_possible var
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # castling move
        if move.is_castling_move:
            if move.end_col - move.start_col == 2: # king side castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # moves the rook into new square
                self.board[move.end_row][move.end_col + 1] = '--'
            else:  # queen side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # moves the rook into new square
                self.board[move.end_row][move.end_col - 2] = '--'

        # update castling rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastlingRights(self.current_castling_rights.wks,
                                                     self.current_castling_rights.bks,
                                                     self.current_castling_rights.wqs,
                                                     self.current_castling_rights.bqs))

    def update_castle_rights(self, move):
        """
        update castling rights (only at rook or king move)
        """
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False

        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False

        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False

        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False

    def undo_move(self):

        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whitetomove = not self.whitetomove

            # update kings location
            if move.piece_moved == 'wK':
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_loc = (move.start_row, move.start_col)

            # undo enpassant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            # undo 2 sq pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row):
                self.enpassant_possible = ()

            # undo castling rights move
            self.castle_rights_log.pop() # get rid of new castle rights from log
            new_rights = self.castle_rights_log[-1]
            self.current_castling_rights = CastlingRights(new_rights.wks,
                                                          new_rights.bks,
                                                          new_rights.wqs,
                                                          new_rights.bqs)

            # undo castle mode
            if move.is_castling_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

    def get_valid_moves(self):

        """
        all moves considering checks
        """

        # temp vars

        temp_enpassant_poss = self.enpassant_possible
        temp_castle_rights = CastlingRights(self.current_castling_rights.wks,
                                            self.current_castling_rights.bks,
                                            self.current_castling_rights.wqs,
                                            self.current_castling_rights.bqs)

        moves = self.get_possible_moves()

        # get castling moves
        if self.whitetomove:
            self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves)
        else:
            self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves)

        for i in range(len(moves) - 1, -1, -1):  # go backwards when removing items from list
            self.make_move(moves[i])
            self.whitetomove = not self.whitetomove  # make_move switches turns, switch after to run in check

            if self.in_check():
                moves.remove(moves[i])
            self.whitetomove = not self.whitetomove  # switch it back
            self.undo_move()

        if len(moves) == 0:  # either checkmate or stalemate
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False

        self.enpassant_possible = temp_enpassant_poss
        self.current_castling_rights = temp_castle_rights

        return moves

    def in_check(self):

        """
        determine if the current player is in check
        """

        if self.whitetomove:
            return self.sq_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.sq_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def sq_under_attack(self, r, c):

        """
        determine if the enemy can attach square r, c
        """

        self.whitetomove = not self.whitetomove
        enemy_moves = self.get_possible_moves()
        self.whitetomove = not self.whitetomove

        for move in enemy_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_possible_moves(self):

        """
        all moves without considering checks
        """

        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # black or whites turn

                if (turn == 'w' and self.whitetomove) or (turn == 'b' and not self.whitetomove):
                    piece = self.board[r][c][1]

                    self.move_functions[piece](r, c, moves)  # move function dict

        return moves

    def get_pawn_moves(self, r, c, moves):

        """
        get all pawn moves
        """

        if self.whitetomove:
            if self.board[r - 1][c] == '--':  # 1 sq pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 sq pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':  # left capture enemy piece
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_enpassant_move=True))

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':  # right capture enemy piece
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_enpassant_move=True))

        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))

            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, r, c, moves):

        """
        get all rook moves
        """

        dirs = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.whitetomove else 'w'

        for d in dirs:
            for i in range(1, 8):
                end_row = r + i * d[0]
                end_col = c + i * d[1]

                if (0 <= end_row < 8) and (0 <= end_col < 8):
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_bishop_moves(self, r, c, moves):

        """
        get all bishop moves
        """

        dirs = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.whitetomove else 'w'

        for d in dirs:
            for i in range(1, 8):
                end_row = r + i * d[0]
                end_col = c + i * d[1]

                if (0 <= end_row < 8) and (0 <= end_col < 8):
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):

        """
        get all knight moves
        """

        knight_moves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        ally_color = 'w' if self.whitetomove else 'b'

        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]

            if (0 <= end_row < 8) and (0 <= end_col < 8):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_king_moves(self, r, c, moves):

        """
        get all king moves
        """

        king_moves = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        ally_color = 'w' if self.whitetomove else 'b'

        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]

            if (0 <= end_row < 8) and (0 <= end_col < 8):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        """
        Generate all valid castle moves for the king at (r, c) and add them to valid moves list
        """
        if self.sq_under_attack(r, c):
            return # cannot castle when in check

        if (self.whitetomove and self.current_castling_rights.wks) or (not self.whitetomove and self.current_castling_rights.bks):
            self.get_king_side_castle(r, c, moves)
        if (self.whitetomove and self.current_castling_rights.wqs) or (not self.whitetomove and self.current_castling_rights.bqs):
            self.get_queen_side_castle(r, c, moves)

    def get_king_side_castle(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.sq_under_attack(r, c + 1) and not self.sq_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castling_move=True))

    def get_queen_side_castle(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3]:
            if not self.sq_under_attack(r, c - 1) and not self.sq_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castling_move=True))

    def get_queen_moves(self, r, c, moves):

        """
        get all queen moves
        """

        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)


class CastlingRights:
    """
    To define possible castling rights
    """

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranks_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_ranks = {v: k for k, v in ranks_rows.items()}

    files_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_files = {v: k for k, v in files_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castling_move=False):

        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # Pawn promotion

        self.is_pawn_promotion = False
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.is_pawn_promotion = True

        # Enpassant

        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        # Castling Move

        self.is_castling_move = is_castling_move

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col * 1
        # print(self.move_id)


    def __eq__(self, other):

        """
        overriding equals method
        """

        if isinstance(other, Move):
            return self.move_id == other.move_id

        return False

    def get_chess_notation(self):

        """
        string move notation
        """

        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        """
        get rank file
        """
        return self.cols_files[c] + self.rows_ranks[r]
