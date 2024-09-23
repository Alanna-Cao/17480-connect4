import requests

BASE_URL = "http://127.0.0.1:8000"

def create_game(player1_name, player2_name, num_human_players):
    response = requests.post(f"{BASE_URL}/games", 
                             params={"player1_name": player1_name, 
                                     "player2_name": player2_name, 
                                     "num_human_players": num_human_players})

    if response.status_code == 200:
        return response.json()
    else:
        print("Error creating game:", response.json())
        return None

def get_game(game_id):
    response = requests.get(f"{BASE_URL}/games/{game_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching game:", response.json())
        return None

def list_games():
    response = requests.get(f"{BASE_URL}/games")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error listing games:", response.json())
        return None

def make_move(game_id, player_id, column):
    response = requests.post(f"{BASE_URL}/games/{game_id}/moves", params={"player_id": player_id, "column": column})
    if response.status_code == 200:
        return response.json()
    else:
        print("Error making move:", response.json()["detail"])
        return None

def restart_game(game_id):
    response = requests.post(f"{BASE_URL}/games/{game_id}/restart")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error restarting game:", response.json())
        return None

def quit_game(game_id):
    response = requests.post(f"{BASE_URL}/games/{game_id}/quit")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error quitting game:", response.json())
        return None

def get_next_move(game_id):
    response = requests.post(f"{BASE_URL}/games/{game_id}/next_move")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error getting next move:", response.json())
        return None

def print_board(board, players):
    color_to_player = {players["p1"]["id"]: 'x', players["p2"]["id"]: 'o'}
    for row in board:
        print("".join(color_to_player.get(cell, '-') for cell in row))

def display_help():
    print("----------------------------------------------")
    print("Available commands:")
    print("  0-5: Drop a piece in the specified column")
    print("  r  : Restart the game")
    print("  q  : Quit the game")
    print("  h  : Display this help message")
    print("  ls : List all games")
    print("  gs <game_id>: Get the current state of a specific game")
    print("----------------------------------------------")

def print_current_board(game):
    if game:
        print("Current Board")
        print_board(game["board"], players=game["players"])
        print(f"{game['players'][game['current_turn']]['name']}'s turn ({game['players'][game['current_turn']]['color']})")

def get_valid_input(prompt, valid_options):
    try:
        value = int(input(prompt))
        if value in valid_options:
            return value
        else:
            print(f"Invalid input. Please enter one of the following: {valid_options}")
            return get_valid_input(prompt, valid_options)
    except ValueError:
        print(f"Invalid input. Please enter a number from the following: {valid_options}")
        return get_valid_input(prompt, valid_options)
    
def main():
    print("##############################################")
    print("#                                            #")
    print("#                 CONNECT 4                  #")
    print("#                                            #")
    print("##############################################")
    print("#                                            #")
    print("#  Welcome to the Connect 4 Game!            #")
    print("#  Two players will take turns to drop       #")
    print("#  their pieces into the columns. The first  #")
    print("#  player to connect four pieces in a row    #")
    print("#  (horizontally, vertically, or diagonally) #")
    print("#  wins the game.                            #")
    print("#                                            #")
    print("##############################################")
    print()
    
    num_human_players = get_valid_input("Enter number of human players (0, 1, or 2): ", [0, 1, 2])

    player1_name = input("Enter Player 1 name: ") if num_human_players > 0 else "Computer 1"
    player2_name = input("Enter Player 2 name: ") if num_human_players > 1 else "Computer 2"

    while True:
        game = create_game(player1_name, player2_name, num_human_players)
        if not game:
            return

        game_id = game["id"]

        print(f"Game created! Game ID: {game_id}")
        print_current_board(game)

        commands = {
            'r': lambda: restart_game(game_id),
            'q': lambda: quit_game(game_id),
            'h': display_help,
            'ls': list_games,
        }

        while True:
            game = get_game(game_id)
            if not game:
                return

            if game["status"] == "won":
                print(f"Game over! {game['players'][game['winner']]['name']} won!")
                input("Press Enter to start a new game...")
                break
            elif game["status"] == "draw":
                print("Game over! It's a draw!")
                input("Press Enter to start a new game...")
                break

            if game["players"][game["current_turn"]]["type"] == "computer":
                next_move = get_next_move(game_id)
                if next_move is not None:
                    game = make_move(game_id, game["current_turn"], next_move["next_move"])
                    print_current_board(game)
            else:
                command = input("Enter column (0-5) or command ('h' for help): ").strip().lower()

                if command in commands:
                    result = commands[command]()
                    if command == 'q' and result:
                        print(result["message"])
                        return
                    elif command == 'r' and result:
                        print("Game restarted.")
                        break;
                    elif command == 'ls' and result:
                        print("----------------------------------------------")
                        print("Active games:")
                        for game in result:
                            print(f"Game ID: {game['id']}, "
                                  f"Players: {game['players']['p1']['name']} vs {game['players']['p2']['name']}, "
                                  f"Current Turn: {game['current_turn']}, "
                                  f"Status: {game['status']}, "
                                  f"Winner: {game['winner']}")
                        print("----------------------------------------------")
                elif command.startswith('gs '):
                    _, game_id_to_check = command.split()
                    result = get_game(game_id_to_check)
                    if result:
                        print("Game Board of", result["id"])
                        print_board(result["board"], players=result["players"])
                        print("----------------------------------------------")
                    else:
                        print("Error fetching game state.")
                else:
                    try:
                        column = int(command)
                        game = make_move(game_id, game["current_turn"], column)
                        print_current_board(game)
                    except ValueError:
                        print("Invalid input. Please enter a column number (0-5), 'r' to restart, or 'q' to quit.")

if __name__ == "__main__":
    main()
    