"""Headless checks that the perfect bot wins as Player 1.

``python bot_vs_bot.py`` plays the bot against each Player 2 type.
``python bot_vs_bot.py --exhaustive`` additionally checks every possible
Player 2 reply sequence against the WeakC4 solution (takes a few minutes).
"""

import argparse
import contextlib
import io

import weakc4
from board import ConnectFourBoard
from player import CPUPlayer, PerfectPlayer, RuleBasedPlayer

RED_SYMBOL, YELLOW_SYMBOL = 'X', 'O'


def play_game(player_1, player_2):
    """Play one game on a fresh board; return (winner or None, move count)."""
    board = ConnectFourBoard(weakc4.ROWS, weakc4.COLS)
    players = (player_1, player_2)
    for turn in range(board.num_rows * board.num_cols):
        player = players[turn % 2]
        with contextlib.redirect_stdout(io.StringIO()):  # silence move text
            col = player.move(board=board)
        board.add_piece(col, player.symbol)
        if board.check_winner():
            return player, turn + 1
    return None, board.num_rows * board.num_cols


def make_opponent(kind, seed=None):
    """Build a Player 2 of the given kind: 'random' or 'rule'."""
    if kind == 'random':
        return CPUPlayer(symbol=YELLOW_SYMBOL, name='Random', seed=seed)
    return RuleBasedPlayer(symbol=YELLOW_SYMBOL, name='Rule-based')


def run_games(kind, games, seed=0):
    """Play `games` games of the perfect bot against an opponent kind.

    Returns (bot wins, list of move counts).
    """
    wins, lengths = 0, []
    for i in range(games):
        bot = PerfectPlayer(symbol=RED_SYMBOL, name='Perfect')
        winner, length = play_game(bot, make_opponent(kind, seed + i))
        wins += winner is bot
        lengths.append(length)
    return wins, lengths


def exhaustive_check(book=None):
    """Play the book against every Yellow reply; return the positions seen.

    Raises AssertionError if Red ever fails to win. Positions are memoized
    together with the diagram being followed, and the book is queried
    directly on grids for speed.
    """
    book = book or weakc4.WeakC4Book()
    solved = set()

    def red_turn(grid, state):
        key = (weakc4.grid_key(grid), state)
        if key in solved:
            return
        col, state = book.step(grid, state)
        if col is None:
            col = weakc4.fallback_move(grid)
        row = weakc4.col_height(grid, col)
        assert row < weakc4.ROWS, 'Red chose a full column'
        grid[row][col] = weakc4.RED
        try:
            if weakc4.makes_four(grid, col, row, weakc4.RED):
                solved.add(key)
                return
            replies = weakc4.playable_columns(grid)
            assert replies, 'draw reached'
            for reply in replies:
                ycol_row = weakc4.col_height(grid, reply)
                grid[ycol_row][reply] = weakc4.YELLOW
                try:
                    assert not weakc4.makes_four(
                        grid, reply, ycol_row, weakc4.YELLOW), 'Yellow won'
                    red_turn(grid, state)
                finally:
                    grid[ycol_row][reply] = weakc4.EMPTY
        finally:
            grid[row][col] = weakc4.EMPTY
        solved.add(key)

    red_turn([[weakc4.EMPTY] * weakc4.COLS for _ in range(weakc4.ROWS)], None)
    return len(solved)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--games', type=int, default=200,
                        help='games per opponent type (default 200)')
    parser.add_argument('--exhaustive', action='store_true',
                        help='check every Yellow reply sequence as well')
    args = parser.parse_args()

    for kind in ('random', 'rule'):
        wins, lengths = run_games(kind, args.games)
        print(f'Perfect bot vs {kind}: won {wins}/{args.games}, '
              f'game length min {min(lengths)}, max {max(lengths)}, '
              f'mean {sum(lengths) / len(lengths):.1f} plies')
    if args.exhaustive:
        print(f'Exhaustive: Red wins from {exhaustive_check()} positions')


if __name__ == '__main__':
    main()
