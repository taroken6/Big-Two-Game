class Lobby:
    def __init__(self, number, name, password):
        self.lobby_number = number
        self.lobby_name = name
        self.password = password
        self.host = 0  # Index of host player within 'players' list
        self.players = [self.host]
        self.ready = [True, False, False, False]
        self.start = False

    def is_full_lobby(self):
        """
        Returns boolean whether the lobby is full
        :return: True | False
        """
        if len(self.players) < 4:
            return False
        else:
            if all(player is not None for player in self.players):
                return True

    def is_pass_protected(self):
        """
        Returns whether the lobby is password protected
        :return: True | False
        """
        if self.password != '':
            return True
        else:
            return False

    def ready_player(self, player_num):
        """
        Readies the given player
        :param player_num: Player number within the lobby
        :return: True | False
        """
        if not self.ready[player_num]:
            self.ready[player_num] = True
        else:
            self.ready[player_num] = False

    def remove_player(self, player_num):
        """
        Remove the given player from lobby
        If the removed player was the host, the player number closest to '0' becomes host
        :param player_num:
        :return:
        """
        if player_num == self.host:
            for player in self.players:
                if player != self.host and player is not None:
                    self.host = player
                    break
        self.players[player_num] = None
        self.ready[player_num] = False

    def reset_lobby(self):
        """
        Called once the game is finished and all players will need to ready up again
        """
        self.start = False
        self.ready = [False] * 4

    def start_game(self):
        players_ready = 0
        if len(self.players) == 1:
            return False
        for player in self.players:
            if player is None:
                continue
            elif self.ready[player]:
                players_ready += 1
        if players_ready == self.get_total_players():
            self.start = True
            return True

    def get_name(self):
        return self.lobby_name

    def get_password(self):
        return self.password

    def get_number(self):
        return self.lobby_number

    def get_host(self):
        return self.host

    def get_total_players(self):
        """
        :return: Number of players inside the lobby
        """
        total_players = 0
        for player in self.players:
            if player is None:
                continue
            else:
                total_players += 1
        return total_players

    def enter_player(self):
        """
        If there's an 'None' slot in list of players, insert player into that player into the slot
        :return: The player's number
        """
        for player_num, player in enumerate(self.players):
            if player is None:
                self.players[player_num] = player_num
                return player_num
            elif player_num == player:
                continue
            else:
                print("Error in making player")
                break
