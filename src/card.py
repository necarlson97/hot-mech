from src.utils import NamedClass
from src.card_steps import *

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
        Can any steps take place at all, e.g.: is it in range
        """
        any_can = any(s.can(self) for s in self.steps)
        all_mandatory = all(
            s.can(self) for s in self.steps
            if s.mandatory
        )
        return any_can and all_mandatory

    def all_can(self):
        """
        Can all steps take place at all, e.g.: is it in range
        """
        return all(s.can(self) for s in self.steps)

    def how_many_can(self):
        """
        How many steps will activate
        """
        return len([s for s in self.steps if s.can(self)])

    def cost(self):
        """
        Calculate the 'cost' of the steps, added up,
        and see how it compares to this card's heat
        """
        c = sum(s.cost() for s in self.steps)
        # Every card gets - some cost for the cost of being in the deck / drawn
        c -= 1
        # TODO take into account block potential?
        return c

    @classmethod
    def can_block(cls):
        """
        All cards can, by default, be retired to reduce incoming damage
        by their heat cost(of course, if the heat cost is 0 or negative,
        they can't)
        """
        # Lets reduce the number of cards that can be used to block
        # No attacks?
        return cls.heat > 0

    @classmethod
    def should_block(cls):
        """
        Lets have the AI smart enough to know they shouldn't get rid of all
        of their attacks
        """
        # TODO could add it as a desperate last thing
        return cls.can_block() and not cls.is_attack()

    @classmethod
    def block_explainer(cls):
        # TODO might just make it meta-rule
        return f"Retire to block {cls.heat} incoming damage"

    @classmethod
    def is_attack(cls):
        return any(isinstance(s, Attack) for s in cls.steps)

    @classmethod
    def is_move(cls):
        return any(isinstance(s, (MoveForward, MoveAway)) for s in cls.steps)

    @classmethod
    def is_control(cls):
        return not cls.is_attack() and not cls.is_move()

    # A dict that holds all defined cards by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

    def __str__(self):
        return f"{self.name} {self.heat}h {self.steps}"

"""
Below, all card types are defined:
"""
class StandardMove(Card):
    heat = 1
    steps = [Rotate(), MoveForward(0, 6)]
    flavor_text = (
        '"Step by step, gear by gear,'
        '\nwe march through metal and fear."'
        '\n— Seawell Militia Drill Song'
    )

class StandingSwivel(Card):
    heat = 1
    steps = [Rotate(0, 180)]
    flavor_text = (
        '"In the dance of death, always pirouette!"'
        '\n— Ballera, Mecha Duelist'
    )

class StepUp(Card):
    heat = 2
    steps = [Rotate(0, 90), MoveForward(0, 6, flying=True)]
    flavor_text = (
        '"When the words crumbles beneath yoU: step up, step up"'
        '\n— Excerpt from Skaldic death poem'
    )

class CombatWit(Card):
    heat = 1
    steps = [Draw()]
    flavor_text = (
        '"Only thing sharper than vibroblades - is me!"'
        '\n— Dillhung the Copper Thief'
    )

class StepBack(Card):
    heat = 0
    steps = [MoveAway(2, 6)]
    flavor_text = (
        '"The shadows are always there to welcome the wary."'
        '\n— V1ncent, Guerilla Droid'
    )

class CoolOff(Card):
    heat = -3
    steps = [EndTurn()]
    flavor_text = (
        '"To forge the strongest iron, spare the constant hammering '
        '- let it rest."'
        '\n— Old Smokey'
    )

class CookCabin(Card):
    heat = 4
    steps = [Attack(3, 6), EnemyDiscard(1)]
    flavor_text = (
        '"May our hope burn brighter than our cockpit fires!"'
        '\n— Reckles, Emberkin'
    )

class MeltSensors(Card):
    heat = 4
    steps = [EnemyDiscard(2)]
    flavor_text = (
        '"Odysseus didn\'t need to outmatch the cyclopse - only its eye."'
        '\n— Phent, Oldland Saboteur'
    )

class TorchEm(Card):
    heat = 4
    steps = [Attack(4, 6), HeatEnemy(2)]
    flavor_text = (
        '"Light them up. Let them beg for darkness."'
        '\n— Pyre, Scabland Lantern King'
    )

class LooseMissile(Card):
    heat = 3
    steps = [Attack(2, 12)]
    flavor_text = (
        '"A stray shot finds the most unexpected targets."'
        '\n— Lucy of the Steel Archers'
    )

class MissileHail(Card):
    heat = 4
    steps = [Attack(4, 18), Retire(), EndTurn()]
    flavor_text = (
        '"They may perish, but they will never forget the storm."'
        '\n— Sgt. Redborn, Artillery Angles'
    )

class ShakeItOff(Card):
    heat = -1
    steps = [Rotate(90, 180)]
    flavor_text = (
        '"Make your own cool wind!"'
        '\n— Ballera, Mecha Duelist'
    )

class JumpPack(Card):
    heat = 3
    steps = [Rotate(0, 90), MoveForward(6, 12, flying=True)]
    flavor_text = (
        '"Get the sun behind you, and fly Icarus, fly!"'
        '\n— Phent, Oldland Saboteur'
    )

class SlowItDown(Card):
    heat = -2
    steps = [Draw(), EndTurn()]
    flavor_text = (
        '"The oldest titans tread the softest."'
        '\n— Grimsmear the Unyielding'
    )

class PushOff(Card):
    heat = 2
    steps = [Attack(6, 2), MoveAway(6, 12), EndTurn()]
    flavor_text = (
        '"Give them a nudge into the abyss."'
        '\n— V1ncent, Guerilla Droid'
    )

class LaserSnapfire(Card):
    heat = 3
    steps = [Attack(2, 12), MoveForward(0, 6)]
    flavor_text = (
        '"Nuthn\' faster than searing light."'
        '\n— Pyre, Scabland Lantern King'
    )

class BlindingBurst(Card):
    heat = 2
    steps = [Attack(2, 6), ForceRotate(90)]
    flavor_text = (
        '"A brilliant display to illuminate my victory!"'
        '\n— Reckles, Emberkin'
    )

class TrackingShot(Card):
    heat = 1
    steps = [Rotate(0, 90), Attack(2, 12), Rotate(90, 90), EndTurn()]
    flavor_text = (
        '"Every target flees - but fate soon follows."'
        '\n— Sgt. Redborn, Artillery Angles'
    )

class StaggerForward(Card):
    heat = 1
    steps = [Rotate(), MoveForward(2, 6)]
    flavor_text = (
        '"When you can no longer march, fall forward."'
        '\n— Grimsmear the Unyielding'
    )

class OverdriveServos(Card):
    heat = 1
    steps = [Rotate(0, 180), MoveForward(0, 12), Retire()]
    flavor_text = (
        '"When metal screams, the battlefield sings."'
        '\n— Zuri, Pole Pos of High Torq'
    )

class DriveBy(Card):
    heat = 5
    steps = [
        MoveForward(4, 6), Rotate(0, 90), Attack(4, 12), MoveForward(4, 6),
        Retire(),
    ]
    flavor_text = (
        '"Passing by the gates of hell, we wave with guns blazing."'
        '\n— Nia, Sand Rambler'
    )

class MechanicalFuse(Card):
    heat = -3
    steps = [HurtSelf(1)]
    flavor_text = (
        '"Mortality is law. For all life. For all machines."'
        '\n— Segg, Digital Deacon'
    )

class RememberTraining(Card):
    heat = 1
    steps = [Unretire(), EndTurn()]
    flavor_text = (
        '"Cacophony on the battlefield, symphony in my mind."'
        '\n— Allison the Deadhand'
    )

class DoItRight(Card):
    heat = 1
    steps = [Unretire(), Retire()]
    flavor_text = (
        '"In here, you don\'t get to fail twice."'
        '\n— Seawell Pilot\'s guide'
    )

class HeavyLead(Card):
    heat = 4
    steps = [Attack(6, 12, 6)]
    flavor_text = (
        '"Every shot fired leaves a wake."'
        '\n— Carving on Thunder Fortress walls'
    )

class SupressingFire(Card):
    heat = 5
    steps = [Attack(3, 12), MoveAway(4, 6), Rotate(0, 90)]
    flavor_text = (
        '"Remember ocean waves.\n'
        'Their fire will crescendo, crest, and break. '
        'Then, we move."'
        '\n— Cpt. Cho Chun, Seawell Militia'
    )

class SweepingBarrage(Card):
    heat = 4
    steps = [Rotate(0, 180), Attack(6, 18, 6), Retire(), EndTurn()]
    flavor_text = (
        '"Sow the breeze will lead, reap the windfall of victory."'
        '\n— Poorly translated Sand Rambler saying'
    )

class PushForward(Card):
    heat = 0
    steps = [MoveForward(6, 12, flying=True)]
    flavor_text = (
        '"Unfaltering, unyielding; the future awaits beyond the fray."'
        '\n— Commander Vael, Frontline Seer'
    )

class KeepTempo(Card):
    heat = 1
    steps = [Rotate(0, 180), MoveForward(6, 12), Draw(), EndTurn()]
    flavor_text = (
        '"Don\'t fall behind. My thunder will be chasing you."'
        '\n— Sgt. Redborn, Artillery Angles'
    )

class ChartStudy(Card):
    heat = 1
    steps = [Rotate(0, 180), MoveForward(0, 12), EndTurn()]
    flavor_text = (
        '"The ruins speak. They will whisper victory. So listen."'
        '\n— Therra, the Geo-Savant'
    )

class RecallWisdom(Card):
    heat = -1
    steps = [Draw(), EndTurn()]
    flavor_text = (
        '"War. War never changes."'
        '\n— Unknown'
    )

class SurveyLandscape(Card):
    heat = -2
    steps = [Rotate(0, 180), EndTurn()]
    flavor_text = (
        '"We fight, because this is our land.'
        '\nWe win, because we know our home."'
        '\n— Cpt. Cho Chun, Seawell Militia'
    )

class RipVitals(Card):
    heat = 4
    steps = [Attack(8, 2)]
    flavor_text = (
        '"KILL THE THING!"'
        '\n— Unnamed Scablander, last words'
    )

class HatefulGlare(Card):
    heat = -1
    steps = [MandatoryRange(6, 12), Rotate(0, 180)]
    flavor_text = (
        '"An eye for scrutiny, and a taste for pain."'
        '\n— Xandar, Techblade'
    )

class BoastChallenge(Card):
    heat = -6
    steps = [MandatoryRange(6), EndTurn()]
    flavor_text = (
        '"Yes, I\', a deadman. But you\'re first!"'
        '\n— Reckles, Emberkin'
    )

class TargetedStrike(Card):
    heat = 1
    steps = [Attack(3, 6, 12)]
    flavor_text = (
        '"A ticket home is a trigger pull away."'
        '\n— Excerpt of the Marksman Creed'
    )

class GiddyRetreat(Card):
    heat = 1
    steps = [Rotate(0, 180), MoveForward(0, 12), RotateAway()]
    flavor_text = (
        '"Alive without breath, cold as death,'
        '\noutrun sorrow, flee into tomorrow!"'
        '\n— Rictus, the Iron Jester'
    )

class CoverEyes(Card):
    heat = -3
    steps = [Draw(), Discard(), Retire()]
    flavor_text = (
        '"The only salve for true terror, is blindness."'
        '\n— V1ncent, Guerilla Droid'
    )

class DriveHarder(Card):
    heat = 2
    steps = [Rotate(0, 90), MoveForward(0, 6), Draw()]
    flavor_text = (
        '"Pinkheads give me limits, and I break \'em!'
        '\nBlackfingers repair me mech... And I break \'em!"'
        '\n— Pyre, Scabland Lantern King'
    )

class LightningInspiration(Card):
    heat = 2
    steps = [Rotate(0, 180), MoveForward(0, 12), Draw(), Retire()]
    flavor_text = (
        '"Flash of genius, followed by the thunder of guns!"'
        '\n— Nia, Sand Rambler'
    )

class BlissfulIgnorance(Card):
    heat = -3
    steps = [Discard(2)]
    flavor_text = (
        '"Serenity IS the weapon."'
        '\n— Trippple, CleanDisk Monk'
    )

class SlowSizzle(Card):
    heat = -2
    steps = []
    flavor_text = (
        '"Patience? Time is an oven that cooks all alive!"'
        '\n— Reckles, Emberkin'
    )

class JettisonHeatsinks(Card):
    heat = -5
    steps = [Discard(), Retire()]
    flavor_text = (
        '"The day you don\'t come to me for repairs, '
        '\nI\'ll know to light the crematorium."'
        '\n— Lizz, Foreman of the Rustring Blackfingers'
    )

class SteamBlowoff(Card):
    heat = -3
    steps = [EndTurn()]
    flavor_text = (
        '"Arched back, a wet hiss.'
        '\nTheir Shots miss, into the mist! "'
        '\n— Rictus, the Iron Jester'
    )

class TakeReading(Card):
    heat = -1
    steps = [Rotate(90)]
    flavor_text = (
        '"Look. Listen. Never rely on the tech.'
        '\nYou\'ll be dead before the radar pings."'
        '\n— Lucy of the Steel Archers'
    )

class LockOn(Card):
    heat = 2
    steps = [IncreaseRange(6)]
    flavor_text = (
        '"I\'ve carved your name on every warhead."'
        '\n— The Calculator'
    )

class JoltForward(Card):
    heat = 1
    steps = [
        Rotate(90), MoveForward(10, 12, flying=True), Rotate(90, 90)]
    flavor_text = (
        '"Blink and I\'ll gut yeh."'
        '\n— Dillhung the Copper Thief'
    )

class BlastOff(Card):
    heat = 0
    steps = [
        Rotate(90), MoveForward(12, 24, flying=True), Retire()]
    flavor_text = (
        '"Let\'s make the hawks jealous, and the vultures hungry."'
        '\n— Jaggek, Rustring Enforcer'
    )
# Unused flavor text:
"""
Extraordinary technology brings extraordinary recklessness
"One man's “magic” is another man's engineering".
"Science is about knowing; engineering is about doing"
"""

# Unused card ideas:
"""
Fists up - -2 heat, 2" range 2 dmg, end turn
Madman Theory - something random
Rushing Wind - -2 heat, move 6-12"
Wargasm - attack, hurt self, draw card
Sentient Cruise Missie
"""
