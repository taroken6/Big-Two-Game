from button import Button


class JoinButton(Button):
    def set_key(self, key):
        """
        Sets button's key to a lobby
        :param key:
        :return:
        """
        self.key = key

    def get_key(self):
        """
        Gets key to joined lobby
        :return:
        """
        return self.key