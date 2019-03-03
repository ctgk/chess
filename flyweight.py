from factory import PieceFactory
from error import InvalidPiece

# alias for convenience
factory = PieceFactory.factory


class Flyweight(object):
    def __init__(self, cls):
        self._cls = cls
        self._instances = dict()

    def __call__(self, *args, **kargs):
        return self._instances.setdefault(
                                    (args, tuple(kargs.items())),
                                    self._cls(*args, **kargs))


@Flyweight
class PieceCreator:
    white_pawn_c = 0
    white_rook_c = 0
    white_knight_c = 0
    white_bishop_c = 0

    black_pawn_c = 0
    black_rook_c = 0
    black_knight_c = 0
    black_bishop_c = 0

    def __init__(self):
        self.white_pawns = [factory('pawn', 'white') for _ in range(8)]
        self.white_rooks = [factory('rook', 'white') for _ in range(2)]
        self.white_knights = [factory('knight', 'white') for _ in range(2)]
        self.white_bishops = [factory('bishop', 'white') for _ in range(2)]
        self.white_queen = factory('queen', 'white')
        self.white_king = factory('king', 'white')

        self.black_pawns = [factory('pawn', 'black') for _ in range(8)]
        self.black_rooks = [factory('rook', 'black') for _ in range(2)]
        self.black_knights = [factory('knight', 'black') for _ in range(2)]
        self.black_bishops = [factory('bishop', 'black') for _ in range(2)]
        self.black_queen = factory('queen', 'black')
        self.black_king = factory('king', 'black')

    def __call__(self, item, *args, **kwargs):
        if item == "-":
            return None

        elif item == "P":
            hold = self.white_pawns[self.white_pawn_c]
            self.white_pawn_c += 1
            if self.white_pawn_c == 8:
                self.white_pawn_c = 0
            return hold

        elif item == "p":
            hold = self.black_pawns[self.black_pawn_c]
            self.black_pawn_c += 1
            if self.black_pawn_c == 8:
                self.black_pawn_c = 0
            return hold

        elif item == "R":
            hold = self.white_rooks[self.white_rook_c]
            self.white_rook_c += 1
            if self.white_rook_c == 2:
                self.white_rook_c = 0
            return hold

        elif item == "r":
            hold = self.black_rooks[self.black_rook_c]
            self.black_rook_c += 1
            if self.black_rook_c == 2:
                self.black_rook_c = 0
            return hold

        elif item == "N":
            hold = self.white_knights[self.white_knight_c]
            self.white_knight_c += 1
            if self.white_knight_c == 2:
                self.white_knight_c = 0
            return hold

        elif item == "n":
            hold = self.black_knights[self.black_knight_c]
            self.black_knight_c += 1
            if self.black_knight_c == 2:
                self.black_knight_c = 0
            return hold

        elif item == "B":
            hold = self.white_bishops[self.white_bishop_c]
            self.white_bishop_c += 1
            if self.white_bishop_c == 2:
                self.white_bishop_c = 0
            return hold

        elif item == "b":
            hold = self.black_bishops[self.black_bishop_c]
            self.black_bishop_c += 1
            if self.black_bishop_c == 2:
                self.black_bishop_c = 0
            return hold

        elif item == 'Q':
            return self.white_queen

        elif item == 'q':
            return self.black_queen

        elif item == 'K':
            return self.white_king

        elif item == 'k':
            return self.black_king

        else:
            raise InvalidPiece(f"Unknown piece: {item}")
