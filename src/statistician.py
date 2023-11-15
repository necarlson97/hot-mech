import logging
from statistics import median

from src.game_state import GameState
from src.player import Player, Choices
from src.mech import Mech
from src.pilot import Pilot
from src.upgrade import Upgrade
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

        def get_rate(games):
            # If something happens x number of games, what percent of
            # games was that?
            number_of_games = len(list(games))
            percent = (number_of_games / len(self.games)) * 100
            percent = round(percent)
            return f"{percent}%"  # ({number_of_games}/{len(self.games)})"

        # Who won?
        mech_names = [m.name for m in Mech.all_types.values()]
        for name in mech_names + ["Tie", "None"]:
            self.stats[f"{name} Wins"] = get_rate(
                g for g in self.games
                if name in str(g.winner)
            )

        pilot_names = [p.name for p in Pilot.all_types.values()]
        for name in pilot_names:
            self.stats[f"{name} Wins"] = get_rate(
                g for g in self.games
                if name in str(g.winner)
            )

        for upgrade in Upgrade.all_types.values():
            self.stats[f"{upgrade.name} Wins"] = get_rate(
                g for g in self.games
                if isinstance(g.winner, Player)
                and upgrade in g.winner.upgrades
            )

        # How long did games take?
        def turn_info(t_list):
            # Helper str for median/min/max # of turns
            t_list = list(t_list)
            return (
                f"Median: {median(t_list)}t ({median(t_list) // 2})r"
                + f" [{min(t_list)}-{max(t_list)}]"
            )

        self.stats["Game Length"] = turn_info(
            g.turns for g in self.games)
        self.stats["1st blood"] = turn_info(
            g.first_blood_turn for g in self.games
            if g.first_blood_turn
        )
        self.stats[f"No weapons"] = get_rate(
            g for g in self.games if g.first_blood_turn is None)

        self.stats["Combat Length"] = turn_info(
            (g.turns - g.first_blood_turn)
            if g.first_blood_turn else 0
            for g in self.games)

        self.stats["Cards per turn"] = turn_info(
            turn_count
            for g in self.games
            for turn_count in g.turn_lengths
        )

        self.stats["Median Melt Damage"] = (
            f"{median(g.total_melt_dmg for g in self.games)}"
        )
        self.stats["Median Weapon Damage"] = (
            f"{median(g.total_weapon_dmg for g in self.games)}"
        )

    def print_statistics(self):
        print(f"\n\n")
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
    s.run_simulations(1)

    # print("Example game vs skeleton:")
    # logger.setLevel(logging.DEBUG)
    # s.run_simulations(1, mechs.Sandpiper, mechs.Skeleton)

    logger.setLevel(logging.WARNING)
    for i in range(10):
        s.run_simulations(1000)
        s.print_statistics()
