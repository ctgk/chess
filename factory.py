from piece import Pawn, Rook, Knight, Bishop, King, Queen


class PieceFactory:
    @staticmethod
    def factory(piece, color):
        piece = piece.lower()
        color = color.lower()
        color = 'w' if color == 'white' else 'b'

        if piece == 'pawn':
            return Pawn(color)

        elif piece == 'rook':
            return Rook(color)

        elif piece == 'knight':
            return Knight(color)

        elif piece == 'bishop':
            return Bishop(color)

        elif piece == 'queen':
            return Queen(color)

        elif piece == 'king':
            return King(color)
