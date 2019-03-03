import tkinter as tk
from PIL import Image, ImageTk

from command import Invoker, ConcreteCommand
from error import Check, InvalidMove, InvalidPiece, NotYourTurn


class GUI(tk.Frame):

    rows = 8
    columns = 8
    original_img_size = (100, 100)
    icon_size = (32, 32)
    files = ["a", "b", "c", "d", "e", "f", "g", "h"]
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
    light_color = "#FFDEAD"
    dark_color = "#CD853F"
    icon_path = {
        "k": "img/black_king.png",
        "q": "img/black_queen.png",
        "r": "img/black_rook.png",
        "n": "img/black_knight.png",
        "b": "img/black_bishop.png",
        "p": "img/black_pawn.png",
        "K": "img/white_king.png",
        "Q": "img/white_queen.png",
        "R": "img/white_rook.png",
        "N": "img/white_knight.png",
        "B": "img/white_bishop.png",
        "P": "img/white_pawn.png"
    }

    def __init__(self, master, chess, square_length=64):
        super().__init__(master)
        self._invoker = Invoker()
        self.chess = chess
        self.square_length = square_length
        self.selected = None
        self.highlighted = [
            [False for _ in range(self.columns)] for _ in range(self.rows)
        ]
        self.master = master

        # create canvas
        canvas_width = self.columns * square_length
        canvas_height = self.rows * square_length
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.pack(side="top", fill="both", anchor="c", expand=True)

        self.statusbar = tk.Frame(self, height=64)

        self.button_quit = tk.Button(self, text="Quit", fg="black", command=self.master.destroy)
        self.button_quit.pack(side=tk.RIGHT, in_=self.statusbar)

        self.button_reset = tk.Button(self, text="Restart", fg="black", command=self.restart)
        self.button_reset.pack(side=tk.RIGHT, in_=self.statusbar)

        self.button_undo = tk.Button(self, text="Undo", fg="black", command=self.undo)
        self.button_undo.pack(side=tk.RIGHT, in_=self.statusbar)

        self.label_status = tk.Label(self.statusbar, text="White's turn", fg="black")
        self.label_status.pack(side=tk.LEFT, expand=0, in_=self.statusbar)

        self.statusbar.pack(expand=False, fill="x", side='bottom')

        # create icons
        light_bg = Image.new("RGBA", self.original_img_size, self.light_color)
        dark_bg = Image.new("RGBA", self.original_img_size, self.dark_color)
        highlight_bg = Image.new("RGBA", self.original_img_size, "yellow")
        self.icons = {}
        for key, path in self.icon_path.items():
            img = Image.open(path)
            light_img = Image.alpha_composite(light_bg, img)
            light_img = light_img.resize(self.icon_size).convert("RGB")
            self.icons[self.light_color + key] = ImageTk.PhotoImage(light_img)
            dark_img = Image.alpha_composite(dark_bg, img)
            dark_img = dark_img.resize(self.icon_size).convert("RGB")
            self.icons[self.dark_color + key] = ImageTk.PhotoImage(dark_img)
            highlight_img = Image.alpha_composite(highlight_bg, img)
            highlight_img = highlight_img.resize(self.icon_size).convert("RGB")
            self.icons["yellow" + key] = ImageTk.PhotoImage(highlight_img)

    def coords2notation(self, row, col):
        return self.files[col] + self.ranks[row]

    def refresh(self, event=None):
        """
        redraw board
        """

        if event:
            xsize = int((event.width - 1) / self.columns)
            ysize = int((event.height - 1) / self.rows)
            self.square_length = min(xsize, ysize)

        # delete the previous images
        self.canvas.delete("square")
        self.canvas.delete("piece")

        # draw board
        # the color of the top left square is light
        color = self.light_color
        for row in range(self.rows):
            # exchange square color
            if color == self.dark_color:
                color = self.light_color
            else:
                color = self.dark_color

            for col in range(self.columns):
                # exchange square color
                if color == self.dark_color:
                    color = self.light_color
                else:
                    color = self.dark_color

                # define coordinates of top left and bottom right of a square
                x1 = col * self.square_length
                x2 = x1 + self.square_length
                y1 = row * self.square_length
                y2 = y1 + self.square_length

                # draw a light or dark square
                if self.highlighted[row][col]:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="black", fill="yellow", tags="square"
                    )
                    filled_color = "yellow"
                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="black", fill=color, tags="square"
                    )
                    filled_color = color

                # draw a piece
                piece = self.chess.board[self.coords2notation(row, col)]
                if piece is not None:
                    self.canvas.create_image(
                        ((x1 + x2) // 2, (y1 + y2) // 2),
                        image=self.icons[filled_color + repr(piece)],
                        tags=(repr(piece), "piece")
                    )

    def click(self, event):
        # selected square
        col = event.x // self.square_length
        row = event.y // self.square_length
        if (not -1 < col < self.columns) or (not -1 < row < self.rows):
            return 0

        if self.selected is not None:
            try:
                self.move(self.selected, (row, col))
            except Check as err:
                self.highlighted = [
                    [False for _ in range(self.columns)] for _ in range(self.rows)
                ]
                self.highlighted[self.selected[0]][self.selected[1]] = True
                self.highlighted[row][col] = True
                self.selected = None
                self.label_status["text"] = err.__class__.__name__
            except (InvalidPiece, NotYourTurn, InvalidMove) as err:
                self.highlighted[self.selected[0]][self.selected[1]] = False
                self.selected = None
                self.label_status["text"] = err.__class__.__name__
            else:
                self.highlighted = [
                    [False for _ in range(self.columns)] for _ in range(self.rows)
                ]
                self.highlighted[self.selected[0]][self.selected[1]] = True
                self.highlighted[row][col] = True
                self.selected = None
                if self.chess.board.playing == "w":
                    self.label_status["text"] = "White's turn"
                else:
                    self.label_status["text"] = "Black's turn"
        else:
            self.highlight(row, col)

        self.refresh()

    def highlight(self, row, col):
        notation = self.coords2notation(row, col)
        piece = self.chess.board[notation]
        if piece is not None and piece.color == self.chess.board.playing:
            self.highlighted[row][col] = True
            self.selected = (row, col)

    def move(self, origin, destination):
        if isinstance(origin, tuple):
            origin = self.coords2notation(*origin)
        if isinstance(destination, tuple):
            destination = self.coords2notation(*destination)
        self.chess.move(origin, destination)

    def restart(self):
        self.chess.restart()
        self.selected = None
        self.highlighted = [
            [False for _ in range(self.columns)] for _ in range(self.rows)
        ]
        self.label_status["text"] = "White's turn"
        self.refresh()

    def undo(self):
        try:
            command = ConcreteCommand(self.chess.undo)
            self._invoker.store_command(command)
            self._invoker.execute_commands()
            self.highlighted = [
                [False for _ in range(self.columns)] for _ in range(self.rows)
            ]
            self.refresh()
        except InvalidMove as err:
            self.label_status["text"] = err.__class__.__name__
        except NotImplementedError:
            self.label_status['text'] = "InvalidOperation"
