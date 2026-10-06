_EMPTY = ' ' # Used to indicate empty spaces in the board

class InvalidMoveError(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ConnectFourBoard:

    """Represents a Connect 4 board. Handles board state and checks moves for validity."""

    def __init__(self, num_rows, num_cols):
        """Initialize a new board"""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.clear()

    def clear(self):
        """Replace all pieces with empty spaces."""
        self.rows = list()
        for row in range(self.num_rows):
            self.rows.append([_EMPTY for col in range(self.num_cols)])

    def display(self):
        """Display the current board state"""
        for row in range(self.num_rows):
            print(f'\t|{"|".join(self.rows[row])}|')
        print('\t ' + ' '.join([str(col) for col in range(self.num_cols)]))

    def check_winner(self):
        """Check whether someone has won the game."""
        # Directions to scan from each cell: right, down, down-right, down-left
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                symbol = self.rows[row][col]
                if symbol == _EMPTY:
                    continue
                for drow, dcol in directions:
                    # Does a run of 4 matching symbols start here in this direction?
                    if all(0 <= row + drow * i < self.num_rows
                           and 0 <= col + dcol * i < self.num_cols
                           and self.rows[row + drow * i][col + dcol * i] == symbol
                           for i in range(4)):
                        return True
        return False

    def is_full(self):
        """Check whether the board is full."""
        return all(_EMPTY not in row for row in self.rows)

    def add_piece(self, col, symbol):
        """Add a piece to the specified column."""
        # Check that the move is valid
        if not 0 <= col < self.num_cols:
            raise InvalidMoveError(f'Column {col} is not on the board.')
        if self.rows[0][col] != _EMPTY:
            raise InvalidMoveError(f'Column {col} is already full.')

        # Find the first empty row in col and replace it with symbol
        for row in reversed(range(self.num_rows)):
            if self.rows[row][col] == _EMPTY:
                self.rows[row][col] = symbol
                break
