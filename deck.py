from card import Card
import random
import pygame


class Deck:

    def __init__(self):
        self.deck = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.deck.append(Card(rank, suit))

    def __repr__(self):
        card_index = 0
        for card in self.deck:
            print(f'{card_index}: {card}')
            card_index += 1
        return ''

    def show(self):
        for card in self.deck:
            print(card)

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        return self.deck.pop()

    def place_at_top(self, card):
        self.deck.append(card)

    def place_at_bottom(self, card):
        self.deck.insert(card, 0)
