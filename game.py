from board import ConnectFourBoard, InvalidMoveError
from player import ConsolePlayer, MatplotlibPlayer, PerfectPlayer


class ConnectFourGame:
    """Represents a Connect 4 game. Manages board and players."""

    def __init__(self, rows=6, cols=7, p1_type=ConsolePlayer,
                 p2_type=ConsolePlayer, display_mode='console'):
        """Initialize a new game"""

        self.display_mode = display_mode

        # Set up board
        self.board = ConnectFourBoard(rows, cols)

        # Set up the board view. In matplotlib mode, human players also need
        # the view so they can pick their moves by clicking on it.
        if display_mode == 'matplotlib':
            from matplotlib_view import MatplotlibBoardView
            self.view = MatplotlibBoardView(self.board)
            if p1_type is ConsolePlayer:
                p1_type = MatplotlibPlayer
            if p2_type is ConsolePlayer:
                p2_type = MatplotlibPlayer
        else:
            self.view = None

        if self.view is not None:
            print('A game window has opened. Answer the symbol prompts '
                  'here in the terminal to start.')

        # Set up Players
        p1_name = 'CPU 1' if p1_type.is_bot else 'Player 1'
        p2_name = 'CPU 2' if p2_type.is_bot else 'Player 2'
        p1_symbol = self.get_player_symbol(p1_name)
        p2_symbol = self.get_player_symbol(p2_name)
        while p2_symbol == p1_symbol:
            print(f"{p2_name} can't have the same symbol as {p1_name}!")
            p2_symbol = self.get_player_symbol(p2_name)
        self.player_1 = p1_type(name=p1_name, symbol=p1_symbol, view=self.view)
        self.player_2 = p2_type(name=p2_name, symbol=p2_symbol, view=self.view)

        self.turn = 0
        self.note = ''  # latest status note from a player, if it has one

    def start(self):
        """Begin playing a new game.

        Players take turns until either someone wins or the board is full."""

        # Clear the board and make Player 1 move first again
        self.board.clear()
        self.turn = 0
        self.note = ''
        if self.view is not None:
            self.view.note = ''

        # Main game loop
        while not self.board.is_full():
            # Figure out whose turn it is
            match self.turn % 2:
                case 0:
                    current_player = self.player_1
                case 1:
                    current_player = self.player_2
            print(f"{current_player.name}'s turn.")

            # Display the board
            status_text = (f"{current_player.name}'s turn "
                           f"(playing '{current_player.symbol}')")
            self.display(status_text=status_text)

            # Get the next player's move
            move_is_invalid = True
            # Keep trying until we get a valid move
            while move_is_invalid:
                col = current_player.move(board=self.board)
                try:
                    self.board.add_piece(col, current_player.symbol)
                    # If we make it to this line, move was valid
                    move_is_invalid = False
                except InvalidMoveError as err:
                    # Otherwise display why the move was not valid
                    print(err.message)
                    if self.view is not None:
                        self.view.draw(status_text=err.message)

            # Show any note the player has about its position
            note = getattr(current_player, 'status_note', '')
            if note:
                self.note = note
                if self.view is not None:
                    # Only steady state is shown in the window, and it stays
                    # up on human turns too
                    steady = getattr(current_player, 'in_steady_state', False)
                    self.view.note = note if steady else ''
                print(note)

            # Increment the turn count
            self.turn += 1

            # Check for winners
            if self.board.check_winner():
                print(f'{current_player.name} wins!')
                self.display(status_text=f'{current_player.name} wins!')
                # Get out of the while loop without triggering the else clause
                break
        else:
            # If we reach this line, the board is full
            print('No winner!')
            self.display(status_text='No winner!')

    def display(self, status_text=None):
        """Show the current board state in the active display mode."""
        if self.view is not None:
            self.view.draw(status_text=status_text)
        else:
            self.board.display()

    def get_player_symbol(self, player_name):
        """Request a valid symbol to use for a player."""
        symbol_is_invalid = True
        while symbol_is_invalid:
            symbol = input(
                f'Enter a character to use as a symbol for {player_name}: ')
            symbol = symbol.strip()  # Remove leading and trailing whitespace
            if not symbol:
                print('Symbol must not be a whitespace character!')
            else:
                symbol = symbol[0]  # Only keep the first character
                # Get positive confirmation from the player
                confirmation = input(
                    f'Use "{symbol}" for {player_name}? (y/N): ')
                symbol_is_invalid = not confirmation.lower().startswith('y')
        return symbol


if __name__ == "__main__":
    # Let the user pick the game mode
    print('Connect 4')
    print('  1) Single-player (you play second against the perfect CPU)')
    print('  2) Two-player')
    mode = ''
    while mode not in ('1', '2'):
        mode = input('Select a game mode (1/2): ').strip()
    p1_type = PerfectPlayer if mode == '1' else ConsolePlayer

    # Let the user pick how the board should be displayed
    print('Display mode')
    print('  1) Console')
    print('  2) Matplotlib window')
    display_choice = ''
    while display_choice not in ('1', '2'):
        display_choice = input('Select a display mode (1/2): ').strip()
    display_mode = 'matplotlib' if display_choice == '2' else 'console'

    # Play a new connect 4 game
    game = ConnectFourGame(p1_type=p1_type, display_mode=display_mode)

    keep_playing = True
    while keep_playing:
        game.start()
        keep_playing = input('Play again? (y/N): ').lower().startswith('y')

    if game.view is not None:
        game.view.close()
