from src.utils import NamedClass
# Ugly shorthand - but it is used so frequently here,
# I will allow it for now
import src.card_steps as s

import logging
logger = logging.getLogger("HotMech")


class Card(NamedClass):
    """
    Abstract class, that each specific type of card will sub-class
    Then each instance of a subclass is the individual card,
    which has a specific game_state/player/enemy, etc, and can be 'retired'
    """

    # Steps defined by the subclass type.
    # A list of 'Step' types, that get initialized
    # to create this individual card's steps
    steps = []

    # How much heat does this contribute to the mech
    heat = 1

    def __init__(self, game_state, player):
        self.game_state = game_state
        self.player = player

    def play(self):
        self.player.mech.heat += self.heat
        for step in self.steps:
            step.play(self)

    def should(self):
        """
        Can this card be played without overheating
        """
        if self.player.mech.heat + self.heat > 6:
            return False
        return self.can()

    def can(self):
        """
        Can this step take place at all, e.g.: is it in range
        """
        return all(s.can(self) for s in self.steps)

    def cost(self):
        """
        Calculate the 'cost' of the steps, added up,
        and see how it compares to this card's heat
        """
        c = sum(s.cost() for s in self.steps)
        # Every card gets - some cost for the cost of being in the deck / drawn
        c -= 1
        return c

    # A dict that holds all defined cards by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

"""
Below, all card types are defined:
"""
class StandardMove(Card):
    heat = 1
    steps = [s.Rotate(), s.MoveForward(0, 6)]
    flavor_text = (
        '"Step by step, gear by gear, we march through metal and fear."'
        '\n— Seawell Militia Drill Song'
    )

class StandingSwivel(Card):
    heat = 1
    steps = [s.Rotate(0, 180)]
    flavor_text = (
        '"In the dance of death, always pirouette!"'
        '\n— Ballera, Mecha Duelist'
    )

class StepUp(Card):
    heat = 2
    steps = [s.Rotate(0, 90), s.MoveForward(0, 6, ignore_terrrain=True)]
    flavor_text = (
        '"When the words crumbles beneath yoU: step up, step up"'
        '\n— Excerpt from Skaldic death poem'
    )

class CombatWit(Card):
    heat = 1
    steps = [s.Draw()]
    flavor_text = (
        '"Only thing sharper than vibroblades - is me!"'
        '\n— Dillhung the Copper Thief'
    )

class StepBack(Card):
    heat = -2
    steps = [s.MoveAway(2, 6)]
    flavor_text = (
        '"The shadows are always there to welcome the wary."'
        '\n— V1ncent, Guerilla Droid'
    )

class CoolOff(Card):
    heat = -4
    steps = [s.EndTurn()]
    flavor_text = (
        '"To forge the strongest iron, spare the constant hammering '
        '- let it rest."'
        '\n— Old Smokey'
    )

class CookCabin(Card):
    heat = 3
    steps = [s.Attack(5, 6), s.EnemyDiscard(1)]
    flavor_text = (
        '"May our hope burn brighter than our cockpit fires!"'
        '\n— Reckles, Emberkin'
    )

class MeltSensors(Card):
    heat = 3
    steps = [s.EnemyDiscard(2)]
    flavor_text = (
        '"Odysseus didn\'t need to outmatch the cyclopse - only its eye."'
        '\n— Phent, Oldland Saboteur'
    )

class TorchEm(Card):
    heat = 3
    steps = [s.Attack(2, 12), s.HeatEnemy(2)]
    flavor_text = (
        '"Light them up. Let them beg for darkness."'
        '\n— Pyre, Scabland Lantern King'
    )

class LooseMissile(Card):
    heat = 1
    steps = [s.Attack(2, 12)]
    flavor_text = (
        '""A stray shot finds the most unexpected targets."'
        '\n— Lucy of the Steel Archers'
    )

class MissileHail(Card):
    heat = 3
    steps = [s.Attack(4, 18), s.Retire()]
    flavor_text = (
        '"They may perish, but they will never forget the storm."'
        '\n— Sgt. Redborn, Artillery Angles'
    )

class ShakeItOff(Card):
    heat = -1
    steps = [s.Rotate(90, 180)]
    flavor_text = (
        '"Make your own cool wind!"'
        '\n— Ballera, Mecha Duelist'
    )

class JumpPack(Card):
    heat = 3
    steps = [s.Rotate(0, 90), s.MoveForward(6, 12, ignore_terrrain=True)]
    flavor_text = (
        '"Get the sun behind you, and fly Icarus, fly!"'
        '\n— Phent, Oldland Saboteur'
    )

class SlowItDown(Card):
    heat = -2
    steps = [s.Draw(), s.EndTurn()]
    flavor_text = (
        '"The oldest titans tread the softest."'
        '\n— Grimsmear the Unyielding'
    )

class PushOff(Card):
    heat = 1
    steps = [s.Attack(6, 2), s.MoveAway(6, 12)]
    flavor_text = (
        '"Give them a nudge into the abyss."'
        '\n— V1ncent, Guerilla Droid'
    )

class LaserSnapfire(Card):
    heat = 2
    steps = [s.Attack(3, 12), s.MoveForward(0, 2)]
    flavor_text = (
        '"Nuthn\' faster than searing light."'
        '\n— Pyre, Scabland Lantern King'
    )

