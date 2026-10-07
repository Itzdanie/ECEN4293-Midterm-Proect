"""Move lookup for the WeakC4 weak solution of Connect 4 (7x6).

The solution data in ``solution/`` comes from WeakC4 by 2swap
(https://github.com/2swap/WeakC4, GPL-3.0). The board helpers and the
steady-state query below are adapted from its ``validate_solution.py``.

The solution guarantees a win for the player who moves first (Red), provided
that player follows it from the first move. It says nothing about positions
reached after Red deviates, and it is of no use to the second player.

Boards are "grids": ``grid[y][x]`` with ``y = 0`` the bottom row and ``x = 0``
the left column. Cells hold ``EMPTY``, ``RED`` or ``YELLOW``. Columns are
0-based here; the solution files use 1-based column digits.
"""

import json
from pathlib import Path

ROWS, COLS = 6, 7
EMPTY, RED, YELLOW = 0, 1, 2
LEVELS = '0123456789'
SOLUTION_DIR = Path(__file__).resolve().parent / 'solution'

# Columns ordered from the center outwards, used when no book move applies.
CENTER_OUT = (3, 2, 4, 1, 5, 0, 6)


def grid_from_position(position):
    """Build a grid from a move string of 1-based columns, Red first."""
    grid = [[EMPTY] * COLS for _ in range(ROWS)]
    heights = [0] * COLS
    for ply, character in enumerate(position):
        col = int(character) - 1
        if not 0 <= col < COLS or heights[col] >= ROWS:
            raise ValueError(f'illegal position {position!r}')
        grid[heights[col]][col] = RED if ply % 2 == 0 else YELLOW
        heights[col] += 1
    return grid


def col_height(grid, col):
    """Number of pieces in a column."""
    for row in range(ROWS):
        if grid[row][col] == EMPTY:
            return row
    return ROWS


def playable_columns(grid):
    """Columns that still have room, left to right."""
    return [col for col in range(COLS) if grid[ROWS - 1][col] == EMPTY]


def makes_four(grid, col, row, player):
    """Whether the piece at (col, row) is part of four in a row."""
    for dcol, drow in ((1, 0), (0, 1), (1, 1), (1, -1)):
        count = 1
        for sign in (1, -1):
            ncol, nrow = col + sign * dcol, row + sign * drow
            while (0 <= ncol < COLS and 0 <= nrow < ROWS
                   and grid[nrow][ncol] == player):
                count += 1
                ncol += sign * dcol
                nrow += sign * drow
        if count >= 4:
            return True
    return False


def wins_at(grid, col, player):
    """Whether `player` wins by playing in `col` (the grid is unchanged)."""
    row = col_height(grid, col)
    if row >= ROWS:
        return False
    grid[row][col] = player
    won = makes_four(grid, col, row, player)
    grid[row][col] = EMPTY
    return won


def winning_column(grid, player):
    """First column where `player` wins immediately, or None."""
    for col in range(COLS):
        if wins_at(grid, col, player):
            return col
    return None


def grid_key(grid):
    """Hashable form of a grid."""
    return tuple(tuple(row) for row in grid)


def mirror_key(key):
    """Left-right mirror image of a grid key."""
    return tuple(row[::-1] for row in key)


def mirror_column(col):
    """Column index after a left-right mirror."""
    return COLS - 1 - col


def fallback_move(grid):
    """Win if possible, else block, else the most central open column.

    Used for positions the solution does not cover, and by the simple
    rule-based opponent. Assumes the mover is RED and the opponent YELLOW.
    """
    col = winning_column(grid, RED)
    if col is None:
        col = winning_column(grid, YELLOW)
    if col is None:
        col = next(c for c in CENTER_OUT if grid[ROWS - 1][c] == EMPTY)
    return col


def query_steady_state(grid, diagram):
    """Red's move from a steady-state diagram, or None if it gives none.

    Take a win, else block a loss, else scan the priority levels from 0 to 9
    and play the level's only playable cell. Levels with two or more playable
    cells cancel out and fall through to the next level.
    """
    for player in (RED, YELLOW):
        col = winning_column(grid, player)
        if col is not None:
            return col
    heights = [col_height(grid, col) for col in range(COLS)]
    for level in LEVELS:
        found = [col for col in range(COLS)
                 if heights[col] < ROWS
                 and diagram[ROWS - 1 - heights[col]][col] == level]
        if len(found) == 1:
            return found[0]
    return None


class WeakC4Book:
    """The WeakC4 solution, indexed by board for fast lookup."""

    def __init__(self, solution_dir=SOLUTION_DIR):
        solution_dir = Path(solution_dir)
        with open(solution_dir / 'branches.json') as file:
            branches = json.load(file)
        with open(solution_dir / 'steady_states.json') as file:
            self.diagrams = json.load(file)
        # Only one of each pair of mirror boards is stored, so index each
        # entry under its board and under the mirror image of that board.
        self._index = {}
        for position, value in branches.items():
            key = grid_key(grid_from_position(position))
            self._index[key] = (value, False)
            self._index.setdefault(mirror_key(key), (value, True))

    def __len__(self):
        return len(self._index)

    def step(self, grid, state=None):
        """Choose Red's move for a Red-to-move grid.

        `state` is None until the book reaches a steady-state diagram. From
        then on Red must keep following that same diagram for the rest of the
        game, because later positions are not in the book. A state is the
        tuple (diagram index, mirrored). Pass back the state returned by the
        previous call.

        Returns (column or None, new state). A column of None means the
        solution gives no move for this position.
        """
        if state is None:
            key = grid_key(grid)
            if key not in self._index:
                return None, None
            value, mirrored = self._index[key]
            if isinstance(value, str):
                col = int(value) - 1
                return (mirror_column(col) if mirrored else col), None
            state = (value, mirrored)
        index, mirrored = state
        if mirrored:
            grid = [row[::-1] for row in grid]
        col = query_steady_state(grid, self.diagrams[index])
        if col is not None and mirrored:
            col = mirror_column(col)
        return col, state

    def moves_to_win(self, grid, state):
        """Most Red moves needed to win from a Red-to-move grid.

        Follows the steady-state diagram in `state` against every possible
        Yellow reply and returns the worst case, counting Red's winning move.
        Raises ValueError if the diagram does not win from this position.
        """
        index, mirrored = state
        if mirrored:
            grid = [row[::-1] for row in grid]
        grid = [row[:] for row in grid]
        return _moves_to_win(grid, self.diagrams[index])


def _moves_to_win(grid, diagram):
    """Worst-case number of Red moves to win by following `diagram`."""
    memo = {}

    def red_turn(grid):
        key = grid_key(grid)
        if key in memo:
            return memo[key]
        col = query_steady_state(grid, diagram)
        if col is None or col_height(grid, col) >= ROWS:
            raise ValueError('the diagram gives no move here')
        row = col_height(grid, col)
        grid[row][col] = RED
        try:
            if makes_four(grid, col, row, RED):
                result = 1
            else:
                replies = playable_columns(grid)
                if not replies:
                    raise ValueError('the game ends in a draw')
                worst = 0
                for reply in replies:
                    reply_row = col_height(grid, reply)
                    grid[reply_row][reply] = YELLOW
                    try:
                        if makes_four(grid, reply, reply_row, YELLOW):
                            raise ValueError('Yellow wins')
                        worst = max(worst, red_turn(grid))
                    finally:
                        grid[reply_row][reply] = EMPTY
                result = 1 + worst
        finally:
            grid[row][col] = EMPTY
        memo[key] = result
        return result

    return red_turn(grid)
