import ui
import pickle

SHIPS = [("Speedboat", 2), ("Destroyer", 4), ("Attacker", 3), ("Attacker", 3), ("Aircraft Carrier", 5), ]


def main():

    scoreboard = load_scoreboard()  # Lade das Scoreboard zu Beginn der Funktion
    
    while True:
        items = menu()

        if items == 1:
            winner = play_battleships()

            if winner:
                scoreboard[winner] = scoreboard.get(winner, 0) + 1  # scoreboard ist jetzt verfügbar
                save_scoreboard(scoreboard)

        elif items == 2:
            ui.display_headline("scoreboard battleships")
            ui.display_scoreboard(scoreboard)
            ui.prompt("Press ENTER to return to the menu")
            
        elif items == 3:
            return None







def menu():
    items = ["Play Battleships", "Scoreboard", "Exit"]

    ui.display_headline("menu battleships")
    ui.display_menu(items)

    while True:
        # Prompt the user for a choice
        choice = ui.prompt("Enter the number of your choice")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(items):
                return choice  # Return valid choice

            

    








def save_scoreboard(scoreboard):
    with open("scoreboard.dat", "wb") as file:
        pickle.dump(scoreboard, file)

    return None






def load_scoreboard():
    
    try:
        with open("scoreboard.dat", "rb") as file:
            scoreboard = pickle.load(file)

            return {player: score for player, score in scoreboard.items() if isinstance(score, int) and score > 0}

    except (FileNotFoundError, pickle.UnpicklingError, EOFError):
        return {}








def is_game_won(grid):
    for row in grid:
        if True in row:  # A ship part still exists
            return False  # If any ship part is still intact, the game is not won

    return True  # All ship parts have been hit









def play_turn(grid_a, grid_b, player_name, is_player_a):

    target_grid = grid_b if is_player_a else grid_a

    while True:
        ui.display_turn_start(player_name, is_player_a)
        ui.display_game(grid_a, grid_b)


        while True:
            user_input = ui.prompt("Please select a row and a column")

            try:
                row, col = map(int, user_input.split())

                if not (1 <= row <= len(target_grid) and 1 <= col <= len(target_grid[0])):
                    continue

                if target_grid[row - 1][col - 1] in [False, "miss"]:
                    continue

                if target_grid[row - 1][col - 1]:
                    target_grid[row - 1][col - 1] = False
                    return True

                else:
                    target_grid[row - 1][col - 1] = "miss"
                    return False
            
            
            except (ValueError, IndexError):
                continue


    # return True or False


    











def is_ship_position_possible(length, start_row, start_col, end_row, end_col, grid):

    if not (start_row == end_row or start_col == end_col):
        return False
    if abs(end_row - start_row) + abs(end_col - start_col) + 1 != length:
        return False

    if start_row == end_row:
        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
            if grid[start_row][col] is not None:
                return False
    else:
        for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
            if grid[row][start_col] is not None:
                return False

    return True
    








def position_ships(player, rows, cols, ships):

    grid = [[None for i in range(cols)] for i in range(rows)]

    for ship_name, ship_length in ships:
        while True:
            ui.display_headline(f"{player} position the ship {ship_name.upper()} - length {ship_length}")
            ui.display_grid(grid)

            try:
                start, end = ui.prompt("Select beginning and end cell").split(",")
                start_row, start_col = map(int, start.strip().split())
                end_row, end_col = map(int, end.strip().split())

                start_row -= 1
                end_row -= 1
                start_col -= 1
                end_col -= 1

                if is_ship_position_possible(ship_length, start_row, start_col, end_row, end_col, grid):
                    for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                        grid[start_row][col] = True
                    for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                        grid[row][start_col] = True
                    break
                else:
                    ui.display_message("Invalid ship position. Try again.")
            except (ValueError, IndexError):
                ui.display_message("Invalid input. Try again.")

    return grid











def play_battleships(ships=SHIPS):

    grid_rows = 8
    grid_cols = 8

    ui.display_headline("enter player names")

    while True:
        player_a = ui.prompt("Enter the name of player A").strip()
        if player_a:
            break

    while True:
        player_b = ui.prompt("Enter the name of player B").strip()
        if player_b and player_b != player_a:
            break

    grid_a = position_ships(player_a, grid_rows, grid_cols, ships)
    grid_b = position_ships(player_b, grid_rows, grid_cols, ships)

    is_player_a_turn = True

    while True:
        winner = player_a if is_player_a_turn else player_b
        play_turn(grid_a, grid_b, winner, is_player_a_turn)

        if is_game_won(grid_b if is_player_a_turn else grid_a):

            ui.display_headline("the game is over!")
            ui.display_game(grid_a, grid_b)
            ui.display_message(f"{winner} won the game!")
            break

        is_player_a_turn = not is_player_a_turn

    ui.prompt("Press ENTER to return to the menu")

    return winner
    
    













if __name__ == '__main__':
    main()
