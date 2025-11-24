import ui
import pickle

SHIPS = [("Speedboat", 2), ("Destroyer", 4), ("Attacker", 3), ("Attacker", 3), ("Aircraft Carrier", 5), ]


def main():
    # Load the scoreboard from a file at the beginning
    scoreboard = load_scoreboard()
    
    while True:
        items = menu() # Show the menu and get the user's choice

        if items == 1:
            # Start a new game of Battleships and update the scoreboard if there's a winner
            winner = play_battleships()

            if winner:
                # Update the scoreboard and save it to the file
                scoreboard[winner] = scoreboard.get(winner, 0) + 1  
                save_scoreboard(scoreboard)

        elif items == 2:
            # Display the scoreboard
            ui.display_headline("scoreboard battleships")
            ui.display_scoreboard(scoreboard)
            ui.prompt("Press ENTER to return to the menu")
            
        elif items == 3:
            return None # Exit the program





def menu():
    # Menu items to display to the user
    items = ["Play Battleships", "Scoreboard", "Exit"]

    ui.display_headline("menu battleships")
    ui.display_menu(items)

    while True:
        # Prompt the user to choose an option
        choice = ui.prompt("Enter the number of your choice")

        if choice.isdigit():
            choice = int(choice)

            # Check if the choice is valid
            if 1 <= choice <= len(items):
                return choice  # Return the valid choice

            

    


def save_scoreboard(scoreboard):
    # Save the scoreboard to a file using pickle
    with open("scoreboard.dat", "wb") as file:
        pickle.dump(scoreboard, file)

    return None






def load_scoreboard():
    try: # Try to load the scoreboard from the file
        with open("scoreboard.dat", "rb") as file:
            scoreboard = pickle.load(file)

            # Only return players with a valid score (positive integers)
            return {player: score for player, score in scoreboard.items() if isinstance(score, int) and score > 0}


    except (FileNotFoundError, pickle.UnpicklingError, EOFError):
        return {} # Return an empty scoreboard if there was an error loading the file






def is_game_won(grid):
    # Check if all ships are hit
    for row in grid:
        if True in row:  # If any ship part still exists
            return False  # Game is not won yet
    
    return True  # All ships have been hit, game is won






def play_turn(grid_a, grid_b, player_name, is_player_a):

    target_grid = grid_b if is_player_a else grid_a

    while True:
        # Display the player's turn and the game grid
        ui.display_turn_start(player_name, is_player_a)
        ui.display_game(grid_a, grid_b)


        while True:
            # Prompt the player for a row and column to target
            user_input = ui.prompt("Please select a row and a column")

            try:
                row, col = map(int, user_input.split()) # Convert input to integers


                # Check if the input is within the grid bounds
                if not (1 <= row <= len(target_grid) and 1 <= col <= len(target_grid[0])):
                    continue

                # Skip if the selected cell has already been hit or missed
                if target_grid[row - 1][col - 1] in [False, "miss"]:
                    continue


                # Mark the hit or miss
                if target_grid[row - 1][col - 1]:
                    target_grid[row - 1][col - 1] = False # Ship hit
                    return True
                else:
                    target_grid[row - 1][col - 1] = "miss" # Missed shot
                    return False
            
            
            except (ValueError, IndexError):
                continue # If invalid input, ask again






def is_ship_position_possible(length, start_row, start_col, end_row, end_col, grid):

    # Check if the ship's position is valid (either horizontal or vertical)
    if not (start_row == end_row or start_col == end_col):
        return False
    if abs(end_row - start_row) + abs(end_col - start_col) + 1 != length:
        return False

    # Check if the selected cells are free of other ships
    if start_row == end_row:
        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
            if grid[start_row][col] is not None:
                return False # Cell is occupied, cannot place the ship here
    else:
        for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
            if grid[row][start_col] is not None:
                return False # Cell is occupied, cannot place the ship here

    return True # Valid position
    





def position_ships(player, rows, cols, ships):
    grid = [[None for _ in range(cols)] for _ in range(rows)] # Create an empty grid for placing ships

    for ship_name, ship_length in ships:
        while True:
            # Display the ship positioning screen
            ui.display_headline(f"{player} position the ship {ship_name.upper()} - length {ship_length}")
            ui.display_grid(grid)

            while True:
                try:
                    # Get the start and end cell for the ship placement
                    start, end = ui.prompt("Select beginning and end cell").split(",")
                    start_row, start_col = map(int, start.strip().split())
                    end_row, end_col = map(int, end.strip().split())

                    # Adjust for zero-indexing
                    start_row -= 1
                    end_row -= 1
                    start_col -= 1
                    end_col -= 1

                    # Check if the ship can be placed at the given coordinates
                    if is_ship_position_possible(ship_length, start_row, start_col, end_row, end_col, grid):

                        # Mark the grid with the ship's cells
                        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                            grid[start_row][col] = True

                        for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                            grid[row][start_col] = True

                        break # Move to the next ship

                except (ValueError, IndexError):
                    continue # If input is invalid, prompt again

            break  # Switch to the next ship

    return grid





def play_battleships(ships=SHIPS):

    # Initialize the game grid
    grid_rows = 8
    grid_cols = 8

    # Get player names
    ui.display_headline("enter player names")

    while True:
        player_a = ui.prompt("Enter the name of player A").strip()
        if player_a:
            break

    while True: 
        player_b = ui.prompt("Enter the name of player B").strip()
        if player_b and player_b != player_a: # Ensure player B is different from player A
            break

    # Position the ships for both players
    grid_a = position_ships(player_a, grid_rows, grid_cols, ships)
    grid_b = position_ships(player_b, grid_rows, grid_cols, ships)

    # Start the game
    is_player_a_turn = True

    while True:
        # Determine the current player
        winner = player_a if is_player_a_turn else player_b
        play_turn(grid_a, grid_b, winner, is_player_a_turn)

        # Check if the game is won
        if is_game_won(grid_b if is_player_a_turn else grid_a):
            ui.display_headline("the game is over!")
            ui.display_game(grid_a, grid_b)
            ui.display_message(f"{winner} won the game!")
            break # Exit the loop after the game ends

        # Switch turns
        is_player_a_turn = not is_player_a_turn

    ui.prompt("Press ENTER to return to the menu")

    return winner
    
    


if __name__ == '__main__':
    main()




# Note: The information used to solve this assignment was primarily gathered from the lecture slides and my own thought processes. ChatGPT 4.0 helped me identify mistakes and enhance the overall quality of the code.