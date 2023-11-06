import math
import random
import logging
logger = logging.getLogger("HotMech")

from src.mech import Mech
from src.character import Character

class Player:
    """
    Represents the individual human player for each game,
    that has chosen a character, mech, etc
    """

    starting_hand = 5

    def __init__(self, game_state,
                 character_type, mech_type, upgrade_types=[]):
        self.game_state = game_state
        self.character = character_type(game_state, self)
        self.mech = mech_type(game_state, self)
        self.upgrades = [u(game_state, self) for u in upgrade_types]
        self.deck = (
            self.character.cards + self.mech.cards
            + [u.cards for u in self.upgrades]
        )

        self.discard = []
        self.hand = []
        self.retired = []

        self.rotation = 0
        self.location = (0, 0)

        # Statistics
        self.largest_hand = 0
        self.played_cards = 0
        self.empty_hands = 0

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
        for i in range(self.starting_hand - len(self.hand)):
            self.draw_card()

        self.my_turn = True

        self.turn_cards = 0
        while self.my_turn and self.turn_cards < 100:
            card = self.choose_card()
            if card is None:
                self.empty_hands += 1
                break

            logger.info(f"{self} playing {card.name}")
            card.play()
            logger.info(f"hand {self.hand}")

            self.get_enemy().mech.check_heat()
            self.mech.check_heat()

            self.turn_cards += 1
            self.played_cards += 1

            # Mostly for testing
            if card_limit and self.turn_cards >= card_limit:
                logger.info(f"{self} reached card limit of {card_limit}")
                break

        if self.turn_cards >= 100:
            logger.warning(f"Long turn: {self.turn_cards}")
            quit()

    def end_turn(self):
        self.my_turn = False

    def choose_card(self):
        if (len(self.hand) < 1):
            return None
        card = random.choice(self.hand)
        self.hand.remove(card)
        self.discard.append(card)
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

    def in_range(self, max_range=6, min_range=0):
        """
        Return true if our location is within a specified range of the enemy
        """
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
        angle = angle or self.rotation
        angle_radians = math.radians(angle)
        new_x = self.location[0] + move_distance * math.cos(angle_radians)
        new_y = self.location[1] + move_distance * math.sin(angle_radians)
        self.location = (new_x, new_y)

    def difficult_terrain(self):
        # For now, to handle crashing into terrain,
        # just make it an occasional random thing
        if random.randint(0, 10) == 0:
            self.mech.hp -= random.randint(0, 6)

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
        print(f"{self} starting rot: {self.rotation}")
        print(f"angle to: {self.angle_to_enemy()} = {angle_difference}")
        print(f"rotation amount: {angle_difference} = {rotation_amount}")
        self.rotate(rotation_amount)

    def rotate(self, rot):
        self.rotation = (self.rotation + rot) % 360

    def get_enemy(self):
        return self.game_state.enemy_of(self)

    def throw_away(self):
        """
        Discard a card
        """
        # TODO naming is a little strange
        self.choose_card()

    def __str__(self):
        return (
            f"({self.character.name}, {self.mech.name} "
            f"{self.mech.heat}h {self.mech.hp}hp)"
        )
    def __repr__(self):
        return self.__str__()

class Choices:
    """
    Simple dataclass to keep track of a player's choices:
    their character type, mech type, etc
    """

    def __init__(self, ct=None, mt=None):
        all_characters = list(Character.all_types.values())
        self.character_type = ct or random.choice(all_characters)
        all_mechs = list(Mech.all_types.values())
        self.mech_type = mt or random.choice(all_mechs)
        # TODO upgrades

    def create_player(self, game_state):
        return Player(game_state, self.character_type, self.mech_type)
