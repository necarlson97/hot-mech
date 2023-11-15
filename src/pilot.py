import src.card as cards
from src.utils import NamedClass

import logging
logger = logging.getLogger("HotMech")

class Pilot(NamedClass):
    """
    Abstract class, that each specific type of pilot will sub-class
    Then each instance of a pilot is the individual game's pilot,
    which has a specific game_state/cards, etc
    """
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
Below, all pilots are defined:
"""
class NamelessDegenerate(Pilot):
    card_types = []

class ValorantStrider(Pilot):
    card_types = [
        cards.PushForward,
        cards.PushForward,
        cards.StandingSwivel,
        cards.KeepTempo,
    ]

class LearnedTactician(Pilot):
    card_types = [
        cards.ChartStudy,
        cards.ChartStudy,
        cards.RecallWisdom,
        cards.SurveyLandscape,
    ]

class VeteranOfWrath(Pilot):
    card_types = [
        cards.RipVitals,
        cards.RipVitals,
        cards.HatefulGlare,
        cards.BoastChallenge,
    ]

class WileyScavenger(Pilot):
    card_types = [
        cards.TargetedStrike,
        cards.TargetedStrike,
        cards.GiddyRetreat,
        cards.CoverEyes,
    ]

class BeguiledZealot(Pilot):
    card_types = [
        cards.DriveHarder,
        cards.DriveHarder,
        cards.LightningInspiration,
        cards.BlissfulIgnorance,
    ]
