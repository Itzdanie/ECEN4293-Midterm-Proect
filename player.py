import random
from abc import ABC, abstractmethod

from board import _EMPTY


class AbstractPlayer(ABC):
    def __init__(self, symbol, name, view=None):
        self.name = name
        self.symbol = symbol
        self.view = view  # Optional MatplotlibBoardView, used by players that need one

    @abstractmethod
    def move(self, **kwargs):
        """Return an integer representing the column where the player intends to play a piece."""


class ConsolePlayer(AbstractPlayer):
    def move(self, **kwargs):
        """Get which column to play in from the user via text console"""
        return int(input('Enter which column to play in: '))


class CPUPlayer(AbstractPlayer):
    """A player that picks its own moves, with no user intervention."""

    def move(self, board=None, **kwargs):
        """Choose a random column that still has an open space."""
        if board is None:
            raise ValueError('CPUPlayer.move needs a board to choose from.')
        open_cols = [col for col in range(board.num_cols)
                     if board.rows[0][col] is _EMPTY]
        col = random.choice(open_cols)
        print(f'{self.name} plays in column {col}.')
        return col


class MatplotlibPlayer(AbstractPlayer):
    """A player that picks a column by clicking on it in a matplotlib window."""

    def move(self, board=None, **kwargs):
        """Wait for the player to click a column in the matplotlib window."""
        if self.view is None:
            raise ValueError('MatplotlibPlayer.move needs a view to interact with.')
        return self.view.get_column_click(
            status_text=f"{self.name}'s turn (playing '{self.symbol}')")
