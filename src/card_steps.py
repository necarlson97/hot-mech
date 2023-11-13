class Step(NamedClass):
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
