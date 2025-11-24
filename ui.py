import sys
import os


def __clear():
    """
    Clears the screen
    """
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        print('\033c')


def display_grid(grid):
    """
    Displays a grid including column numbers, ships, and horizontal lines.
    Appends an empty line.

    :grid: The grid as a two-dimensional array of rows and per-row column values,
           from left to right and bottom to top. True indicates a ship,
           None indicates an empty cell.
    """
    rows, cols = len(grid), len(grid[0])
    print('   ' + ''.join([f'{i:2d}  ' for i in range(1, cols + 1)]))  # Display column numbers

    # Horizontal line
    horizontal_line = '  +' + '---+' * cols

    for row in range(rows):
        row_symbols = ['0' if v else ' ' for v in grid[row]]
        print(horizontal_line)
        if row < 9:
            print(str(row + 1) + ' | ' + ' | '.join(row_symbols) + ' |')
        else:
            print(str(row + 1) + '| ' + ' | '.join(row_symbols) + ' |')

    print(horizontal_line)
    print('')


def display_game(gridA, gridB):
    """
    Displays the game, where the current grids of both players are placed side by side.
    Appends an empty line.

    :gridA: The grid of player_a as a two-dimensional array of rows and per-row column values,
            from top to bottom and left to right. False indicates a hit ship and is represented by an 'X'
            'miss' indicates the cell was empty and shot at and is represented by a '0'
            True and None are represented by ' ' (empty cell), they are intact ship cells and empty cells not yet hit.
    
    :gridB: The grid of player_b as a two-dimensional array of rows and per-row column values,
            from top to bottom and left to right. False indicates a hit ship and is represented by an 'X'
            'miss' indicates the cell was empty and shot at and is represented by a '0'
            True and None are represented by ' ' (empty cell), they are intact ship cells and empty cells not yet hit.
    """
    rows, cols = len(gridA), len(gridB[0])
    print('   ' + ''
          .join([f'{i:2d}  ' for i in range(1, cols + 1)])
          + '          ' + ''.join([f'{i:2d}  ' for i in range(1, cols + 1)]))  # Display column numbers

    # Horizontal line
    horizontal_line = '  +' + '---+' * cols + "   |   " + '  +' + '---+' * cols

    for row in range(rows):
        row_symbolsA = ['X' if v == False else '0' if v == 'miss' else ' ' for v in gridA[row]]
        row_symbolsB = ['X' if v == False else '0' if v == 'miss' else ' ' for v in gridB[row]]
        print(horizontal_line)
        if row < 9:
            print(str(row + 1) + ' | ' + ' | '.join(row_symbolsA) + ' |' + '   |   '
                  + str(row + 1) + ' | ' + ' | '.join(row_symbolsB) + ' |')
        else:
            print(str(row + 1) + '| ' + ' | '.join(row_symbolsA) + ' |' + '   |   '
                  + str(row + 1) + '| ' + ' | '.join(row_symbolsB) + ' |')

    print(horizontal_line)
    print('')


def display_headline(headline):
    """
    Displays a headline in uppercase. Clears the screen first and append an empty line.

    :headline: Headline string to display.
    """
    __clear()
    print(headline.upper(), '\n', sep='')


def display_menu(items):
    """
    Displays a menu item list.

    :items: Ordered list of menu items (strings).
    """
    display_message('\n'.join([f'{i + 1}. {item}' for i, item in enumerate(items)]))


def display_message(message):
    """
    Displays a message.

    :message: The message string to display.
    """
    print(message, '\n', sep='')


def display_scoreboard(scoreboard):
    """
    Displays the scoreboard in descending order.

    :scoreboard: The scoreboard as dictionary of player names and their scores as integers.
    """
    if len(scoreboard) == 0:
        display_message('no scores available')
    else:
        # Descendingly sorted list of bi-tuple (name, score)
        highscore = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
        display_message('\n'.join([f'{i + 1}. {name} ({score})' for i, (name, score) in enumerate(highscore)]))


def display_turn_start(player_name, is_player_a):
    """
    Display that a new turn starts with the name of the player who's turn it is and which board he needs to attack.
    Clears the screen first.

    :player_name: Name of the player.
    :is_player_a: Boolean that is true if the player is player A.
    """
    display_headline('Battleships')
    display_message(f"{player_name}, it is your turn! Attack the {'right' if is_player_a else 'left'} board.")


def prompt(message):
    """
    Displays a prompt with the provided message and waits for a line of user input on STDIN.

    :message: Message to show first.
    :return: String read from STDIN without tailing \n linefeed character.
    """
    return input(f'{message}: ').rstrip('\n')
