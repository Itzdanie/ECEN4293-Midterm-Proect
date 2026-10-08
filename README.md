# Connect 4 with a perfect Player 1 bot

ECEN 4293 midterm. Extends the Lab 2 Connect 4 game (7x6) with a CPU player
that, moving first, always wins.

## How it works

The bot uses the WeakC4 weak solution of Connect 4 (see Credits). The
solution is a small book of positions plus 481 "steady state" diagrams, and
choosing a move needs no search. It only guarantees a win for the player who
moves first and follows it from move 1. It cannot help the second player, so
the perfect bot is always Player 1. It wins, but not necessarily quickly.

- `weakc4.py`: book lookup, mirror handling and diagram queries.
- `player.py`: `PerfectPlayer` (WeakC4), `RuleBasedPlayer` (win, block,
  then center, or a random open column when given a `seed`) and
  `CPUPlayer` (random, optional `seed`) alongside the Lab 2 players.
- Status notes: while you play, the console prints after each bot move
  whether the bot is still in the book, has left it, or has reached a
  steady state with a forced win within N more bot moves. The game window
  shows only the steady-state note. It appears once the bot reaches a
  steady state and stays up for the rest of the game, including your turns.
- `bot_vs_bot.py`: headless games, an exhaustive check, and `--show`, which
  plays one game in a window.
- `solution/`: WeakC4 data, see `solution/SOURCE.md`.

## Usage

```
python game.py                      # play second against the perfect bot
python bot_vs_bot.py                # bot vs random and rule-based opponents
python bot_vs_bot.py --exhaustive   # every Yellow reply sequence
python bot_vs_bot.py --show         # watch the bot play a random rule-based bot
python bot_vs_bot.py --show --seed 42   # replay a specific game
python -m pytest -m "not slow"      # quick tests
python -m pytest                    # includes the exhaustive test
python -m pycodestyle . --exclude=solution   # PEP 8 check
```

`--show` picks a random seed for the rule-based opponent, which plays a
random open column whenever it has no win or block, so every game differs.
The seed is printed as `Game seed: N`; pass it back with `--seed N` to
replay that game. The window stays open after the game until you close it.

## Credits and license

The solution data and `validate_solution.py` come from
[WeakC4](https://github.com/2swap/WeakC4) by 2swap, with contributions from
dave-zyx and Waffle3z, and are licensed under GPL-3.0. This project is
therefore distributed under GPL-3.0 as well (see `LICENSE`).
