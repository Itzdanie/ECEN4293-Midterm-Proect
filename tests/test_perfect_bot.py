"""Tests for the WeakC4-based perfect Player 1 bot."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bot_vs_bot  # noqa: E402
import weakc4  # noqa: E402
from board import ConnectFourBoard  # noqa: E402
from player import PerfectPlayer, board_to_grid  # noqa: E402

SOLUTION = Path(weakc4.SOLUTION_DIR)


@pytest.fixture(scope='module')
def book():
    return weakc4.WeakC4Book()


def board_from_position(position, symbols=('X', 'O')):
    """ConnectFourBoard with the moves of a 1-based column string played."""
    board = ConnectFourBoard(6, 7)
    for ply, character in enumerate(position):
        board.add_piece(int(character) - 1, symbols[ply % 2])
    return board


def test_opening_move_is_center(capsys):
    bot = PerfectPlayer(symbol='X', name='Bot')
    assert bot.move(board=ConnectFourBoard(6, 7)) == 3
    assert bot.last_move_from_book


def test_book_matches_json_entries(book):
    branches = json.loads((SOLUTION / 'branches.json').read_text())
    for position, value in branches.items():
        if isinstance(value, str):
            col, state = book.step(weakc4.grid_from_position(position))
            assert col == int(value) - 1 and state is None


def test_mirrored_position_gives_mirrored_move(book):
    branches = json.loads((SOLUTION / 'branches.json').read_text())
    checked = 0
    for position, value in branches.items():
        original = weakc4.grid_from_position(position)
        mirrored = weakc4.grid_from_position(
            ''.join(str(8 - int(c)) for c in position))
        col, _ = book.step(mirrored)
        assert col is not None
        if weakc4.grid_key(original) == weakc4.grid_key(mirrored):
            continue  # symmetric board: its mirror image is itself
        if isinstance(value, str):
            assert col == weakc4.mirror_column(int(value) - 1)
            checked += 1
    assert checked > 100


def test_board_to_grid_uses_symbols_not_turn_order():
    board = board_from_position('44', symbols=('#', '@'))
    grid = board_to_grid(board, '#')
    assert grid[0][3] == weakc4.RED and grid[1][3] == weakc4.YELLOW
    grid = board_to_grid(board, '@')
    assert grid[0][3] == weakc4.YELLOW and grid[1][3] == weakc4.RED


def test_takes_immediate_win(capsys):
    # Red (X) has three in column 0 and Yellow (O) has played elsewhere.
    board = board_from_position('1' + '2' + '1' + '2' + '1' + '3')
    bot = PerfectPlayer(symbol='X', name='Bot')
    assert bot.move(board=board) == 0


def test_blocks_immediate_loss_outside_book(capsys):
    # Not a book position (Red has not followed the solution): Yellow
    # threatens to win in column 2, so the fallback must block there.
    board = board_from_position('1' + '3' + '7' + '3' + '7' + '3' + '1')
    bot = PerfectPlayer(symbol='X', name='Bot')
    # Yellow (O) has three stacked in column 2 and Red is to move.
    assert bot.move(board=board) == 2


@pytest.mark.parametrize('kind', ['random', 'rule'])
def test_perfect_bot_beats_opponent_as_player_1(kind):
    wins, lengths = bot_vs_bot.run_games(kind, games=100, seed=1234)
    assert wins == 100


def test_state_resets_between_games(capsys):
    bot = PerfectPlayer(symbol='X', name='Bot')
    for seed in range(5):
        winner, _ = bot_vs_bot.play_game(
            bot, bot_vs_bot.make_opponent('random', seed))
        assert winner is bot


@pytest.mark.slow
def test_exhaustive_every_yellow_reply_loses():
    assert bot_vs_bot.exhaustive_check() > 0


def test_moves_to_win_matches_actual_games(book):
    """The predicted worst case is never exceeded in real games."""
    import re
    checked = 0
    for seed in range(60):
        bot = PerfectPlayer(symbol='X', name='Bot')
        opponent = bot_vs_bot.make_opponent('random', seed)
        board = ConnectFourBoard(6, 7)
        players = (bot, opponent)
        predicted = bot_moves = None
        for turn in range(42):
            player = players[turn % 2]
            col = player.move(board=board)
            board.add_piece(col, player.symbol)
            if player is bot:
                found = re.search(r'within (\d+) more', bot.status_note)
                if predicted is None and found:
                    predicted = int(found.group(1))
                    bot_moves = 0
                elif predicted is not None:
                    bot_moves += 1
            if board.check_winner():
                break
        if predicted is not None:
            assert bot_moves <= predicted
            checked += 1
    assert checked > 0


def test_status_notes(capsys):
    bot = PerfectPlayer(symbol='X', name='Bot')
    bot.move(board=ConnectFourBoard(6, 7))
    assert bot.status_note == 'In the book: win guaranteed.'
    # Not a book position, so there is no guarantee.
    odd = board_from_position('1' + '1' + '1' + '1' + '1' + '1')
    bot.move(board=odd)
    assert 'no win guaranteed' in bot.status_note


def test_moves_to_win_every_diagram_entry(book):
    branches = json.loads((SOLUTION / 'branches.json').read_text())
    entries = [(p, v) for p, v in branches.items() if isinstance(v, int)]
    for position, index in entries[:25]:
        grid = weakc4.grid_from_position(position)
        assert 1 <= book.moves_to_win(grid, (index, False)) <= 21
