import random
from abc import ABC, abstractmethod

import weakc4
from board import _EMPTY


def board_to_grid(board, my_symbol):
    """Convert a ConnectFourBoard to a WeakC4 grid, with my_symbol as RED.

    Any other non-empty symbol is treated as the opponent (YELLOW).
    """
    grid = []
    for row in reversed(board.rows):  # WeakC4 grids start at the bottom row
        grid.append([weakc4.EMPTY if cell == _EMPTY
                     else weakc4.RED if cell == my_symbol
                     else weakc4.YELLOW
                     for cell in row])
    return grid


class AbstractPlayer(ABC):
    is_bot = False  # True for players that choose their own moves

    def __init__(self, symbol, name, view=None):
        self.name = name
        self.symbol = symbol
        # Optional MatplotlibBoardView, used by players that need one
        self.view = view

    @abstractmethod
    def move(self, **kwargs):
        """Return the column (an integer) where the player will play."""


class ConsolePlayer(AbstractPlayer):
    def move(self, **kwargs):
        """Get which column to play in from the user via text console"""
        return int(input('Enter which column to play in: '))


class CPUPlayer(AbstractPlayer):
    """A player that picks its own moves, with no user intervention."""

    is_bot = True

    def __init__(self, *args, seed=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rng = random.Random(seed)  # a seed makes games reproducible

    def move(self, board=None, **kwargs):
        """Choose a random column that still has an open space."""
        if board is None:
            raise ValueError('CPUPlayer.move needs a board to choose from.')
        open_cols = [col for col in range(board.num_cols)
                     if board.rows[0][col] == _EMPTY]
        col = self.rng.choice(open_cols)
        print(f'{self.name} plays in column {col}.')
        return col


class RuleBasedPlayer(AbstractPlayer):
    """Takes a win, else blocks a loss, else plays the most central column."""

    is_bot = True

    def move(self, board=None, **kwargs):
        if board is None:
            raise ValueError('RuleBasedPlayer.move needs a board.')
        col = weakc4.fallback_move(board_to_grid(board, self.symbol))
        print(f'{self.name} plays in column {col}.')
        return col


class PerfectPlayer(AbstractPlayer):
    """Player 1 bot that always wins, using the WeakC4 solution.

    The guarantee only holds when this player moves first and has made every
    move itself. In any position the solution does not cover, it falls back
    to taking a win, blocking a loss, or playing the most central column.
    """

    is_bot = True
    _book = None  # loaded once and shared by all instances

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_move_from_book = None  # for tests and reporting
        self._state = None  # steady-state diagram being followed, if any

    @classmethod
    def book(cls):
        if cls._book is None:
            cls._book = weakc4.WeakC4Book()
        return cls._book

    def move(self, board=None, **kwargs):
        if board is None:
            raise ValueError('PerfectPlayer.move needs a board.')
        grid = board_to_grid(board, self.symbol)
        if not any(weakc4.EMPTY != cell for row in grid for cell in row):
            self._state = None  # empty board: a new game has started
        col, self._state = self.book().step(grid, self._state)
        self.last_move_from_book = col is not None
        if col is None:
            col = weakc4.fallback_move(grid)
        print(f'{self.name} plays in column {col}.')
        return col


class MatplotlibPlayer(AbstractPlayer):
    """A player that picks a column by clicking it in a matplotlib window."""

    def move(self, board=None, **kwargs):
        """Wait for the player to click a column in the matplotlib window."""
        if self.view is None:
            raise ValueError(
                'MatplotlibPlayer.move needs a view to interact with.')
        return self.view.get_column_click(
            status_text=f"{self.name}'s turn (playing '{self.symbol}')")
