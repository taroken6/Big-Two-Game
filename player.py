from deck import Deck
from card import Card

class Player:

    def __init__(self, player):
        self.hand = []
        self.player = player
        self.finish = False

    def __repr__(self):
        print('Player {}\'s hand:'.format(self.player))
        card_index = 0
        for card in self.hand:
            print("{}: {}".format(card_index, card))
            card_index += 1
        return ''

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