from src.utils import NamedClass, get_range

import logging
logger = logging.getLogger("HotMech")

class Step(NamedClass):
    """
    Abstract class, that each specific type of step will sub-class.
    Then each instance of a subclass is a step on a card,
    with the parameters it uses (e.g. 'Move' with '0-6"')
    """

    # is this step's 'can' required to play the card?
    mandatory = False

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

    def x_cards_str(self):
        """
        Just a helpful plurilization shorthand for explainer
        """
        return (
            "a card" if self.number_of_cards < 2
            else f"{self.number_of_cards} cards"
        )

    def range_str(self, unit='"'):
        """
        Just a helpful x-x" for explainer
        """
        return (
            f"{self.min}-{self.max}{unit}" if self.max != self.min
            else f" ~{self.max}{unit}"
        )

    # A dict that holds all defined cards by:
    # string of class name -> type
    all_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_types[cls.__name__] = cls

"""
Below, all step types are defined:
"""
class MoveForward(Step):
    def __init__(self, max_move=6, min_move=0, flying=False):
        self.min, self.max = get_range(min_move, max_move)
        self.flying = flying

    def play(self, card):
        card.player.move_toward(self.max, self.min, self.flying)
        # logger.info(f"Moved {card.player} to {card.player.location}")

    def explainer(self):
        return (
            ("Fly" if self.flying else "Move")
            + f" forward {self.range_str()}"
        )

    def cost(self):
        c = (self.max - self.min) / 6
        if self.flying:
            c += 1
        return max(int(c), 1)

class MoveAway(Step):
    def __init__(self, max_move=6, min_move=0):
        self.min, self.max = get_range(min_move, max_move)

    def play(self, card):
        card.player.move_away(self.max, self.min)
        # logger.info(f"Moved away {card.player} to {card.player.location}")

    def explainer(self):
        return (
            f"Move away {self.range_str()}"
        )

    def cost(self):
        return (self.max - self.min) // 3

class Rotate(Step):
    def __init__(self, max_rot=90, min_rot=0):
        self.min, self.max = get_range(min_rot, max_rot)
        if self.max > 180:
            self.max = 180

    def play(self, card):
        card.player.rotate_towards(self.max, self.min)
        # logger.info(f"Rotated {card.player} to {card.player.rotation}")

    def explainer(self):
        return (
            f"Rotate +/- {self.range_str('°')}"
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
            f"Rotate the enemy +/- ~{self.rotation}°"
        )

    def cost(self):
        return self.rotation // 90

class Attack(Step):
    def __init__(self, damage=4, max_range=6, min_range=0):
        self.min, self.max = get_range(min_range, max_range)
        self.damage = damage

    def play(self, card):
        if self.can(card):
            card.game_state.damage_enemy(card.player, self.damage)
            logger.info(f"Attacked for {self.damage}")

    def can(self, card):
        """
        Is enemy in range
        """
        return (
            card.player.facing_toward_enemy()
            and card.player.in_range(self.min, self.max)
        )

    def explainer(self):
        return (
            f"{self.range_str()} range, deal {self.damage} damage"
        )

    def cost(self):
        usable_range = self.max / 4 - self.min / 4
        usable_range = max(usable_range, 1)
        dmg_mult = self.damage / 2
        dmg_mult = max(dmg_mult, 1)
        return int(usable_range * dmg_mult)

class Retire(Step):
    def play(self, card):
        card.player.retire(card)

    def explainer(self):
        return (
            f"Retire this card"
        )

    def cost(self):
        return -2

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
        # Can't unretire same card
        return len([c for c in card.player.retired if c.name != card.name]) > 0

    def cost(self):
        return 4 * self.number_of_cards

class Draw(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            card.player.draw_card()

    def explainer(self):
        return f"Draw {self.x_cards_str()}"

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

class Discard(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        card.player.discard(self.number_of_cards)

    def explainer(self):
        return (
            f"Discard {self.x_cards_str()}"
        )

    def cost(self):
        return -1 * self.number_of_cards

class EnemyDiscard(Step):
    def __init__(self, number_of_cards=1):
        self.number_of_cards = number_of_cards

    def play(self, card):
        for i in range(self.number_of_cards):
            card.player.get_enemy().discard()

    def can(self, card):
        return len(card.player.get_enemy().hand) > 0

    def explainer(self):
        return (
            f"Enemy must discard {self.x_cards_str()}"
        )

    def cost(self):
        return 3 * self.number_of_cards

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

    def can(self, card):
        return card.player.mech.hp > self.damage

    def explainer(self):
        return (
            f"Deal {self.damage} damage to yourself"
        )

    def cost(self):
        return -self.damage

class RangeCheck(Step):
    """
    Add a conditional check to see if we can play the next step
    """
    # TODO could add a more abstract 'ConditionalStep'
    # and maybe even use a predicate or something

    def __init__(self, max_range=6, min_range=0, step=None):
        if step is None:
            raise ValueError("None passed for step")
        self.min, self.max = get_range(min_range, max_range)
        self.step = step

    def play(self, card):
        if not self.can(card):
            return
        self.step.play(card)

    def explainer(self):
        return (
            f"If within {self.range_str()}, "
            + self.step.explainer()
        )

    def can(self, card):
        return (
            card.player.in_range(self.min, self.max)
            and self.step.can(card)
        )

    def cost(self):
        """
        Subtract some cost from the step:
        If the range is very usable, then don't subtract much
        """
        usable_range = self.max / 3 - self.min / 3
        usable_range = max(usable_range, 1)
        best_case = -5
        cost_decrease = min(best_case + usable_range, 0)
        return cost_decrease + self.step.cost()

class MandatoryRange(Step):
    """
    Card can only be played if within X
    """
    mandatory = True

    def __init__(self, max_range=6, min_range=0):
        self.min, self.max = get_range(min_range, max_range)

    def play(self, card):
        pass

    def explainer(self):
        return (
            f"Must be within {self.range_str()} to play this"
        )

    def can(self, card):
        return card.player.in_range(self.min, self.max)

    def cost(self):
        """
        Subtract some cost from the step:
        If the range is very usable, then don't subtract much
        """
        usable_range = self.max / 3 - self.min / 3
        usable_range = max(usable_range, 1)
        best_case = -5
        cost_decrease = min(best_case + usable_range, 0)
        return cost_decrease


class RotateAway(Step):
    """
    Rotate myself so I face away from the enemy
    """

    def play(self, card):
        card.player.rotation = (card.player.angle_to_enemy() + 180) % 360

    def explainer(self):
        return (
            f"Rotate to face away from the enemy"
        )

    def cost(self):
        return -2

class IncreaseRange(Step):
    """
    Increase next card's max range
    """

    def __init__(self, add=6):
        self.add = add

    def play(self, card):
        if not self.can(card):
            return
        # TODO technically this isn't the 'next card'
        # - but close enough
        # TODO this should be temporary...
        self.boostable_cards(card)[0].max += self.add

    def boostable_cards(self, card):
        hand = card.player.hand
        return [c for c in hand if hasattr(c, "max")]

    def can(self, card):
        return self.boostable_cards(card) != []

    def explainer(self):
        return (
            f"Increase next card's max by {self.add}\""
        )

    def cost(self):
        return 1 + self.add / 3