class BlindingBurst(Card):
    heat = 3
    steps = [s.Attack(5, 6), s.ForceRotate(90)]
    flavor_text = (
        '"A brilliant display to illuminate my victory!"'
        '\n— Reckles, Emberkin'
    )

class TrackingShot(Card):
    heat = 2
    steps = [s.Rotate(0, 90), s.Attack(2, 12), s.Rotate(0, 90)]
    flavor_text = (
        '"Every target flees - but fate soon follows."'
        '\n— Sgt. Redborn, Artillery Angles'
    )

class StaggerForward(Card):
    heat = 1
    steps = [s.Rotate(), s.MoveForward(2, 6)]
    flavor_text = (
        '"When you can no longer march, fall forward."'
        '\n— Grimsmear the Unyielding'
    )

class OverdriveServos(Card):
    heat = 1
    steps = [s.Rotate(0, 180), s.MoveForward(0, 12), s.Retire()]
    flavor_text = (
        '"When metal screams, the battlefield sings."'
        '\n— Zuri, Pole Pos of High Torq'
    )

class DriveBy(Card):
    heat = 3
    steps = [
        s.MoveForward(2, 6), s.Rotate(0, 180),
        s.Attack(4, 12), s.MoveForward(2, 6),
        s.Retire()
    ]
    flavor_text = (
        '"Passing by the gates of hell, we wave with guns blazing."'
        '\n— Nia, Sand Rambler'
    )

class MechanicalFuse(Card):
    heat = -3
    steps = [s.HurtSelf(2)]
    flavor_text = (
        '"Mortality is law. For all life. For all machines."'
        '\n— Segg, Digital Deacon'
    )

class RememberTraining(Card):
    heat = 0
    steps = [s.Unretire(), s.EndTurn()]
    flavor_text = (
        '"Cacophony on the battlefield, symphony in my mind."'
        '\n— Allison the Deadhand'
    )

class DoItRight(Card):
    heat = 0
    steps = [s.Unretire(), s.Retire()]
    flavor_text = (
        '"In here, you don\'t get to fail twice."'
        '\n— Seawell Pilot\'s guide'
    )

class HeavyLead(Card):
    heat = 2
    steps = [s.Attack(6, 12, 6)]
    flavor_text = (
        '"Every shot fired leaves a wake."'
        '\n— Carving on Thunder Fortress walls'
    )

class SupressingFire(Card):
    heat = 4
    steps = [s.Attack(4, 12), s.MoveAway(2, 6), s.Rotate(0, 90)]
    flavor_text = (
        '"Remember ocean waves. '
        'Their fire will crescendo, crest, and break. '
        'Only then, we move."'
        '\n— Cpt. Cho Chun, Seawell Militia'
    )

class SweepingBarrage(Card):
    heat = 4
    steps = [
        s.Rotate(0, 180), s.Attack(8, 18, 6),
        s.Retire(), s.EndTurn()
    ]
    flavor_text = (
        '"Sow the breeze will lead, reap the windfall of victory."'
        '\n— Poorly translated Sand Rambler saying'
    )

class PushForward(Card):
    heat = 0
    steps = [s.MoveForward(6, 12, ignore_terrrain=True)]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class RushingWind(Card):
    heat = 0
    steps = [s.Rotate(0, 180), s.MoveForward(6, 12), s.Draw(), s.EndTurn()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class ChartStudy(Card):
    heat = 2
    steps = [s.Rotate(0, 180), s.MoveForward(0, 12), s.EndTurn()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class RecallWisdom(Card):
    heat = -1
    steps = [s.Draw(), s.EndTurn()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class SurveyLandscape(Card):
    heat = -2
    steps = [s.Rotate(0, 180), s.EndTurn()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class RipVitals(Card):
    heat = 3
    steps = [s.Attack(12, 2)]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class HatefulGlare(Card):
    heat = -1
    steps = [s.RangeCheck(12, step=s.Rotate(0, 180))]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class BoastChallenge(Card):
    heat = -3
    steps = [s.RangeCheck(6, step=s.EndTurn())]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class TargetedStrike(Card):
    heat = 1
    steps = [s.Attack(2, 6, 12)]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class GiddyRetreat(Card):
    heat = -2
    steps = [s.Rotate(0, 180), s.MoveForward(0, 12), s.RotateAway()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class CoverEyes(Card):
    heat = -2
    steps = [s.Draw(), s.Discard(), s.EndTurn()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class DriveHarder(Card):
    heat = 2
    steps = [s.Rotate(0, 90), s.MoveForward(0, 6), s.Draw()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class LightningInspiration(Card):
    heat = 3
    steps = [s.Rotate(0, 90), s.MoveForward(0, 12), s.Draw(), s.EndTurn()]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )

class BlissfulIgnorance(Card):
    heat = -3
    steps = [s.Discard(2)]
    flavor_text = (
        '"TODO"'
        '\n— TODO'
    )
# Unused flavor text:
"""
Extraordinary technology brings extraordinary recklessness
"One man's “magic” is another man's engineering".
"Science is about knowing; engineering is about doing"
"""
