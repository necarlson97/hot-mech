import logging
logger = logging.getLogger("HotMech")

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

    def __init__(self, game_state, player):
        self.name = self.__class__.__name__
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
        logger.info(f"Moved {card.player} to {card.player.location}")

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
        logger.info(f"Moved away {card.player} to {card.player.location}")

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
        logger.info(f"Rotated {card.player} to {card.player.rotation}")

    def cost(self):
        return (self.max // 90) - (self.min // 90)

class ForceRotate(Step):
    def __init__(self, rotation=90):
        self.rotation = rotation

    def play(self, card):
        enemy = card.player.get_enemy()
        enemy.rotate(90)
        logger.info(f"Forcefully rotated {enemy} to {enemy.rotation}")

    def cost(self):
        return self.rotation // 90

class Attack(Step):
    def __init__(self, damedge=4, max_range=6, min_range=0):
        self.max = max_range
        self.min = min_range
        self.damedge = damedge

    def play(self, card):
        logger.info(
            f"Trying to attack: "
            f"{self.can(card)} {round(card.player.distance_to_enemy())} in "
            f"[{self.min},{self.max}] "
            f"{card.player.facing_toward_enemy()} "
            f"({round(card.player.rotation)}°)"
        )
        if card.player.facing_toward_enemy() and self.can(card):
            card.game_state.damage_enemy(card.player, self.damedge)
            logger.info(f"Attacked for {self.damedge}")

    def can(self, card):
        """
        Is enemy in range
        """
        return card.player.in_range(self.min, self.max)

    def cost(self):
        usable_range = self.max / 3 - self.min / 3
        dmg_mult = self.damedge / 3
        return int(usable_range * dmg_mult)

class Retire(Step):
    def play(self, card):
        card.player.discard.remove(card)
        card.player.retired.append(card)

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

    def cost(self):
        return 2 * self.number_of_cards

class EndTurn(Step):
    def play(self, card):
        card.player.end_turn()

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

    def cost(self):
        return 2 * self.number_of_cards

class HeatEnemy(Step):
    def __init__(self, heat=1):
        self.heat = heat

    def play(self, card):
        card.player.get_enemy().mech.heat += self.heat

    def cost(self):
        return self.heat

class HurtSelf(Step):
    def __init__(self, damedge):
        self.damedge = damedge

    def play(self, card):
        card.player.mech.hp -= self.damedge

    def cost(self):
        return -self.damedge // 2

"""
Below, all card types are defined:
"""
class StandardMove(Card):
    heat = 1
    steps = [Rotate(), MoveForward(0, 6)]

class StandingSwivel(Card):
    heat = 1
    steps = [Rotate(0, 180)]

class StepUp(Card):
    heat = 2
    steps = [Rotate(0, 90), MoveForward(0, 6, ignore_terrrain=True)]

class CombatWit(Card):
    heat = 1
    steps = [Draw()]

class StepBack(Card):
    heat = -2
    steps = [MoveAway(2, 6)]

class CoolOff(Card):
    heat = -4
    steps = [EndTurn()]

class CookCabin(Card):
    heat = 3
    steps = [Attack(5, 6), EnemyDiscard(1)]

class MeltSensors(Card):
    heat = 3
    steps = [EnemyDiscard(2)]

class TorchEm(Card):
    heat = 3
    steps = [Attack(2, 12), HeatEnemy(2)]

class LooseMissile(Card):
    heat = 1
    steps = [Attack(2, 12)]

class MissileHail(Card):
    heat = 3
    steps = [Attack(4, 18), Retire()]

class ShakeItOff(Card):
    heat = -1
    steps = [Rotate(90, 180)]

class JumpPack(Card):
    heat = 3
    steps = [Rotate(0, 90), MoveForward(6, 12, ignore_terrrain=True)]

class SlowItDown(Card):
    heat = -2
    steps = [Draw(), EndTurn()]

class PushOff(Card):
    heat = 1
    steps = [Attack(6, 2), MoveAway(6, 12)]

class LaserSnapfire(Card):
    heat = 2
    steps = [Attack(3, 12), MoveForward(0, 2)]

class BlindingBurst(Card):
    heat = 3
    steps = [Attack(5, 6), ForceRotate(90)]

class TrackingShot(Card):
    heat = 2
    steps = [Rotate(0, 90), Attack(2, 12), Rotate(0, 90)]

class StaggerForward(Card):
    heat = 1
    steps = [Rotate(), MoveForward(2, 6)]

class OverdriveServos(Card):
    heat = 1
    steps = [Rotate(0, 180), MoveForward(0, 12), Retire()]

class DriveBy(Card):
    heat = 3
    steps = [
        MoveForward(2, 6), Rotate(0, 180), Attack(4, 12), MoveForward(2, 6),
        Retire()
    ]

class MechanicalFuse(Card):
    heat = -3
    steps = [HurtSelf(2)]

class RememberTraining(Card):
    heat = 0
    steps = [Unretire(), EndTurn()]

class DoItRight(Card):
    heat = 0
    steps = [Unretire(), Retire()]

class HeavyLead(Card):
    heat = 2
    steps = [Attack(6, 12, 6)]

class SupressingFire(Card):
    heat = 4
    steps = [Attack(4, 12), MoveAway(2, 6), Rotate(0, 90)]

class SweepingBarrage(Card):
    heat = 4
    steps = [Rotate(0, 180), Attack(8, 18, 6), Retire(), EndTurn()]
