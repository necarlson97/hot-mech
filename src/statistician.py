import random
import logging
from statistics import median, mode

from src.game_state import GameState
from src.player import Player, Choices
from src.mech import Mech, Skeleton
from src.pilot import Pilot, NamelessDegenerate
from src.upgrade import Upgrade, Tassles
import src.mech as mechs
from src.card import Card
from src.card_steps import Step

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

    def run_simulations(self, number=1000, w_mech=None, b_mech=None):
        """
        Run randomized 'real' games, with the defined mechs, pilots, etc
        """
        for i in range(number):
            # For now, let's randomly select entities for simulation
            white_choices = Choices(None, w_mech)
            black_choices = Choices(None, b_mech)
            game_state = GameState(white_choices, black_choices)
            logger.info(f"Starting {game_state}")
            game_state.play()
            logger.info(
                f"{game_state.turns}t {game_state.winner} win: "
                f"{game_state.white} {game_state.black}"
            )
            self.games.append(game_state)

        self.calc_stats()

    def run_card_simulations(self, number=1000):
        """
        Run randomized games with randomized decks - to see which cards/steps
        are good
        """
        for i in range(number):
            # Create empty decks
            white_choices = Choices(NamelessDegenerate, Skeleton, Tassles)
            black_choices = Choices(NamelessDegenerate, Skeleton, Tassles)
            game_state = GameState(white_choices, black_choices)
            assert game_state.white.deck == []
            assert game_state.black.deck == []

            # Add 20 random cards, but ensure they have some of each type
            all_cards = Card.all_types.values()
            attacks = [ct for ct in all_cards if ct.is_attack()]
            moves = [ct for ct in all_cards if ct.is_move()]
            controls = [ct for ct in all_cards if ct.is_control()]

            def add_random_cards(player, n=21):
                # For now, adding only unique cards, no repeats,
                # to prevent infinite chains
                split = n // 3  # Apx equal from each
                deck = (
                    random.sample(attacks, split)
                    + random.sample(moves, split)
                    + random.sample(controls, split)
                )
                random.shuffle(deck)
                deck = deck[:split]
                [player.create_card(c) for c in deck]
            add_random_cards(game_state.white)
            add_random_cards(game_state.black)

            logger.info(f"Starting {game_state}")
            game_state.play()
            logger.info(
                f"{game_state.turns}t {game_state.winner} win: "
                f"\n{game_state.white} had {game_state.white.all_cards()} "
                f"\n{game_state.black} had {game_state.black.all_cards()}"
            )

            self.games.append(game_state)

        self.calc_card_stats()

    def get_rate(self, games, as_int=False):
        # If something happens x number of games, what percent of
        # games was that?
        number_of_games = len(list(games))
        percent = (number_of_games / len(self.games)) * 100
        percent = round(percent)
        if as_int:
            return percent
        return f"{percent}%"  # ({number_of_games}/{len(self.games)})"

    def breakdown_by_name(self, named_class, add=[]):
        # Who won? Mech, pilot, upgrade, etc
        names = [c.short_name() for c in named_class.all_types.values()]
        for name in names + add:
            self.stats[f"{named_class.__name__} - {name} Wins"] = self.get_rate(
                g for g in self.games
                if name in str(g.winner)
            )

    def turn_info(self, t_list):
        # Helper str for median/min/max # of turns
        t_list = list(t_list)
        return (
            f"Median: {median(t_list)}t ({median(t_list) // 2})r"
            + f" [{min(t_list)}-{max(t_list)}]"
        )

    def number_info(self, t_list):
        # Helper str for median/min/max for any numerical value
        t_list = list(t_list)
        return (
            f"Median: {median(t_list)}"
            + f" [{min(t_list)}-{max(t_list)}]"
        )

    def long_game_cards(self):
        # In how many long games was this card seen
        long_games = [g for g in self.games if g.turns > 50]
        normal_card_count = {
            card_type: 0
            for card_type in Card.all_types.values()
        }
        long_card_count = {
            card_type: 0
            for card_type in Card.all_types.values()
        }
        for ct in Card.all_types.values():
            for game in self.games:
                played_cards = set(
                    game.white.played_cards + game.black.played_cards
                )
                if ct not in played_cards:
                    continue
                normal_card_count[ct] += 1
                if game.turns > 50:
                    long_card_count[ct] += 1

        # What % of games was the card in?
        long_card_ratio = {
            k: round(v / max(len(long_games), 1), 2)
            for k, v in long_card_count.items()
        }
        normal_card_ratio = {
            k: round(v / len(self.games), 2)
            for k, v in normal_card_count.items()
        }
        # How many more long games than normal games?
        differential_ratio = {
            k: round(long_card_ratio[k] - normal_card_ratio[k], 2)
            for k in normal_card_ratio.keys()
        }
        # TODO check if there we 0 long games
        freq_cards = sorted(differential_ratio.items(), key=lambda kv: -kv[1])
        self.stats[f"Long games"] = self.get_rate(
            g for g in self.games if g.turns > 50)
        self.stats[f"Cards seen in long games"] = "\n  " + (
            "\n  ".join(f'{k.name}: {v}' for k, v in freq_cards[:10])
        )

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

        self.breakdown_by_name(Mech, ["Tie", "None"])
        self.breakdown_by_name(Pilot)
        self.breakdown_by_name(Upgrade)

        # How long did games take?
        self.stats["Game Length"] = self.turn_info(
            g.turns for g in self.games)
        self.stats["1st blood"] = self.turn_info(
            g.first_blood_turn for g in self.games
            if g.first_blood_turn
        )
        self.stats["Combat Length"] = self.turn_info(
            (g.turns - g.first_blood_turn)
            if g.first_blood_turn else 0
            for g in self.games
        )

        self.stats[f"No weapons"] = self.get_rate(
            g for g in self.games if g.first_blood_turn is None)

        cards_per_turn = [
            turn_count
            for g in self.games
            for turn_count in g.turn_lengths
        ]
        self.stats["Cards per turn"] = self.number_info(cards_per_turn)

        self.stats["Melt Damage"] = self.number_info(
            g.total_melt_dmg for g in self.games)

        self.stats["Weapon Damage"] = self.number_info(
            g.total_weapon_dmg for g in self.games)

        self.long_game_cards()

    def calc_card_stats(self):

        def card_type_in_game(game, card_type, loser=False):
            player = game.loser if loser else game.winner
            if not isinstance(player, Player):
                return False
            return card_type in set(player.played_cards)

        def step_type_in_game(game, step_type, loser=False):
            player = game.loser if loser else game.winner
            if not isinstance(player, Player):
                return False
            winner_steps = set(
                type(s)
                for card_type in player.played_cards
                for s in card_type.steps
            )
            return step_type in winner_steps

        def get_wins_vs_losses(named_type, get_win_func):
            win_dict = {}
            loss_dict = {}
            diff_dict = {}  # +/- Differential between wins/losses
            for ct in named_type.all_types.values():
                wins = (
                    g for g in self.games
                    if get_win_func(g, ct)
                )
                win_dict[ct] = self.get_rate(wins, as_int=True)
                losses = (
                    g for g in self.games
                    if get_win_func(g, ct, loser=True)
                )
                loss_dict[ct] = self.get_rate(losses, as_int=True)

                diff_dict[ct] = win_dict[ct] - loss_dict[ct]

            # Sort by what needs attention
            sorted_diff = sorted(
                diff_dict.items(),
                key=lambda kv: -abs(kv[1])
            )

            for ct, differntial in sorted_diff:
                # Did they do win, or lose more of their games?
                # Show as +x% or -x%
                win_rate = win_dict[ct]
                lose_rate = loss_dict[ct]
                is_plus = "+" if differntial > 0 else ""
                better_percent = f"{is_plus}{differntial}%"
                self.stats[f"{named_type.__name__} - {ct.name}"] = (
                    f"{better_percent} ({win_rate}w% vs {lose_rate}l%)")

        get_wins_vs_losses(Card, card_type_in_game)
        get_wins_vs_losses(Step, step_type_in_game)
        self.long_game_cards()

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

    # print("One game at a time:")
    # logger.setLevel(logging.DEBUG)
    # while input('Keep going? y/n').lower() != 'n':
    #     s.run_simulations(1)

    logger.setLevel(logging.WARNING)
    for i in range(10):
        s.run_simulations()
        s.print_statistics()

    # logger.setLevel(logging.WARNING)
    # for i in range(10):
    #     s.run_card_simulations()
    #     s.print_statistics()
