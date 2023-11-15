import math
import random
import itertools

from src.mech import Mech, Skeleton
from src.pilot import Pilot
from src.upgrade import Upgrade, Tassles
from src.utils import get_range
from src.card_steps import Attack

import logging
logger = logging.getLogger("HotMech")

class Player:
    """
    Represents the individual human player for each game,
    that has chosen a pilot, mech, etc
    """

    starting_hand = 5

    def __init__(self, game_state,
                 pilot_type, mech_type, upgrade_types=[]):
        self.game_state = game_state
        self.pilot = pilot_type(game_state, self)
        self.mech = mech_type(game_state, self)
        self.upgrades = [u(game_state, self) for u in upgrade_types]
        # Remove any that is more than hardpoints
        if len(self.upgrades) > self.mech.hard_points:
            logger.warning(
                f"More upgrades than hardpoints:"
                f"{self.upgrades} {self.mech} {self.mech.hard_points}"
            )
            self.upgrades = self.upgrades[0:self.mech.hard_points]
        self.deck = list(itertools.chain(
            self.pilot.cards, self.mech.cards,
            *[u.cards for u in self.upgrades]
        ))

        self.discard = []
        self.hand = []
        self.retired = []

        self.rotation = 0
        self.location = (0, 0)

        # Statistics
        self.largest_hand = 0
        self.played_cards = 0
        self.empty_hands = 0
        self.turn_cards = 0

    def draw_card(self):
        # If we are out of cards, shuffle back in discard
        if (self.deck == []):

            # If discard is empty, all cards are retired / in hand?
            if (self.discard == []):
                # logger.warning(
                #     f"{self} draw and discard empty. "
                #     f"Hand: {[c.name for c in self.hand]}. "
                #     f"Retired: {[c.name for c in self.retired]}"
                # )
                return

            self.deck = random.sample(self.discard, len(self.discard))
            self.discard = []

        new_card = self.deck.pop()
        self.hand.append(new_card)

        if len(self.hand) > self.largest_hand:
            self.largest_hand = len(self.hand)

    def take_turn(self, card_limit=None):
        # If our hand is still full from last turn,
        # discard some cards
        # TODO are we allowed? Or are we forced to play,
        # and take heat?
        if (len(self.hand) > 4):
            self.throw_away(5 - len(self.hand))

        for i in range(self.starting_hand - len(self.hand)):
            self.draw_card()

        # TODO is heat subtracted, reset, or untouched at the start of a turn?
        self.mech.heat -= 1
        # self.mech.heat = 1

        self.my_turn = True

        self.turn_cards = 0
        while self.my_turn and self.turn_cards < 100:
            card = self.choose_card()

            # If we can't play anything
            if card is None:
                logger.info(f"{self} can't choose card {self.hand}")
                break

            self.play_card(card)

            # Mostly for testing
            if card_limit and self.turn_cards >= card_limit:
                logger.info(f"{self} reached card limit of {card_limit}")
                break

        if self.turn_cards >= 100:
            logger.warning(f"Long turn: {self.turn_cards}")
            quit()

    def play_card(self, card):
        logger.info(
            f"{self} playing {card.name} ({card.should()}/{card.can()})")

        self.hand.remove(card)
        self.discard.append(card)
        card.play()

        self.get_enemy().mech.check_heat()
        self.mech.check_heat()

        self.turn_cards += 1
        self.played_cards += 1

    def end_turn(self):
        self.my_turn = False

    def sorted_hand(self, reverse=False):
        return self.sorted_cards(self.hand, reverse)

    def sorted_cards(self, cards, reverse=False):
        """
        Sort the cards by:
        1. Can we play the card without overheating? a.k.a card.should()
        2. Will the card have any effect? a.k.a card.can
        3. As a tiebreaker, which card has the lower 'card.heat' cost
        """

        def dmg(card):
            # Prioritize cards that deal damage
            # (negative = sorted earlier = better)
            for s in card.steps:
                if isinstance(s, Attack):
                    return -s.damage
            return 0

        s_hand = sorted(
            cards,
            key=lambda card: (
                not card.should(), -card.how_many_can(), dmg(card), card.heat
            )
        )
        if reverse:
            s_hand.reverse()
        return s_hand

    def choose_card(self):
        """
        Choose a random card to play, but ideally:
        1. A card we can play without overheating
        2. A card we can play, but will overheat
        3. A card we can somewhat play (some but not all steps will activate)
        4. A card no steps will activate on
        """
        if len(self.hand) < 1:
            self.empty_hands += 1
            return None

        card = self.sorted_hand()[0]

        # If we are going to overheat, make it a 50/50
        # TOOD could see if it was a 'worthwhile' card by some metric...
        # (one in 'x' chance to play overheating card)
        one_in = 5
        if not card.should() and random.randint(0, one_in) < one_in:
            return None

        # Don't overheat if it might kill you
        if not card.should() and self.mech.hp <= 5:
            return None

        return card

    def angle_to_enemy(self):
        """
        Calculate the direction of the enemy relative to the player's location
        """
        enemy = self.get_enemy()
        dx = enemy.location[0] - self.location[0]
        dy = enemy.location[1] - self.location[1]
        return math.degrees(math.atan2(dy, dx)) % 360

    def facing_toward_enemy(self):
        """
        Return true if our location/rotation is pointing toward
        the enemy location
        """

        # Normalize angles to 0-360
        self.rotation = self.rotation % 360
        angle_to_enemy = self.angle_to_enemy()

        # Determine if the player is facing the enemy,
        # considering a margin for 'facing towards'
        facing_margin = 45  # +/- degrees considered as facing toward the enemy
        lower_bound = (self.rotation - facing_margin) % 360
        upper_bound = (self.rotation + facing_margin) % 360

        # Check if the enemy is within the 'facing towards' margin
        if lower_bound < upper_bound:
            return lower_bound <= angle_to_enemy <= upper_bound
        else:  # The margin crosses the 0 degree line
            return (
                angle_to_enemy >= lower_bound or angle_to_enemy <= upper_bound
            )

    def distance_to_enemy(self):
        enemy = self.get_enemy()
        dx = enemy.location[0] - self.location[0]
        dy = enemy.location[1] - self.location[1]
        return math.sqrt(dx**2 + dy**2)

    def in_range(self, range_a=6, range_b=0):
        """
        Return true if our location is within a specified range of the enemy
        """
        min_range, max_range = get_range(range_a, range_b)
        return min_range <= self.distance_to_enemy() <= max_range

    def move_toward(self, range_max=6, range_min=0, ignore_terrrain=False):
        """
        If we are facing toward the enemy, move towards them the max
        (or 1 in front of them, if we are able)
        If we are facing away from the enemy, move the minimum
        """
        if self.facing_toward_enemy():
            distance_to_enemy = self.distance_to_enemy()

            # Move up to range_max but not closer than 1 unit from the enemy
            move_distance = min(
                range_max, max(distance_to_enemy - 1, range_min)
            )
        else:
            # Move the minimum distance if not facing the enemy
            move_distance = range_min

        self.move(move_distance)

        forced_move = move_distance == range_min and range_min > 0
        if not ignore_terrrain and forced_move:
            self.difficult_terrain()

    def move_away(self, range_max=6, range_min=0):
        """
        If we are facing toward the enemy, move towards them the max
        (or 1 in front of them, if we are able)
        If we are facing away from the enemy, move the minimum
        """
        away_angle = (self.angle_to_enemy() + 180) % 360
        self.move(range_min, away_angle)
        self.difficult_terrain()

    def move(self, move_distance, angle=None):
        """
        If we are facing toward the enemy, move towards them the max
        (or 1 in front of them, if we are able)
        If we are facing away from the enemy, move the minimum
        """
        # Calculate the new position using the angle and move_distance
        if angle is None:
            angle = self.rotation
        angle_radians = math.radians(angle)
        new_x = self.location[0] + move_distance * math.cos(angle_radians)
        new_y = self.location[1] + move_distance * math.sin(angle_radians)
        self.location = (new_x, new_y)

    def difficult_terrain(self):
        # For now, to handle crashing into terrain,
        # just make it an occasional random thing
        # if random.randint(0, 10) == 0:
        #     self.mech.hp -= random.randint(1, 6)
        # TODO eh, do we care?
        pass

    def rotate_towards(self, rot_max=90, rot_min=0):
        """
        Turns as much toward the enemy as we are allowed by min/max
        """
        angle_to_enemy = self.angle_to_enemy()

        # Calculate the smallest angle between self.rotation and angle_to_enemy
        angle_difference = (angle_to_enemy - self.rotation + 360) % 360
        if angle_difference > 180:
            # If the angle is more than 180,
            # it's shorter to rotate in the negative direction
            angle_difference -= 360

        # Clamp the rotation between rot_min and rot_max
        rotation_amount = max(min(rot_max, angle_difference), -rot_max)
        self.rotate(rotation_amount)

    def rotate(self, rot):
        self.rotation = (self.rotation + rot) % 360

    def get_enemy(self):
        return self.game_state.enemy_of(self)

    def throw_away(self, number_of_cards=1):
        """
        Discard a card
        """
        for i in range(number_of_cards):
            if len(self.hand) < 1:
                return
            card = self.sorted_hand(reverse=True)[0]
            self.hand.remove(card)
            self.discard.append(card)

    def __str__(self):
        return (
            f"({self.pilot.name}, {self.mech.name} "
            f"{self.mech.heat}h {self.mech.hp}hp)"
        )

    def __repr__(self):
        return self.__str__()

class Choices:
    """
    Simple dataclass to keep track of a player's choices:
    their pilot type, mech type, etc
    """

    def __init__(self, ct=None, mt=None, ut=[]):
        all_pilots = list(Pilot.all_types.values())
        self.pilot_type = ct or random.choice(all_pilots)

        # Do we simulate skeleton? So just pilot / upgrades?
        all_mechs = list(Mech.all_types.values())
        all_mechs.remove(Skeleton)

        all_upgrades = list(Upgrade.all_types.values())

        self.mech_type = mt or random.choice(all_mechs)
        self.upgrade_types = ut or [
            random.choice(all_upgrades)
            for i in range(self.mech_type.hard_points)
        ]

    def create_player(self, game_state):
        return Player(
            game_state,
            self.pilot_type, self.mech_type, self.upgrade_types
        )
