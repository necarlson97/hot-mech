import logging
logger = logging.getLogger("HotMech")

from src.utils import camel_to_hypens, snake_to_title

class Card:
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

    def __new__(cls, *args, **kwargs):
        cls.name = camel_to_hypens(cls.__name__)
        instance = super().__new__(cls)
        return instance

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

    @classmethod
    def human_name(cls):
        return snake_to_title(cls.name)

    # A dict that holds all defined cards by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

    # TODO I want to define a way to calculate the
    # 'cost' of each step, and thus see if each card's
    # individual pieces are balanced with its heat

    def __str__(self):
        return f"{self.name} {self.steps}"
    def __repr__(self):
        return self.__str__()

class Step:
    """
    Abstract class, that each specific type of step will sub-class.
    Then each instance of a subclass is a step on a card,
    with the parameters it uses (e.g. 'Move' with '0-6"')
    """

    def play(self, card):
        pass

    def can(self, card):
        """
        Can this step take place at all, e.g.: is it in range
        """
        return True

    def cost(self):
        """
        How 'good' is this step - will depend on it's specific
        params (like how generous is the range, how much dmg, etc)
        """
        raise NotImplemented()

    def x_cards(self):
        """
        Just a helpful plurilization shorthand for 'a card' vs 'x cards'
        """
        return (
            "a card" if self.number_of_cards < 2
            else f"{self.number_of_cards} cards"
        )

    def __str__(self):
        public_attrs = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }
        return f"{self.__class__.__name__} {public_attrs}"
    def __repr__(self):
        return self.__str__()

"""
Below, all step types are defined:
"""
class MoveForward(Step):
    def __init__(self, min_move=0, max_move=6, ignore_terrrain=False):
        self.min = min_move
        self.max = max_move
        self.ignore_terrrain = ignore_terrrain

    def play(self, card):
        card.player.move_toward(self.max, self.min, self.ignore_terrrain)
        # logger.info(f"Moved {card.player} to {card.player.location}")

    def explainer(self):
        return (
            f"Move forward {self.min}-{self.max}\""
            + (", ignoring terrain" if self.ignore_terrrain else "")
        )

    def cost(self):
        c = (self.max - self.min) / 6
        if self.ignore_terrrain:
            c *= 2
        return int(c)

