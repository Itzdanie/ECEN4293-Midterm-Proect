import matplotlib.pyplot as plt

from board import _EMPTY


class MatplotlibBoardView:
    """Draws a ConnectFourBoard as a simple grid in a matplotlib window and
    lets players pick a column by clicking on it."""

    def __init__(self, board):
        self.board = board
        self.selected_col = None
        self.closed = False

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        self.fig.canvas.mpl_connect('close_event', self._on_close)

        self.draw()

    def draw(self, status_text=None):
        """Redraw the current board state, with an optional status message."""
        if self.closed:
            return

        board = self.board
        self.ax.clear()

        # Draw the grid lines
        for col in range(board.num_cols + 1):
            self.ax.axvline(col, color='black')
        for row in range(board.num_rows + 1):
            self.ax.axhline(row, color='black')

        # Draw each player's symbol in its cell
        for row in range(board.num_rows):
            for col in range(board.num_cols):
                symbol = board.rows[row][col]
                if symbol is not _EMPTY:
                    y = board.num_rows - row - 0.5  # flip so row 0 is drawn at the top
                    self.ax.text(col + 0.5, y, symbol, ha='center', va='center', fontsize=20)

        self.ax.set_xlim(0, board.num_cols)
        self.ax.set_ylim(0, board.num_rows)
        self.ax.set_xticks([col + 0.5 for col in range(board.num_cols)])
        self.ax.set_xticklabels(range(board.num_cols))
        self.ax.set_yticks([])
        self.ax.set_xlabel('Click a column above to drop a piece there.')
        if status_text:
            self.ax.set_title(status_text)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def _on_click(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return
        col = int(event.xdata)
        if 0 <= col < self.board.num_cols:
            self.selected_col = col

    def _on_close(self, event):
        self.closed = True

    def get_column_click(self, status_text):
        """Block until the player clicks a valid column, then return its index."""
        self.selected_col = None
        self.draw(status_text=status_text)
        while self.selected_col is None:
            if self.closed:
                raise SystemExit('The game window was closed.')
            plt.pause(0.05)
        return self.selected_col

    def close(self):
        if not self.closed:
            plt.close(self.fig)
            self.closed = True
