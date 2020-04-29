class Lobby:
    def __init__(self, number, name, password):
        self.number = number
        self.name = name
        self.password = password
        self.host = 0
        self.players = [self.host]
        self.ready = [True, False, False, False]
        self.start = False

    def full_lobby(self):
        if len(self.players) < 4:
            return False
        else:
            if all(player is not None for player in self.players):
                return True

    def is_pass_protected(self):
        if self.password != '':
            return True
        else:
            return False

    def ready_player(self, player_num):
        if not self.ready[player_num]:
            self.ready[player_num] = True
        else:
            self.ready[player_num] = False

    def remove_player(self, player):
        if player == self.host:
            for player_num in self.players:
                if player_num != self.host and player_num is not None:
                    self.host = player_num
                    break
        self.players[player] = None
        self.ready[player] = False
        print(f"Removed player {player}")

    def reset_lobby(self):
        self.start = False
        self.ready = [False] * 4

    def start_game(self):
        players_ready = 0
        if len(self.players) == 1:
            print("Not enough players!")
            return False
        for player in self.players:
            if player is None:
                continue
            elif self.ready[player]:
                players_ready += 1
        if players_ready == self.get_playing_players():
            self.start = True
            return True

    def get_name(self):
        return self.name

    def get_password(self):
        return self.password

    def get_number(self):
        return self.number

    def get_host(self):
        return self.host

    def get_playing_players(self):
        players_playing = 0
        for player in self.players:
            if player is None:
                continue
            else:
                players_playing += 1
        return players_playing

    def make_player(self):
        for index, number in enumerate(self.players):
            if number is None:
                self.players[index] = index
                return index
            elif index != number:
                self.players.append(index)
                return index
            elif index + 1 == len(self.players):
                self.players.append(index + 1)
                return index + 1
            elif index == number:
                continue
            else:
                print("Error in making player")
                break
