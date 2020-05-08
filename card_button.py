from button import Button


class CardButton(Button):

    def is_at_diff_pos(self):
        """
        Checks whether the card button was selected
        :return:
        """
        if self.y != self.initial_y:
            return True
        else:
            return False

    def reset_pos(self):
        """
        Returns card to its original position in the hand
        """
        self.y = self.initial_y

    def update_x(self, x):
        self.x = x

    def update_width(self, width, card_width):
        if width > card_width:
            self.width = card_width
        else:
            self.width = width