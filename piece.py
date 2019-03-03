from copy import deepcopy
from error import ColorError, InvalidMove


class Piece(object):
    """ base class of chess pieces """

    def __init__(self, color):
        if color not in ["w", "b"]:
            raise ColorError(f"Unknown color: {color}")
        self.color = color  # which color white or black
        self.abbreviation = ""

    def __repr__(self):
        return self.abbreviation

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.__dict__ == other.__dict__
        elif isinstance(other, str):
            return other == self.abbreviation
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def name(self):
        return self.__class__.__name__

    def place_at(self, position, board=None):
        if board is not None:
            self.board = board
        self.board[position] = self
        self.position = position
        self.home = position

    def move_to(self, dest):
        if dest not in self.possible_moves():
            raise InvalidMove(
                f"{self.position} cannot move to {dest}, "
                f"possible moves are {self.possible_moves()}"
            )
        self.board[dest] = self
        self.board[self.position] = None
        self.position = dest

    def attacking_squares(self):
        return self.possible_moves()

    def possible_moves(self):
        raise NotImplementedError


class Pawn(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.abbreviation = "p" if color == "b" else "P"

    def possible_moves(self):
        moves = []
        sign = -1 if self.color == "w" else 1

        # standard move
        dest = self.board.destination(self.position, (sign, 0))
        if dest is not None:
            moves.append(dest)

            # moving two squares
            if self.position == self.home:
                dest = self.board.destination(self.position, (2 * sign, 0))
                if dest is not None:
                    moves.append(dest)

        # attacking moves
        dest_candidates = [
            self.board.destination(self.position, (sign, d)) for d in [-1, 1]
        ]
        for cand in dest_candidates:
            if cand is None:
                continue
            if self.board.isdifferentcolor(self.position, cand):
                moves.append(cand)
            if self.board.enpassant_target == cand:
                moves.append(cand)

        return moves

    def move_to(self, dest):
        # next en passant target square
        if self.position == self.home and dest[1] in ["4", "5"]:
            enpassant_target = self.home[0] + ("3" if dest[1] == "4" else "6")
        else:
            enpassant_target = "-"

        # move this piece
        super().move_to(dest)

        # promotion
        if self.position[1] in ["1", "8"]:
            queen = Queen(self.color)
            queen.place_at(self.position, self.board)
            del self

        # en passant capturing
        if dest == self.board.enpassant_target:
            sign = -1 if self.color == "w" else 1
            enemy_position = self.board.destination(dest, (-sign, 0))
            self.board[enemy_position] = None

        # update en passant target square
        self.board.enpassant_target = enpassant_target


class Knight(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.abbreviation = "n" if color == "b" else "N"

    def possible_moves(self):
        directions = [
            (-2, -1), (-2, 1),  # forward (from white's perspective)
            (-1, 2), (1, 2),    # right
            (2, 1), (2, -1),    # backward
            (1, -2), (-1, -2)   # left
        ]
        moves = [self.board.destination(self.position, d) for d in directions]
        return list(filter(None, moves))


class Bishop(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.abbreviation = "b" if color == "b" else "B"

    def possible_moves(self):
        directions = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
        moves = []

        for dir_ in directions:
            current = deepcopy(dir_)
            while True:
                dest = self.board.destination(self.position, current)
                if dest is None:
                    break
                moves.append(dest)
                if self.board.isdifferentcolor(self.position, dest):
                    break
                current = [x + y for x, y in zip(dir_, current)]
        return moves


class Rook(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.abbreviation = "r" if color == "b" else "R"

    def possible_moves(self):
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        moves = []

        for dir_ in directions:
            current = deepcopy(dir_)
            while True:
                dest = self.board.destination(self.position, current)
                if dest is None:
                    break
                moves.append(dest)
                if self.board.isdifferentcolor(self.position, dest):
                    break
                current = [x + y for x, y in zip(dir_, current)]
        return moves

    def move_to(self, dest):
        # erase castiling availability
        if self.color == "w":
            home_rank = "1"
            letters = ["K", "Q"]
        else:
            home_rank = "8"
            letters = ["k", "q"]
        if self.position == "h" + home_rank:
            self.board.castling = self.board.castling.replace(letters[0], "")
        elif self.position == "a" + home_rank:
            self.board.castling = self.board.castling.replace(letters[1], "")

        super().move_to(dest)


class Queen(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.abbreviation = "q" if color == "b" else "Q"

    def possible_moves(self):
        return Bishop.possible_moves(self) + Rook.possible_moves(self)


class King(Piece):

    def __init__(self, color):
        super().__init__(color)
        self.abbreviation = "k" if color == "b" else "K"

    def attacking_squares(self):
        directions = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1], [0, 1],
            [1, -1], [1, 0], [1, 1]
        ]
        squares = [self.board.destination(self.position, d) for d in directions]
        return list(filter(None, squares))

    def possible_moves(self):
        moves = []
        side = ("K", "Q") if self.color == "w" else ("k", "q")
        rank = "1" if self.color == "w" else "8"

        attacked_squares = self.board.attacked_squares(self.color)
        if self.position == self.home and self.home not in attacked_squares:
            if (
                    side[0] in self.board.castling
                    and self.board["f" + rank] is None and "f" + rank not in attacked_squares
                    and self.board["g" + rank] is None and "g" + rank not in attacked_squares
            ):
                moves.append("g" + rank)
            if (
                    side[1] in self.board.castling
                    and self.board["d" + rank] is None and "d" + rank not in attacked_squares
                    and self.board["c" + rank] is None and "c" + rank not in attacked_squares
                    and self.board["b" + rank] is None and "b" + rank not in attacked_squares
            ):
                moves.append("c" + rank)

        moves += self.attacking_squares()
        return moves

    def move_to(self, dest):
        if dest not in self.possible_moves():
            raise InvalidMove(
                f"{self.position} cannot move to {dest}, "
                f"possible moves are {self.possible_moves()}"
            )

        # castling
        if self.color == "w":
            home_rank = "1"
            table = str.maketrans({"K": "", "Q": ""})
        else:
            home_rank = "8"
            table = str.maketrans({"k": "", "q": ""})

        if self.position == self.home:
            # if king moved erase castling availability
            self.board.castling = self.board.castling.translate(table)

            if dest == "g" + home_rank:
                # king side castling, move rook
                self.board["h" + home_rank].move_to("f" + home_rank)
            elif dest == "c" + home_rank:
                # queen side castling, move rook
                self.board["a" + home_rank].move_to("d" + home_rank)

        self.board[dest] = self
        self.board[self.position] = None
        self.position = dest


