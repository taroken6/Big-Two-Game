class Card:
    RANKS = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    SUITS = ("Club", "Diamond", "Heart", "Spade")

    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        if self.rank == 15:
            rank = 2
        elif self.rank == 14:
            rank = 'Ace'
        elif self.rank == 13:
            rank = 'King'
        elif self.rank == 12:
            rank = 'Queen'
        elif self.rank == 11:
            rank = 'Jack'
        else:
            rank = self.rank

        return "{} of {}s".format(rank, self.suit)

    def __eq__(self, other):
        if not isinstance(other, Card):  # Don't attempt if not same type
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return hash(str(self))

    def get_rank(self):
        return self.rank

    def get_suit(self):
        return self.suit
