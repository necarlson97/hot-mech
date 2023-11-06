import random
import logging
logger = logging.getLogger("HotMech")

import src.card as cards

class Mech:
    """
    Abstract class, that each specific type of mech will sub-class
    Then each instance of a subclass is the individual game's mech,
    which has a specific game_state/player/enemy, etc, and can be killed
    """

    max_hp = 20
    hard_points = 2
    card_types = []

    # Min of 1, max of 6
    # as it is counted with a d6
    heat = 1

    def __init__(self, game_state, player):
        self.name = self.__class__.__name__
        self.player = player
        self.hp = self.max_hp
        self.cards = [
            card(game_state, player)
            for card in self.card_types
        ]

    def check_heat(self):
        """
        Check if mech 'overheats'
        """
        if self.heat > 6:
            self.heat = 6
            melt_dmg = random.randint(0, 6)
            self.heat -= melt_dmg
            self.hp -= melt_dmg
            logger.info(f"{self.name} overheated for {melt_dmg}")
            self.player.end_turn()
        if self.heat < 1:
            self.heat = 1

    # A dict that holds all defined subclasses by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

"""
All mechs defined below
"""
class Sandpiper(Mech):
    max_hp = 15
    hard_points = 3
    # TODO
    card_types = [
        cards.StandardMove,
        cards.StandardMove,
        cards.ShakeItOff,
        cards.StepUp,
        cards.StepUp,
        cards.JumpPack,
        cards.JumpPack,
        cards.SlowItDown,
        cards.PushOff,
        cards.CoolOff,
        cards.CoolOff,
        cards.LaserSnapfire,
        cards.LaserSnapfire,
        cards.BlindingBurst,
        cards.BlindingBurst,
        cards.TrackingShot,
    ]

class Thermo(Mech):
    max_hp = 20
    hard_points = 2
    # TODO
    card_types = [
        cards.StandardMove,
        cards.StandardMove,
        cards.StandingSwivel,
        cards.StandingSwivel,
        cards.StepUp,
        cards.StepUp,
        cards.CombatWit,
        cards.CombatWit,
        cards.StepBack,
        cards.StepBack,
        cards.CoolOff,
        cards.CoolOff,
        cards.CookCabin,
        cards.CookCabin,
        cards.MeltSensors,
        cards.TorchEm,
    ]

class Hauler(Mech):
    max_hp = 25
    hard_points = 2
    # TODO
    card_types = [
        cards.StaggerForward,
        cards.StaggerForward,
        cards.LooseMissile,
        cards.LooseMissile,
        cards.MissileHail,
    ]

class Skeleton(Mech):
    # Mostly for tests
    max_hp = 10
    hard_points = 2
    card_types = []
