import src.card as cards
from src.utils import NamedClass


class Upgrade(NamedClass):
    card_types = []

    def __init__(self, game_state, player):
        self.cards = [card() for card in self.card_types]

    # A dict that holds all defined cards by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

"""
Below, all upgrades are defined:
"""
class Tassles(Upgrade):
    card_types = []