class MoveAway(Step):
    def __init__(self, min_move=0, max_move=6):
        self.min = min_move
        self.max = max_move

    def play(self, card):
        card.player.move_away(self.max, self.min)
        # logger.info(f"Moved away {card.player} to {card.player.location}")

    def explainer(self):
        return (
            f"Move away "
            f"{self.min}-{self.max}\""
        )

    def cost(self):
        return (self.max // 6) - (self.min // 6) - 1

class Rotate(Step):
    def __init__(self, min_rot=0, max_rot=90):
        self.min = min_rot
        self.max = max_rot
        if self.max > 180:
            self.max = 180

    def play(self, card):
        card.player.rotate_towards(self.max, self.min)
        # logger.info(f"Rotated {card.player} to {card.player.rotation}")

    def explainer(self):
        return (
            f"Rotate +/- {self.min}°-{self.max}°"
        )

    def cost(self):
        return (self.max // 90) - (self.min // 90)

class ForceRotate(Step):
    def __init__(self, rotation=90):
        self.rotation = rotation

    def play(self, card):
        enemy = card.player.get_enemy()
        enemy.rotate(90)
        logger.info(f"Forcefully rotated {enemy} to {enemy.rotation}")

    def explainer(self):
        return (
            f"Rotate the enemy {self.rotation}° right"
        )

    def cost(self):
        return self.rotation // 90

class Attack(Step):
    def __init__(self, damage=4, max_range=6, min_range=0):
        self.max = max_range
        self.min = min_range
        self.damage = damage

    def play(self, card):
        if card.player.facing_toward_enemy() and self.can(card):
            card.game_state.damage_enemy(card.player, self.damage)
            logger.info(f"Attacked for {self.damage}")

    def can(self, card):
        """
        Is enemy in range
        """
        return card.player.in_range(self.min, self.max)

    def explainer(self):
        return (
            f"If within {self.min}-{self.max}\", deal {self.damage} damage"
        )

    def cost(self):
        usable_range = self.max / 3 - self.min / 3
        dmg_mult = self.damage / 3
        return int(usable_range * dmg_mult)

class Retire(Step):
    def play(self, card):
        card.player.discard.remove(card)
        card.player.retired.append(card)

    def explainer(self):
        return (
            f"Retire this card"
        )

    def cost(self):
        return -3

class Unretire(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            if not self.can(card):
                return
            unretired = card.player.sorted_cards(card.player.retired)[0]
            card.player.retired.remove(unretired)
            card.player.hand.append(unretired)

    def explainer(self):
        return (
            f"Choose a 'retired' card, and return it to your hand"
        )

    def can(self, card):
        return len(card.player.retired) >= self.number_of_cards

    def cost(self):
        return 3 * self.number_of_cards

class Draw(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            card.player.draw_card()

    def explainer(self):
        return f"Draw {self.x_cards()}"

    def cost(self):
        return 2 * self.number_of_cards

class EndTurn(Step):
    def play(self, card):
        card.player.end_turn()

    def explainer(self):
        return (
            f"End your turn"
        )

    def cost(self):
        return -3

class EnemyDiscard(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            card.player.get_enemy().throw_away()

    def can(self, card):
        return len(card.player.get_enemy().hand) >= self.number_of_cards

    def explainer(self):
        return (
            f"Enemy must discard {self.x_cards()}"
        )

    def cost(self):
        return 2 * self.number_of_cards

class HeatEnemy(Step):
    def __init__(self, heat=1):
        self.heat = heat

    def play(self, card):
        card.player.get_enemy().mech.heat += self.heat

    def explainer(self):
        return (
            f"Enemy heats up {self.heat}"
        )

    def cost(self):
        return self.heat

class HurtSelf(Step):
    def __init__(self, damage):
        self.damage = damage

    def play(self, card):
        card.player.mech.hp -= self.damage

    def explainer(self):
        return (
            f"Deal {self.damage} damage to yourself"
        )

    def cost(self):
        return -self.damage // 2

"""
Below, all card types are defined:
"""
class StandardMove(Card):
    heat = 1
    steps = [Rotate(), MoveForward(0, 6)]
    flavor_text = (
        '"Step by step, gear by gear, we march through metal and fear."'
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
    steps = [Rotate(0, 90), MoveForward(0, 6, ignore_terrrain=True)]
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
    heat = -2
    steps = [MoveAway(2, 6)]
    flavor_text = (
        '"The shadows are always there to welcome the wary."'
        '\n— V1ncent, Guerilla Droid'
    )

class CoolOff(Card):
    heat = -4
    steps = [EndTurn()]
    flavor_text = (
        '"To forge the strongest iron, spare the constant hammering '
        '- let it rest."'
        '\n— Old Smokey'
    )

class CookCabin(Card):
    heat = 3
    steps = [Attack(5, 6), EnemyDiscard(1)]
    flavor_text = (
        '"May our hope burn brighter than our cockpit fires!"'
        '\n— Reckles, Emberkin'
    )

class MeltSensors(Card):
    heat = 3
    steps = [EnemyDiscard(2)]
    flavor_text = (
        '"Odysseus didn\'t need to outmatch the cyclopse - only its eye."'
        '\n— Phent, Oldland Saboteur'
    )

class TorchEm(Card):
    heat = 3
    steps = [Attack(2, 12), HeatEnemy(2)]
    flavor_text = (
        '"Light them up. Let them beg for darkness."'
        '\n— Pyre, Scabland Lantern King'
    )

class LooseMissile(Card):
    heat = 1
    steps = [Attack(2, 12)]
    flavor_text = (
        '""A stray shot finds the most unexpected targets."'
        '\n— Lucy of the Steel Archers'
    )

class MissileHail(Card):
    heat = 3
    steps = [Attack(4, 18), Retire()]
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
    steps = [Rotate(0, 90), MoveForward(6, 12, ignore_terrrain=True)]
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
    heat = 1
    steps = [Attack(6, 2), MoveAway(6, 12)]
    flavor_text = (
        '"Give them a nudge into the abyss."'
        '\n— V1ncent, Guerilla Droid'
    )

class LaserSnapfire(Card):
    heat = 2
    steps = [Attack(3, 12), MoveForward(0, 2)]
    flavor_text = (
        '"Nuthn\' faster than searing light."'
        '\n— Pyre, Scabland Lantern King'
    )

class BlindingBurst(Card):
    heat = 3
    steps = [Attack(5, 6), ForceRotate(90)]
    flavor_text = (
        '"A brilliant display to illuminate my victory!"'
        '\n— Reckles, Emberkin'
    )

class TrackingShot(Card):
    heat = 2
    steps = [Rotate(0, 90), Attack(2, 12), Rotate(0, 90)]
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
    heat = 3
    steps = [
        MoveForward(2, 6), Rotate(0, 180), Attack(4, 12), MoveForward(2, 6),
        Retire()
    ]
    flavor_text = (
        '"Passing by the gates of hell, we wave with guns blazing."'
        '\n— Nia, Sand Rambler'
    )

class MechanicalFuse(Card):
    heat = -3
    steps = [HurtSelf(2)]
    flavor_text = (
        '"Mortality is law. For all life. For all machines."'
        '\n— Segg, Digital Deacon'
    )

class RememberTraining(Card):
    heat = 0
    steps = [Unretire(), EndTurn()]
    flavor_text = (
        '"Cacophony on the battlefield, symphony in my mind."'
        '\n— Allison the Deadhand'
    )

class DoItRight(Card):
    heat = 0
    steps = [Unretire(), Retire()]
    flavor_text = (
        '"In here, you don\'t get to fail twice."'
        '\n— Seawell Pilot\'s guide'
    )

class HeavyLead(Card):
    heat = 2
    steps = [Attack(6, 12, 6)]
    flavor_text = (
        '"Every shot fired leaves a wake."'
        '\n— Carving on Thunder Fortress walls'
    )

class SupressingFire(Card):
    heat = 4
    steps = [Attack(4, 12), MoveAway(2, 6), Rotate(0, 90)]
    flavor_text = (
        '"Remember ocean waves. '
        'Their fire will crescendo, crest, and break. '
        'Only then, we move."'
        '\n— Cpt. Cho Chun, Seawell Militia'
    )

class SweepingBarrage(Card):
    heat = 4
    steps = [Rotate(0, 180), Attack(8, 18, 6), Retire(), EndTurn()]
    flavor_text = (
        '"Sow the breeze will lead, reap the windfall of victory."'
        '\n— Poorly translated Sand Rambler saying'
    )

# Unused flavor text:
"""
Extraordinary technology brings extraordinary recklessness
"One man's “magic” is another man's engineering".
"Science is about knowing; engineering is about doing"
"""
