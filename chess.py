from copy import deepcopy
import pickle

from memento import Memento, CareTaker
from board import Board
from error import Check, InvalidMove, InvalidPiece, NotYourTurn


class Chess(object):
    """ class for a chess game """

    files = ["a", "b", "c", "d", "e", "f", "g", "h"]
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
    initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self, fen=None):
        if fen is None:
            fen = self.initial_fen
        self.board = Board(fen)
        self.history = []
        self._care_taker = CareTaker()

    def restart(self):
        self.board = Board(self.initial_fen)
        self.history = []

    def incheck_after(self, origin, dest):
        board_copy = deepcopy(self.board)
        piece = board_copy[origin]
        color = piece.color
        piece.move_to(dest)
        king_pos = board_copy.king_position(color)
        return king_pos in board_copy.attacked_squares(color)

    def incheck(self, color):
        king_pos = self.board.king_position(color)
        return king_pos in self.board.attacked_squares(color)

    def isdraw(self):
        pass

    def move(self, origin, dest):
        piece = self.board[origin]

        # if no piece at the origin, exit
        if piece is None:
            raise InvalidPiece(f"No piece at {origin}")

        # raise error if it's not the player's turn
        played = piece.color
        if played != self.board.playing:
            color = "white" if played == "w" else "black"
            raise NotYourTurn(f"It's not {color}'s turn")

        if self.incheck_after(origin, dest):
            raise InvalidMove("The king is under attack")

        # update board
        # 1. push to care-taker
        self._care_taker.push(self.create_memento())
        # 2. update history (what for?)
        self.history.append(deepcopy(self.board))
        piece.move_to(dest)

        # update player turn
        self.board.playing = "w" if piece.color == "b" else "b"

        # update en passant target square
        if piece.name != "Pawn":
            self.board.enpassant_target = "-"

        # update halfmove clock
        if self.history[-1][dest] is None and piece.name != "Pawn":
            self.board.halfmove_clock += 1
        else:
            self.board.halfmove_clock = 0

        # update fullmove number
        if piece.color == "b":
            self.board.fullmove_number += 1

        self.board.update_fen()

        if self.incheck(self.board.playing):
            raise Check()

    def undo(self):
        last_memento = self._care_taker.pop()
        self.set_memento(last_memento)

    def set_memento(self, memento):
        previous_state = pickle.loads(memento).get_state()
        vars(self).clear()
        vars(self).update(previous_state)

    def create_memento(self):
        memento = Memento(vars(self))
        return pickle.dumps(memento)
