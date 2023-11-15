import logging
logger = logging.getLogger("HotMech")

from src.player import Choices

class GameState:
    """
    Keeps track of the state of a game, and goes into the record
    for the 'Statistics' class to draw conclusions from
    """

    def __init__(self, white_choices=None, black_choices=None):
        white_choices = white_choices if white_choices else Choices()
        black_choices = black_choices if black_choices else Choices()

        self.white = white_choices.create_player(self)
        self.black = black_choices.create_player(self)

        # Start one player 'on other side of board'
        self.black.location = (20, 0)
        self.black.rotation = 180

        self.turns = 0

        # For stats
        self.turn_lengths = []
        self.first_blood_turn = None
        self.winner = None
        self.total_melt_dmg = 0
        self.total_weapon_dmg = 0

        GameState._last_instance = self


    _last_instance = None
    @classmethod
    def get_last(cls):
        """
        Get the most recent instance of GameState
        - mostly for testing
        """
        return GameState._last_instance

    def play(self):
        while self.turns < 100:
            self.take_turn()
            white_dead = self.white.mech.hp <= 0
            black_dead = self.black.mech.hp <= 0

            if white_dead and black_dead:
                return self.end_game("Tie")
            elif white_dead:
                return self.end_game(self.black)
            elif black_dead:
                return self.end_game(self.white)

        if self.turns >= 100:
            logging.warning(f"Long game: {self}")

    def end_game(self, winner):
        self.winner = winner
        self.total_melt_dmg = (
            self.white.mech.total_melt_dmg
            + self.black.mech.total_melt_dmg
        )

    def take_turn(self):
        self.turns += 1
        player = self.white
        if self.turns % 2 == 0:
            player = self.black

        logger.info(f"Starting turn {self.turns} - {player}")

        player.take_turn()
        self.turn_lengths.append(player.turn_cards)

    def damage_enemy(self, attacker, ammount):
        self.enemy_of(attacker).mech.hp -= ammount
        logger.info(f"Dealt {ammount} to {self.enemy_of(attacker)}")
        self.total_weapon_dmg += ammount

        if self.first_blood_turn is None:
            self.first_blood_turn = self.turns
            logger.info(f"First blood at {self.first_blood_turn}")

    def enemy_of(self, player):
        enemy = self.white
        if player == self.white:
            enemy = self.black
        return enemy

    def __str__(self):
        return (
            f"({self.white} vs {self.black} turn {self.turns}"
        )
    def __repr__(self):
        return self.__str__()
