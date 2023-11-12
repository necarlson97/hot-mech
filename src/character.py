class Character:
    """
    Abstract class, that each specific type of character will sub-class
    Then each instance of a character is the individual game's character,
    which has a specific game_state/cards, etc
    """
    card_types = []

    def __init__(self, game_state, player):
        self.name = "".join(
            filter(lambda c: c.isupper(), self.__class__.__name__)
        )
        self.cards = [card() for card in self.card_types]

    # A dict that holds all defined subclasses by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

"""
Below, all characters are defined:
"""
class NamelessDegenerate(Character):
    card_types = []
