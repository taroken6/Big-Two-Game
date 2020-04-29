from deck import Deck
from card import Card
import math


class Game:
    PLAY_TYPES = ('none', 'Single', 'Pair', 'Straight', 'Full House', 'Four of a kind', 'Straight Flush')

    def __init__(self, ID):
        # Loading
        self.ready = False
        self.players_dealt = False
        self.players_loaded = False
        self.loaded_count = 0
        self.ID = ID
        # Post-loading
        self.deck = Deck()
        self.players = []
        self.first_play = True
        self.first_play_card = Card(Card.RANKS[0], Card.SUITS[0])
        self.hand_played = []  # List of cards played previously
        self.play_type = 0
        # self.prev_play = []  # Not Used
        self.starting_player = 0
        self.current_player = 0
        self.strong_play_player = 4  # 4 = no strong player
        self.finished_players = []
        self.game_finished = False

    def finish_game(self):
        finished_player_count = 0

        for player in self.players:
            if player.get_finish_status() or player.quit:
                finished_player_count += 1

        if finished_player_count == len(self.players) - 1:
            print("Game finished!")
            self.finished_players.append(self.players[self.current_player])
            self.game_finished = True

    def deal_cards(self):
        if len(self.players) == 2:
            print('2 players')
            for player in range(2):
                self.players[player].draw(self.deck, 13)
                self.players[player].hand.sort(key=lambda card: (card.rank, card.suit))
                print(self.players[player])
            # self.players[0].hand.sort(key=lambda card: (card.rank, card.suit))
            # self.players[1].hand.sort(key=lambda card: (card.rank, card.suit))
            p1_card = self.players[0].hand[0]
            p2_card = self.players[1].hand[0]
            if p1_card.rank < p2_card.rank:
                self.starting_player = 0
            elif p1_card.suit < p2_card.suit and p1_card.rank == p2_card.rank:
                self.starting_player = 0
            else:
                self.starting_player = 1
        else:
            print('3+ players')
            for player in range(len(self.players)):
                self.players[player].draw(self.deck, math.floor(52 / len(self.players)))
                # player_hand.draw(self.game_deck, math.floor(52 / len(self.players)))
                for card in self.players[player].hand:
                    if card == Card(Card.RANKS[0], Card.SUITS[0]):  # If card equals '3 of Clubs'
                        self.starting_player = player
                        if len(self.players) == 3:
                            self.players[player].draw(self.deck, 1)
                self.players[player].hand.sort(key=lambda card: (card.rank, card.suit))
        self.players_dealt = True
        self.current_player = self.starting_player
        self.first_play_card = self.players[self.starting_player].hand[0]
        print(f'Starting player is: {self.current_player}')
        print(f'First card should be: {self.first_play_card}')

    def update_first_play(self):
        card = None
        starting_player = 4
        for player in self.players:
            if not (player.finish or player.quit):
                if card is None:
                    card = player.hand[0]
                    starting_player = player.player
                elif player.hand[0].rank < card.rank:
                    card = player.hand[0]
                    starting_player = player.player
                elif player.hand[0].rank == card.rank and player.hand[0].suit < card.suit:
                    card = player.hand[0]
                    starting_player = player.player
        self.first_play_card = card
        self.current_player = starting_player
        print(f"New card is {card} and starting player switched to {starting_player}")

    def update_players(self):
        self.finished_players.append(self.players[self.current_player])
        self.play_type = 0
        self.strong_play_player = 4

        print("All finished players:")
        for player in self.finished_players:
            print(f"Player {player.player}")

    def check_if_finished(self):
        current_player = self.players[self.current_player]
        if len(current_player.hand) == 0:
            current_player.finish = True
            print(f"Player {self.current_player}'s status changed to \'Finished\'")

    def pass_track(self):
        if self.current_player == self.strong_play_player:
            self.strong_play_player = 4
            self.play_type = 0
            self.reset_play()
            print("Everyone passed.")

    def set_strong_player(self):
        self.strong_play_player = self.current_player

    def reset_play(self):
        self.hand_played.clear()

    def get_play(self, index):
        self.hand_played.append(self.players[self.current_player].hand[index])

    def next_player(self):
        found_player = False

        while not found_player:
            if self.current_player == len(self.players) - 1:
                self.current_player = 0
                print("Last player. current_player index is 0")
            else:
                self.current_player += 1
                print("Incremented current_player")

            if not self.players[self.current_player].get_finish_status() and not self.players[self.current_player].quit:
                print(f"Next player is player {self.current_player}")
                found_player = True
                break

    def check_hand(self, hand):
        if (self.is_single(hand)): return 1
        if (self.is_double(hand)): return 2
        if (self.is_straight(hand)): return 3
        if (self.is_full_house(hand)): return 4
        if (self.is_fours(hand)): return 5
        if (self.is_straight_flush(hand)): return 6
        return 0

    def is_single(self, hand):
        return True if (len(hand) == 1) else False

    def is_double(self, hand):
        return True if (len(hand) == 2 and (hand[0].rank == hand[1].rank)) else False

    def is_straight(self, hand):
        strongest_straight = [3, 4, 5, 6, 15]
        if (len(hand) != 5):
            return False
        else:
            rank_set = {card.rank for card in hand}
            print(rank_set)
            if (len(rank_set) != 5):
                return False
            if (max(rank_set) - min(rank_set) == 4):
                print("Normal straight")
                return True
            elif (set(rank_set) == set(strongest_straight)):
                print("Strongest straight hand played!")
                return True
            else:
                return False

    def is_full_house(self, hand):
        if (len(hand) != 5):
            return False
        else:
            rank_set = sorted([card.rank for card in hand])
            print(rank_set)
            if (rank_set[0] == rank_set[1] and rank_set[3] == rank_set[4] and
                    (rank_set[2] == rank_set[1] or rank_set[2] == rank_set[3])):
                return True
            else:
                return False

    def is_fours(self, hand):
        if (len(hand) != 5):
            return False
        else:
            rank_set = sorted([card.rank for card in hand])
            print(rank_set)
            return True if (rank_set[0] == rank_set[3] or rank_set[1] == rank_set[4]) else False

    def is_straight_flush(self, hand):
        if (len(hand) != 5 or not self.is_straight(hand)):
            return False
        else:
            suit = hand[0].suit
            for card in hand[1:]:
                if (card.suit != suit):
                    return False
            return True

    def is_super_hand(self, hand):
        return True if (self.is_fours(hand) or self.is_straight_flush(hand)) else False

    def get_index(self, player_num):
        for index, player in enumerate(self.players):
            if player.player == player_num:
                return index
        print("Unable to find player")

    def shuffle_deck(self):
        self.deck.shuffle()

    def start(self):
        return self.ready


class Player:

    def __init__(self, player):
        self.hand = []
        self.player = player
        self.finish = False
        self.quit = False

    def __repr__(self):
        print('Player {}\'s hand:'.format(self.player))
        card_index = 0
        for card in self.hand:
            print("{}: {}".format(card_index, card))
            card_index += 1
        return ''

    def get_finish_status(self):
        return self.finish

    def remove_card(self, index):
        del self.hand[index]

    def draw(self, deck, qty):
        for quantity in range(qty):
            self.hand.append(deck.draw())

    def draw_all(self, deck):
        for card in deck:
            self.hand.append(card)

    def draw_from_index(self, index):
        card = self.hand.pop(index)
        return card

    def finish(self):
        self.finish = True

    def show_hand(self):
        card_index = 0
        for card in self.hand:
            print("{}: {}".format(card_index, card))
            card_index += 1
