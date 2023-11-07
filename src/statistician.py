import logging
from statistics import median

from src.game_state import GameState
from src.player import Choices
import src.mech as mechs

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("HotMech")

# Run using:
# seba
# python -m src.statistician

class Statistician:
    """
    Collect statistics for showing at the end of the game
    """

    # Every game state played
    games = []

    # Dict of the interesting staticstics
    stats = {}

    def run_simulations(self, number=10000, w_mech=None, b_mech=None):
        print("Running simulations.")

        for i in range(number):
            # For now, let's randomly select entities for simulation
            # TODO upgrades
            # TODO every permutation
            # TODO randomized mechs
            white_choices = Choices(None, w_mech)
            black_choices = Choices(None, b_mech)
            game_state = GameState(white_choices, black_choices)
            logger.info(f"Starting {game_state}")
            game_state.play()
            logger.info(
                f"{game_state.winner} win: "
                f"{game_state.white} {game_state.black}"
            )
            self.games.append(game_state)

        self.calc_stats()

    def calc_stats(self):
        """
        Calculate the things we actually care about
        """

        # TODO we are going to need to keep track of each turn,
        # and use that for stats

        # TOOD stats we want:
        """
        * How long did each game take?
        * How close was it? (winner hp)
        * How often was someone unable to draw cards?
        * How long did it take to initiate combat?
        * How often did each mech win?
        * How often did each pilot win?
        * How often did each upgrade win?
        * What & of damage was overheating?
        """

        def get_rate(number_of_games):
            # If something happens x number of games, what percent of
            # games was that?
            percent = (number_of_games / len(self.games)) * 100
            percent = round(percent)
            return f"{percent}% ({number_of_games}/{len(self.games)})"

        # Who won?
        mech_names = [m.__name__ for m in mechs.Mech.all_types.values()]
        for mech_name in mech_names + ["Tie", "None"]:
            wins = len([
                g for g in self.games
                if mech_name in str(g.winner)
            ])
            self.stats[f"{mech_name} Wins"] = get_rate(wins)

        # How long did games take?
        self.stats["Median Game Length"] = (
            f"{median(g.turns for g in self.games)} turns"
        )
        self.stats["Max Game Length"] = (
            f"{max(g.turns for g in self.games)} turns"
        )

        turn_counts = [
            turn_count
            for g in self.games
            for turn_count in g.turn_lengths
        ]
        self.stats["Median Turn Length"] = (
            f"{median(turn_counts)} cards per turn"
        )
        self.stats["Max Turn Length"] = (
            f"{max(turn_counts)} cards per turn"
        )

    def print_statistics(self):
        print(f"Played {len(self.games)} games:")
        for game in self.games:
            msg = (
                f"{game.winner} win, {game.turns} turns, "
                f"{game.first_blood_turn} fb\n"
                f"{game.white.mech.hp} white hp, {game.black.mech.hp} black hp"
                f"\n"
            )
            logger.info(msg)

        for key, value in self.stats.items():
            print(f"{key}: {value}")

# Start the simulations
if __name__ == "__main__":
    s = Statistician()

    print("Example game:")
    logger.setLevel(logging.DEBUG)
    s.run_simulations(1, mechs.Sandpiper, mechs.Thermo)

    # print("Example game vs skeleton:")
    # logger.setLevel(logging.DEBUG)
    # s.run_simulations(1, mechs.Sandpiper, mechs.Skeleton)

    logger.setLevel(logging.WARNING)
    s.run_simulations()
    s.print_statistics()
