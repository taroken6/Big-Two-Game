import socket
from _thread import *
from game import Game, Player
import pickle
from lobby import Lobby

server = socket.gethostbyname(socket.gethostname())
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"Connecting to {server}:{port}")
try:
    s.bind((server, port))
    print("Connected!")
except socket.error as e:
    str(e)

s.listen(4)
print("Waiting for connection...")

connected = set()  # Doesn't seem needed?
games = {}  # Game dictionary
game_ID = {}  # Lobby dictionary
rooms = []


def setup_game(room, game):
    for player in room.players:
        if player is not None:
            game.players.append(Player(player))
    game.shuffle_deck()
    game.deal_cards()


def read_data(data):
    bad_char = '[],'
    data = data.translate({ord(c): None for c in bad_char})
    data = list(map(str, data.split()))

    return data


def threaded_client(conn):
    run = True
    playing = False

    this_room = None
    room = None
    key = None
    global rooms
    game_number = 0
    player_num = 0

    conn.send(str.encode("Connected!"))

    while run:

        try:

            if not playing:
                data = pickle.loads(conn.recv(4096))

                if type(data) is tuple:
                    if len(data) == 3:  # Create a room
                        if data[2] == 'create':
                            print(f"Received Tuple: {data[2]}")
                            if len(rooms) == 0:
                                print("No rooms... Creating first room")
                                rooms.append(0)
                                this_room = 0
                            else:
                                print("Room detected")
                                for count, room_ID in enumerate(rooms):
                                    if count != room_ID:
                                        this_room = count
                                        rooms.append(count)
                                        print(f"Created room {count}")
                                        break
                                    elif count + 1 == len(rooms):
                                        this_room = count + 1
                                        rooms.append(count + 1)
                                        print(f"Created room {count + 1}")
                                        break
                                    elif count == room_ID:
                                        print("Count = room_ID")
                                        continue
                                    else:
                                        print(f"Error in making rooms... count = {count}, room_ID = {room_ID}")
                            key = this_room
                            game_ID[this_room] = Lobby(this_room, data[0], data[1])
                            print(f"Created room {this_room} with host {game_ID[this_room].get_host()}")
                            conn.sendall(pickle.dumps(game_ID[this_room]))
                    elif data[1] == 'join':
                        print("Received join")
                        key = data[0]
                        player_num = 5
                        if key in game_ID.keys():
                            room = game_ID[key]
                            if room.in_progress:
                                room = "In-progress"
                            elif room.is_full_lobby():
                                room = "Full"
                            else:
                                player_num = room.enter_player()
                        else:
                            room = "Empty"
                        conn.sendall(pickle.dumps((room, player_num)))
                    elif data[1] == 'password':  # TODO: Encrypt password in the future
                        key, password = data[0]
                        room = game_ID[key]
                        print("User input Password = " + password)
                        if password == room.get_password():
                            conn.sendall(pickle.dumps(True))
                        else:
                            conn.sendall(pickle.dumps(False))
                    elif data[1] == 'quit':
                        key, player = data[0]
                        room = game_ID[key]
                        print(f"Player {player} has quit...")
                        room.remove_player(player)
                        if all(players is None for players in room.players):
                            game_ID.pop(key, None)
                            print("No more players! Removed room")
                            print(game_ID.items())
                        conn.sendall(pickle.dumps(None))
                    elif data[1] == 'key':  # Reloads room
                        conn.sendall(pickle.dumps(game_ID[data[0]]))
                    elif data[1] == 'ready':
                        info = data[0]  # Tuple: Key, player_num
                        key = info[0]
                        player_num = info[1]

                        room = game_ID[key]
                        room.ready_player(player_num)
                        conn.sendall(pickle.dumps(room))
                    elif data[1] == 'start':
                        print("Starting game...")
                        room = game_ID[data[0]]
                        if room.start_game():
                            game_number = room.get_number()
                            games[game_number] = Game(game_number)
                            setup_game(room, games[game_number])
                            print(games[game_number].players)
                            conn.sendall(pickle.dumps(None))
                        else:
                            print("Failed to start game")
                    elif data[1] == "game":
                        game_number = data[0]
                        print(f"Game key is {game_number}")
                        playing = True
                        conn.sendall(pickle.dumps(games[game_number]))
                        continue
                    else:
                        print("Received unknown tuple")
                else:
                    print("Sending lobby")
                    conn.sendall(pickle.dumps(list(game_ID.items())))

            elif playing:
                data = conn.recv(4096).decode()
                if game_number in games:
                    game = games[game_number]

                    if not data:
                        print("No data received")
                        break
                    else:
                        if data[0] == '[':
                            print(f"Data list before is: {data}")
                            data = read_data(data)
                            print(f"Received list data is {data}")
                            if data[0] == "'leave'":
                                player_num, key = int(data[1]), int(data[2])
                                room = game_ID[key]

                                room.remove_player(player_num)
                                print(f"Player {player_num} has quit!")
                                game.players[player_num].quit = True
                                if player_num == game.current_player:
                                    game.next_player()
                                    if game.first_play:
                                        game.update_first_play()
                            else:
                                data = (int(index) for index in data)
                                data = list(data)
                                game.reset_play()
                                for index in reversed(data):
                                    game.get_play(index)
                                    game.players[game.current_player].remove_card(index)
                                if game.first_play:
                                    game.first_play = False
                                game.hand_played.sort(key=lambda card: (card.rank, card.suit))
                                game.check_if_finished()
                                if game.players[game.current_player].get_finish_status():
                                    game.update_players()
                                    print(f"Current player index is {game.current_player}")
                                    print(f"Player {game.players[game.current_player].player}")
                                else:
                                    game.play_type = game.check_hand(game.hand_played)
                                    game.set_strong_player()
                                game.next_player()
                                print(f"Play type is now {game.PLAY_TYPES[game.play_type]}")
                        elif data == 'pass':
                            print(f"Player {game.players[game.current_player].player} passed!")
                            game.next_player()
                            game.pass_track()
                            print("A player has passed!")

                    if not game.game_finished:
                        game.finish_game()

                    conn.sendall(pickle.dumps(game))

                    if game.game_finished:
                        print("Resetting lobby...")
                        ID = game.ID
                        playing = False
                        game_ID[ID].reset_lobby()

                else:
                    print("Game key not in dictionary")
            else:
                print('Game go bye bye')
                break
        except socket.error as e:
            print('No game (End of threaded_client)')
            print(e)
            if key in game_ID.keys():
                print("Key of disconnected user is found! Deleting...")
                room = game_ID[key]
                room.remove_player(player_num)
                if all(players is None for players in room.players):
                    game_ID.pop(key, None)
                    print("No more players! Removed room")
                if playing:
                    game.players[player_num].quit = True
                    if player_num == game.current_player:
                        game.next_player()
                        if game.first_play:
                            game.update_first_play()
            else:
                print("Unknown key! Room was not closed!")
            break
    conn.close()


while True:
    connection, address = s.accept()
    print("Connected to: ", address)
    start_new_thread(threaded_client, (connection, ))
