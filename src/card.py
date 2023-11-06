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

class MoveAway(Step):
    def __init__(self, min_move=0, max_move=6):
        self.min = min_move
        self.max = max_move

    def play(self, card):
        card.player.move_away(self.max, self.min)

class Rotate(Step):
    def __init__(self, min_rot=0, max_rot=90):
        self.min = min_rot
        self.max = max_rot

    def play(self, card):
        card.player.rotate_towards(self.max, self.min)
        logger.info(f"Rotated {card.player} to {card.player.rotation}")

class ForceRotate(Step):
    def __init__(self, rotation=90):
        self.rotation = rotation

    def play(self, card):
        card.player.get_enemy().rotate(90)

class Attack(Step):
    def __init__(self, damedge=4, max_range=6, min_range=0):
        self.max_range = max_range
        self.min_range = max_range
        self.damedge = damedge

    def play(self, card):
        in_range = card.player.in_range(self.min_range, self.max_range)
        if card.player.facing_toward_enemy() and in_range:
            card.game_state.damage_enemy(card.player, self.damedge)

class Retire(Step):
    def play(self, card):
        card.player.discard.remove(card)
        card.player.retired.append(card)

class Draw(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            card.player.draw_card()

class EndTurn(Step):
    def play(self, card):
        card.player.end_turn()

class EnemyDiscard(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            card.player.get_enemy().throw_away()

class HeatEnemy(Step):
    def __init__(self, heat=1):
        self.heat = heat

    def play(self, card):
        card.player.get_enemy().mech.heat += self.heat


"""
Below, all card types are defined:
"""
class StandardMove(Card):
    heat = 1
    steps = [Rotate(), MoveForward(0, 6)]

class StandingSwivel(Card):
    heat = 1
    steps = [Rotate(0, 360)]

class StepUp(Card):
    heat = 2
    steps = [Rotate(0, 90), MoveForward(0, 6, ignore_terrrain=True)]

class CombatWit(Card):
    heat = 2
    steps = [Draw()]

class StepBack(Card):
    heat = -2
    steps = [MoveAway(2, 6)]

class CoolOff(Card):
    heat = -3
    steps = [EndTurn()]

class CookCabin(Card):
    heat = 3
    steps = [Attack(5, 6), EnemyDiscard(1)]

class MeltSensors(Card):
    heat = 4
    steps = [EnemyDiscard(2)]

class TorchEm(Card):
    heat = 4
    steps = [Attack(4, 12), HeatEnemy(2)]

class StaggerForward(Card):
    heat = 1
    steps = [Rotate(), MoveForward(2, 6)]

class LooseMissile(Card):
    heat = 1
    steps = [Attack(2, 12)]

class MissileHail(Card):
    heat = 3
    steps = [Attack(5, 24), Retire()]

class ShakeItOff(Card):
    heat = -1
    steps = [Rotate(90, 180)]

class JumpPack(Card):
    heat = 3
    steps = [Rotate(0, 90), MoveForward(6, 12, ignore_terrrain=True)]

class SlowItDown(Card):
    heat = -1
    steps = [Draw(), EndTurn()]

class PushOff(Card):
    heat = 2
    steps = [Attack(2, 2), MoveAway(6, 12)]

class LaserSnapfire(Card):
    heat = 2
    steps = [Attack(3, 12), MoveForward(0, 2)]

class BlindingBurst(Card):
    heat = 3
    steps = [Attack(5, 12), ForceRotate(90)]

class TrackingShot(Card):
    heat = 2
    steps = [Rotate(0, 90), Attack(3, 12), Rotate(0, 90)]

class TODO(Card):
    heat = -1
    steps = [Rotate(90, 180)]
