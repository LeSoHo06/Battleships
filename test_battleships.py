import os
import re
import time
from unittest.mock import Mock

from battleships import *

SCOREBOARD_FILE = 'scoreboard.dat'

PLACEMENT_INPUT = ["1 1, 1 2", "1 1, 1 2"]


def remove_file(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def normalize_output(output):
    return re.sub(r"[^a-z0-9]", "", output.lower())


def mock_ui_fn(monkeypatch, function, return_values=None):
    params = []

    def record_params(param):
        params.append(param.copy() if type(param) == dict else param)
        if return_values is not None:
            if len(return_values) < len(params):
                raise RuntimeError(f'{function} called too many times')
            else:
                return return_values[len(params) - 1]

    monkeypatch.setattr(ui, function, record_params)
    return params


def assert_interaction(monkeypatch, capfd, subject, expected_output, inputs=None, output_exact=True, input_exact=True):
    if inputs is None:
        inputs = []
    stdin = STDIN(inputs)
    monkeypatch.setattr('sys.stdin', stdin)
    subject()
    stdout, stderr = capfd.readouterr()

    normalized_expected_output = normalize_output(expected_output)
    normalized_stdout = normalize_output(stdout)

    if output_exact:
        assert normalized_stdout == normalized_expected_output
    else:
        assert (normalized_expected_output in normalized_stdout) == True
    assert stderr == ''
    if input_exact:
        assert stdin.done()  # Check that all inputs were read


class STDIN:
    def __init__(self, values):
        self.values = list(reversed(values))

    def readline(self):
        if not self.values:
            raise Exception('Too many reads from STDIN')
        return self.values.pop() + '\n'

    def done(self):
        return not self.values


def grid_empty(cols, rows) -> list:
    return [[None] * rows for _ in range(cols)]


def grid_draw(cols, rows):
    return [[(row // 2 + col) % 2 == 0 for row in range(rows)] for col in range(cols)]


###############################################################################
### MAIN
###############################################################################

def mock_menu_end_with_exit(monkeypatch, menu_choices=None):
    if menu_choices is None:
        menu_choices = []
    menu_mock = Mock()
    menu_mock.side_effect = menu_choices + [3]
    monkeypatch.setattr('battleships.menu', menu_mock)
    main()
    expected_menu_calls = len(menu_choices) + 1
    assert menu_mock.call_count == expected_menu_calls


def test_main_exit(monkeypatch):
    "Runs main and checks the menu by selecting exit"
    mock_menu_end_with_exit(monkeypatch)


def test_main_play_battleships_exit(monkeypatch):
    "Runs main and checks the menu by selecting the battleships option and exit"
    play_battleships_mock = Mock()
    play_battleships_mock.return_value = None
    monkeypatch.setattr('battleships.play_battleships', play_battleships_mock)
    mock_menu_end_with_exit(monkeypatch, [1])
    play_battleships_mock.assert_called_once()


def test_main_scoreboard_exit(monkeypatch):
    "Runs main and checks the menu by selecting the scoreboard option and exit"
    monkeypatch.setattr('sys.stdin', STDIN(['']))
    mock_menu_end_with_exit(monkeypatch, [2])


###############################################################################
### MENU
###############################################################################

def test_menu_return(monkeypatch):
    "Checks that the menu returns the correct values for valid inputs"
    inputs = list(range(1, 3))
    stdin = STDIN([str(i) for i in inputs])
    monkeypatch.setattr('sys.stdin', stdin)
    assert [menu() for _ in range(len(inputs))] == inputs
    assert stdin.done()  # Check that all inputs were read


def test_menu_input_validation(monkeypatch):
    "Checks that the menu returns the correct values for invalid and valid inputs"
    stdin = STDIN(['-1', '-5', 'hello', 'hi', '4', 'True', '5', '1'])
    monkeypatch.setattr('sys.stdin', stdin)
    assert [menu() for _ in range(1)] == [1]
    assert stdin.done()  # Check that all inputs were read


def test_menu_interaction(monkeypatch, capfd):
    "Checks the user interaction with the menu"
    inputs = ['1', '2', 'a', '3', '4', '3', 'hi', '3']
    subject = lambda: [menu() for _ in range(5)]
    expected_output = ''.join(["""cMENU BATTLESHIPS

1. Play Battleships
2. Scoreboard
3. Exit
                                 
""" + "Enter the number of your choice: " * prompts for prompts in [1, 1, 2, 2, 2]])
    assert_interaction(monkeypatch, capfd, subject, expected_output, inputs)


###############################################################################
### SCOREBOARD
###############################################################################

def test_save_scoreboard_creates_file():
    "Checks that if an empty scoreboard is saved to the scoreboard file"
    remove_file(SCOREBOARD_FILE)
    save_scoreboard({})
    assert os.path.isfile(SCOREBOARD_FILE) == True


def test_save_scoreboard_updates_file():
    "Checks that saving an updated scoreboard updates the scoreboard file"
    save_scoreboard({})
    t1 = os.stat(SCOREBOARD_FILE).st_mtime
    time.sleep(0.1)
    save_scoreboard({'Player A': 10})
    t2 = os.stat(SCOREBOARD_FILE).st_mtime
    assert t1 != t2


def test_load_scoreboard_non_existing():
    "Checks that loading the scoreboard returns an empty scoreboard if the scoreboard file is missing"
    remove_file(SCOREBOARD_FILE)
    assert load_scoreboard() == {}


def test_load_scoreboard_invalid_files():
    "Checks that loading the scoreboard returns an empty scoreboard if the scoreboard file is invalid"
    with open(SCOREBOARD_FILE, 'w') as f:
        f.write('')
    assert load_scoreboard() == {}
    with open(SCOREBOARD_FILE, 'wb') as f:
        pickle.dump({'Player A': 'Player B'}, f)
    assert load_scoreboard() == {}


def test_save_load_scoreboard():
    "Checks that saving and loading the scoreboard yields the same scoreboard"
    scoreboard = {'Player A': 42, 'Player B': 1}
    save_scoreboard(scoreboard)
    assert load_scoreboard() == scoreboard


def test_save_update_load_scoreboard():
    "Checks that, after multiple saving, loading the scoreboard yields the most recently saved scoreboard"
    scoreboard = {'Player A': 42, 'Player B': 1}
    save_scoreboard(scoreboard)
    scoreboard = {'Player A': 42, 'Player B': 2, 'Player C': 3}
    save_scoreboard(scoreboard)
    assert load_scoreboard() == scoreboard


def test_save_remove_load_scoreboard():
    "Checks that loading the scoreboard returns an empty scoreboard if the scoreboard file was deleted after saving"
    scoreboard = {'Player A': 42, 'Player B': 1}
    save_scoreboard(scoreboard)
    remove_file(SCOREBOARD_FILE)
    assert load_scoreboard() == {}


def test_save_load_scoreboard_remove_empty():
    "Checks that a scoreboarded that has been loaded after saving it only contains player names with a score greater than 0"
    scoreboard = {'Player A': 0, 'Player B': 30, 'Player C': 4, 'Player D': 0, 'Player E': 2}
    save_scoreboard(scoreboard)
    assert load_scoreboard() == {p: s for p, s in scoreboard.items() if s > 0}


def test_main_create_scoreboard(monkeypatch):
    "Checks that the scoreboard information is correctly updated when a player wins a game"
    remove_file(SCOREBOARD_FILE)
    stdin = STDIN(['1', '1', '1', '1', '1', '3'])
    monkeypatch.setattr('sys.stdin', stdin)
    game_mock = Mock()
    game_mock.side_effect = ['Player A', 'Player B', 'Player C', 'Player A', 'Player B']
    monkeypatch.setattr('battleships.play_battleships', game_mock)

    main()
    if load_scoreboard() != {}:
        assert load_scoreboard() == {'Player A': 2, 'Player B': 2, 'Player C': 1}
    else:
        # In case the scoreboard is not persisted in main(), unmock and simulate simple games
        remove_file(SCOREBOARD_FILE)
        stdin = STDIN(
            ['1', 'Player A', 'B'] + ['1 1', '2 1'] + ['2 2', '3 1'] + ['3 3', '4 1'] + ['4 4', '5 1'] + ['5 5'] + [
                'END'] + \
            ['1', 'Player B', 'B'] + ['7 7', '6 2'] + ['6 6', '1 3'] + ['5 5', '1 4'] + ['8 8', '1 5'] + ['4 4'] + [
                'END'] + \
            ['1', 'Player B', 'B'] + ['8 1', '1 1'] + ['7 2', '1 2'] + ['6 3', '1 3'] + ['5 4', '1 4'] + ['4 5'] + [
                'END'] + \
            ['1', 'Player A', 'B'] + ['1 8', '1 1'] + ['2 7', '1 5'] + ['3 6', '1 3'] + ['4 5', '1 2'] + ['5 4'] + [
                'END'] + \
            ['1', 'Player C', 'B'] + ['1 2', '8 1'] + ['2 3', '8 2'] + ['3 4', '8 3'] + ['4 5', '8 4'] + ['5 6'] + [
                'END', '5'])
        monkeypatch.setattr('sys.stdin', stdin)
        monkeypatch.setattr('battleships.play_battleships', play_battleships)
        main()
        assert load_scoreboard() == {'Player A': 2, 'Player B': 2, 'Player C': 1}


def test_main_update_scoreboard(monkeypatch):
    "Check that the scoreboard information is correctly updated when a player wins a game and when there is a draw"
    stdin = STDIN(['1', '1', '1', '1', '3'])
    monkeypatch.setattr('sys.stdin', stdin)
    game_mock = Mock()
    game_mock.side_effect = ['Player A', None, None, 'Player B']
    monkeypatch.setattr('battleships.play_battleships', game_mock)

    save_scoreboard({'Player A': 1, 'Player B': 1, 'Player C': 1})
    main()
    if load_scoreboard() != {}:
        assert load_scoreboard() == {'Player A': 2, 'Player B': 2, 'Player C': 1}
    else:
        remove_file(SCOREBOARD_FILE)
        # In case the scoreboard is not persisted in main(), unmock and simulate simple games
        stdin = STDIN(
            ['1', 'Player A', 'B'] + ['1 1', '2 1'] + ['2 2', '1 3'] + ['3 3', '1 4'] + ['4 4', '5 1'] + ['5 5'] + [
                'END'] + \
            ['1', 'Player B', 'B'] + ['1 2', '8 1'] + ['2 3', '8 2'] + ['3 4', '8 3'] + ['4 5', '8 6'] + ['5 6'] + [
                'END', '5'])
        monkeypatch.setattr('sys.stdin', stdin)
        monkeypatch.setattr('battleships.play_battleships', play_battleships)
        save_scoreboard({'Player A': 1, 'Player B': 1, 'Player C': 1})
        main()
        assert load_scoreboard() == {'Player A': 2, 'Player B': 2, 'Player C': 1}


def test_scoreboard_interaction(monkeypatch, capfd):
    "Checks the user interaction with the scoreboard"
    inputs = ['2','1','3']
    expected_output = """cSCOREBOARD BATTLESHIPS

1. Player A (3)
2. Player B (2)
3. Player C (1)

Press ENTER to return to the menu: """
    remove_file(SCOREBOARD_FILE)
    save_scoreboard({'Player A': 3, 'Player B': 2, 'Player C': 1})
    assert_interaction(monkeypatch, capfd, main, expected_output, inputs, output_exact=False)


###############################################################################
### IS GAME WON
###############################################################################

def test_is_game_won_empty():
    "Checks that is_game_won returns False if there is a single cell that is still alive"
    grid = grid_empty(8, 8)
    grid[0][0] = True
    assert is_game_won(grid) == False


def test_is_game_won_simple():
    "Checks that is_game_won returns True for a grid of size (8,8) and a single ship that is fully sunk"
    grid = grid_empty(8, 8)
    for i in range(1, 6):
        grid[i][i] = False
    assert is_game_won(grid) == True


def test_is_game_won_any_size():
    "Checks that is_game returns True for a grid of user-defined size if values are all False"
    grid = grid_empty(10, 9)
    for i in range(1, 6):
        grid[i][i] = False
    for i in range(4):
        grid[7][i] = False
        assert is_game_won(grid) == True


def test_is_game_not_won_any_size():
    "Checks that is_game returns False for a grid of user-defined size if there are still ships afloat"
    grid = [[False, True, True, True, False, True, False] for i in range(10)]
    assert is_game_won(grid) == False


###############################################################################
### PLAY TURN
###############################################################################

def test_play_turn_input_validation(monkeypatch):
    "Checks that play_turn correctly validates user input"
    stdin = STDIN(['-1 -2', 'hello hi', '2 2'])
    monkeypatch.setattr('sys.stdin', stdin)
    grid_a = grid_empty(8, 8)
    grid_b = grid_empty(8, 8)
    play_turn(grid_a, grid_b, True, False)
    assert stdin.done()  # Check that all inputs were read


def test_play_turn_miss(monkeypatch):
    "Checks that play_turn returns the correct input values (columns and rows)"
    stdin = STDIN(['1 6'])
    monkeypatch.setattr('sys.stdin', stdin)
    grid_a = grid_empty(8, 8)
    grid_b = grid_empty(8, 8)
    assert play_turn(grid_a, grid_b, "Player B", False) == False

def test_play_turn_hit(monkeypatch):
    "Checks that play_turn returns the correct input values (columns and rows)"
    stdin = STDIN(['1 6'])
    monkeypatch.setattr('sys.stdin', stdin)
    grid_a = grid_empty(8, 8)
    grid_a[0][5] = True
    grid_b = grid_empty(8, 8)
    assert play_turn(grid_a, grid_b, "Player B", False) == True


def test_play_turn(monkeypatch):
    "Checks that play_turn returns the correct input values (columns and rows)"
    stdin = STDIN(['6 4', 'hi hello', 'hello hi', '1 1', '2 2'])
    monkeypatch.setattr('sys.stdin', stdin)
    grid_a = grid_empty(8, 8)
    grid_b = grid_empty(8, 8)

    grid_a[0][0] = True

    grid_b[3][5] = True
    grid_b[1][1] = True

    assert play_turn(grid_a, grid_b, "Player A", True) == False
    assert play_turn(grid_a, grid_b, "Player B", False) == True
    assert play_turn(grid_a, grid_b, "Player A", True) == True


def test_play_turn_interaction(monkeypatch, capfd):
    "Checks that play_turn displays the correct information to the user"
    inputs = ['6 4', 'hi hello', '-1 -1', 'hello hi', '7 1', '1 1']
    grid_a = grid_empty(8, 8)
    grid_b = grid_empty(8, 8)

    def subject():
        play_turn(grid_a, grid_b, "A", True)
        play_turn(grid_a, grid_b, "B", False)
        play_turn(grid_a, grid_b, "A", True)

    expected_output = ('cbattleshipsaitisyourturnattacktherightboard12345678123456781122334455667788pleaseselectarowand'
                       'acolumncbattleshipsbitisyourturnattacktheleftboard123456781234567811223344556607788pleaseselect'
                       'arowandacolumnpleaseselectarowandacolumnpleaseselectarowandacolumnpleaseselectarowandacolumncba'
                       'ttleshipsaitisyourturnattacktherightboard1234567812345678112233445566070788pleaseselectarowanda'
                       'column')
    assert_interaction(monkeypatch, capfd, subject, expected_output, inputs)


###############################################################################
### NAME DIALOG
###############################################################################
def small_battleships():
    FLEET = [("Speedboat", 2), ]
    return play_battleships(FLEET)


def test_player_dialog_interaction_valid_inputs(monkeypatch, capfd):
    "Checks the user interaction with the name dialog with valid user input"
    inputs = ['Player A','Player B'] + PLACEMENT_INPUT + ["1 1", "1 1", "1 2", "ENTER"]
    expected_output = """ENTER PLAYER NAMES

Enter the name of player A: 
Enter the name of player B: """
    assert_interaction(monkeypatch, capfd, small_battleships, expected_output, inputs, output_exact=False,
                       input_exact=False)


def test_player_dialog_interaction_invalid_a(monkeypatch, capfd):
    "Checks the user interaction with the name dialog of play_battleships when player A's name input is invalid once"
    inputs = ['', 'Player A', 'Player B'] + PLACEMENT_INPUT + ["1 1", "1 1", "1 2", "ENTER"]
    expected_output = """ENTER PLAYER NAMES

Enter the name of player A: 
Enter the name of player A: 
Enter the name of player B: """
    assert_interaction(monkeypatch, capfd, small_battleships, expected_output, inputs, output_exact=False,
                       input_exact=False)


def test_player_dialog_interaction_invalid_b(monkeypatch, capfd):
    "Checks the user interaction with the name dialog of play_battleships when player B's name input is invalid twice"
    inputs = ['Player A', '', 'Player A', 'Player B'] + PLACEMENT_INPUT + ["1 1", "1 1", "1 2", "ENTER"]
    expected_output = """ENTER PLAYER NAMES

Enter the name of player A: 
Enter the name of player B: 
Enter the name of player B: 
Enter the name of player B: """
    assert_interaction(monkeypatch, capfd, small_battleships, expected_output, inputs, output_exact=False,
                       input_exact=False)


###############################################################################
### PLAY BATTLESHIPS
###############################################################################

def test_play_battleship_a_wins(monkeypatch):
    "Checks that play_battleships returns the correct winner A"
    stdin = STDIN(['A', 'B'] + PLACEMENT_INPUT + ["1 1", "1 1", "1 2", "ENTER"])
    monkeypatch.setattr('sys.stdin', stdin)
    assert small_battleships() == 'A'


def test_play_battleship_b_wins(monkeypatch):
    "Checks that play_battleships returns the correct winner B"
    stdin = STDIN(['A', 'B'] + PLACEMENT_INPUT + ["1 1", "1 1", "2 1", "1 2", "ENTER"])
    monkeypatch.setattr('sys.stdin', stdin)
    assert small_battleships() == 'B'


def test_play_battleships_win_interaction(monkeypatch, capfd):
    "Checks the user interaction of play_battleships when there is a winner"
    inputs = ['Player A', 'B'] + PLACEMENT_INPUT + ["1 1", "1 1", "1 2", "\n"]
    expected_output = """THE GAME IS OVER!

    1   2   3   4   5   6   7   8             1   2   3   4   5   6   7   8  
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
1 | X |   |   |   |   |   |   |   |   |   1 | X | X |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
2 |   |   |   |   |   |   |   |   |   |   2 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
3 |   |   |   |   |   |   |   |   |   |   3 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
4 |   |   |   |   |   |   |   |   |   |   4 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
5 |   |   |   |   |   |   |   |   |   |   5 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
6 |   |   |   |   |   |   |   |   |   |   6 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
7 |   |   |   |   |   |   |   |   |   |   7 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+
8 |   |   |   |   |   |   |   |   |   |   8 |   |   |   |   |   |   |   |   |
  +---+---+---+---+---+---+---+---+   |     +---+---+---+---+---+---+---+---+

Player A won the game!

Press ENTER to return to the menu: """
    assert_interaction(monkeypatch, capfd, small_battleships, expected_output, inputs, output_exact=False)

def test_play_battleships_interaction(monkeypatch, capfd):
    "Check the user interaction of battleships"
    input = ['Albert', 'Berta',

             # a input
             '1 1, 1 2', '2 1, 2 4', '3 1, 3 3', '4 1, 4 3', '5 1, 5 5',
             # b input
             '1 1, 1 2', '2 1, 2 4', '3 1, 3 3', '4 1, 4 3', '5 1, 5 5',
             '1 1', '1 1', '1 2', '1 2',
             '2 1', '2 1', '2 2', '2 2', '2 3', '2 3', '2 4', '2 4',
             '3 1', '3 1', '3 2', '3 2', '3 3', '3 3',
             '4 1', '4 1', '4 2', '4 2', '4 3', '4 3',
             '5 1', '5 1', '5 2', '5 2', '5 3', '5 3', '5 4', '5 4', '5 5',
             '\n']
    expected_output = ("centerplayernamesenterthenameofplayeraenterthenameofplayerbcalbertpositiontheshipspeedboatlengt"
                       "h21234567812345678selectbeginningandendcellcalbertpositiontheshipdestroyerlength412345678100234"
                       "5678selectbeginningandendcellcalbertpositiontheshipattackerlength31234567810020000345678selectb"
                       "eginningandendcellcalbertpositiontheshipattackerlength31234567810020000300045678selectbeginning"
                       "andendcellcalbertpositiontheshipaircraftcarrierlength51234567810020000300040005678selectbeginni"
                       "ngandendcellccbertapositiontheshipspeedboatlength21234567812345678selectbeginningandendcellcber"
                       "tapositiontheshipdestroyerlength4123456781002345678selectbeginningandendcellcbertapositionthesh"
                       "ipattackerlength31234567810020000345678selectbeginningandendcellcbertapositiontheshipattackerle"
                       "ngth31234567810020000300045678selectbeginningandendcellcbertapositiontheshipaircraftcarrierleng"
                       "th51234567810020000300040005678selectbeginningandendcell"
                       "cbattleshipsalbertitisyourturnattacktherightboard12345678123456781122334455667788"
                       "pleaseselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard123456781234567811"
                       "x22334455667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattacktherightboard"
                       "12345678123456781x1x22334455667788pleaseselectarowandacolumncbattleshipsbertaitisyourturnattack"
                       "theleftboard12345678123456781x1xx22334455667788pleaseselectarowandacolumncbattleshipsalbert"
                       "itisyourturnattacktherightboard12345678123456781xx1xx22334455667788pleaseselectarowandacolumn"
                       "cbattleshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx22x334455667788please"
                       "selectarowandacolumncbattleshipsalbertitisyourturnattacktherightboard12345678123456781xx1xx2x2"
                       "x334455667788pleaseselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard123456781"
                       "23456781xx1xx2x2xx334455667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattackthe"
                       "rightboard12345678123456781xx1xx2xx2xx334455667788pleaseselectarowandacolumncbattleshipsbertait"
                       "isyourturnattacktheleftboard12345678123456781xx1xx2xx2xxx334455667788pleaseselectarowandacolumn"
                       "cbattleshipsalbertitisyourturnattacktherightboard12345678123456781xx1xx2xxx2xxx334455667788plea"
                       "seselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx2xxx"
                       "2xxxx334455667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattacktherightboard12"
                       "345678123456781xx1xx2xxxx2xxxx334455667788pleaseselectarowandacolumncbattleshipsbertaitisyourt"
                       "urnattacktheleftboard12345678123456781xx1xx2xxxx2xxxx33x4455667788pleaseselectarowandacolumncb"
                       "attleshipsalbertitisyourturnattacktherightboard12345678123456781xx1xx2xxxx2xxxx3x3x4455667788p"
                       "leaseselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx2"
                       "xxxx2xxxx3x3xx4455667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattacktheright"
                       "board12345678123456781xx1xx2xxxx2xxxx3xx3xx4455667788pleaseselectarowandacolumncbattleshipsber"
                       "taitisyourturnattacktheleftboard12345678123456781xx1xx2xxxx2xxxx3xx3xxx4455667788pleaseselecta"
                       "rowandacolumncbattleshipsalbertitisyourturnattacktherightboard12345678123456781xx1xx2xxxx2xxxx3"
                       "xxx3xxx4455667788pleaseselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard12345"
                       "678123456781xx1xx2xxxx2xxxx3xxx3xxx44x55667788pleaseselectarowandacolumncbattleshipsalbertitisy"
                       "ourturnattacktherightboard12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4x4x55667788pleaseselectarowa"
                       "ndacolumncbattleshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx2xxxx2xxxx3xxx3xx"
                       "x4x4xx55667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattacktherightboard123456"
                       "78123456781xx1xx2xxxx2xxxx3xxx3xxx4xx4xx55667788pleaseselectarowandacolumncbattleshipsbertaitis"
                       "yourturnattacktheleftboard12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xx4xxx55667788pleaseselectar"
                       "owandacolumncbattleshipsalbertitisyourturnattacktherightboard12345678123456781xx1xx2xxxx2xxxx3x"
                       "xx3xxx4xxx4xxx55667788pleaseselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard"
                       "12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx55x667788pleaseselectarowandacolumncbattleships"
                       "albertitisyourturnattacktherightboard12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx5x5x667788"
                       "pleaseselectarowandacolumncbattleshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx"
                       "2xxxx2xxxx3xxx3xxx4xxx4xxx5x5xx667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnat"
                       "tacktherightboard12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx5xx5xx667788pleaseselectarowan"
                       "dacolumncbattleshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx2xxxx2xxxx3xxx3xxx"
                       "4xxx4xxx5xx5xxx667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattacktherightboar"
                       "d12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx5xxx5xxx667788pleaseselectarowandacolumncbattl"
                       "eshipsbertaitisyourturnattacktheleftboard12345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx5xxx5x"
                       "xxx667788pleaseselectarowandacolumncbattleshipsalbertitisyourturnattacktherightboard12345678123"
                       "456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx5xxxx5xxxx667788pleaseselectarowandacolumncthegameisover12"
                       "345678123456781xx1xx2xxxx2xxxx3xxx3xxx4xxx4xxx5xxxx5xxxxx667788albertwonthegamepressentertoretu"
                       "rntothemenu")
    assert_interaction(monkeypatch, capfd, play_battleships, expected_output, input)