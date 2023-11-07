import logging
logger = logging.getLogger("HotMech")

class GameState:
    """
    Keeps track of the state of a game, and goes into the record
    for the 'Statistics' class to draw conclusions from
    """

    def __init__(self, white_choices, black_choices):
        self.white = white_choices.create_player(self)
        self.black = black_choices.create_player(self)

        # Start one player 'on other side of board'
        self.black.location = (30, 10)
        self.black.rotation = 180

        self.turns = 0
        self.turn_lengths = []
        self.first_blood_turn = None
        self.winner = None

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
                self.winner = "Tie"
                return
            elif white_dead:
                self.winner = self.black
                return
            elif black_dead:
                self.winner = self.white
                return

        if self.turns >= 100:
            logging.warning(f"Long game: {self}")

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
