import src.card as cards
from src.utils import NamedClass


class Upgrade(NamedClass):
    card_types = []

    def __init__(self, game_state, player):
        self.cards = [card(game_state, player) for card in self.card_types]

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

class EjectableHeatsink(Upgrade):
    card_types = [
        cards.SlowSizzle,
        cards.SlowSizzle,
        cards.JettisonHeatsinks
    ]

class RhodiumRadiators(Upgrade):
    card_types = [
        cards.SlowSizzle,
        cards.SlowSizzle,
        cards.SteamBlowoff
    ]

class SensorArray(Upgrade):
    card_types = [
        cards.TakeReading,
        cards.TakeReading,
        cards.LockOn,
        cards.LockOn,
    ]

class Misslepod(Upgrade):
    card_types = [
        cards.LooseMissile,
        cards.LooseMissile,
        cards.MissileHail,
        cards.MissileHail,
    ]

class SolidBoosters(Upgrade):
    card_types = [
        cards.JoltForward,
        cards.JoltForward,
        cards.BlastOff,
    ]

"""
class TODO(Upgrade):
    card_types = [
        cards.todo,
        cards.todo,
        cards.todo,
        cards.todo,
    ]
"""
