from src.game_state import GameState
from src.player import Choices
from src.mech import Skeleton
from src.character import NamelessDegenerate
import src.card as cards


def assert_player(player, health=10, location=(0, 0)):
    loc = tuple(map(lambda x: round(x), player.location))
    assert player.mech.hp == health
    assert loc == location

def play_card(player, card_type, card_limit=None):
    player.hand = []
    player.discard = []
    player.deck = [card_type(GameState.get_last(), player)]
    player.take_turn(card_limit)

def get_players():
    # Create two blank mechs
    gs = GameState(
        Choices(NamelessDegenerate, Skeleton),
        Choices(NamelessDegenerate, Skeleton),
    )
    # shorthand
    w = gs.white
    b = gs.black
    w.character.name = "white"
    b.character.name = "black"

    # Let's move to be in more predictable locations
    b.location = (10, 0)

    # Start with no cards, full hp, etc
    assert w.deck == []
    assert b.deck == []
    assert_player(w)
    assert_player(b, 10, (10, 0))

    return w, b

def test_movement():
    w, b = get_players()
    assert_player(w, 10, (0, 0))
    assert_player(b, 10, (10, 0))

    # White moves forward 6in
    play_card(w, cards.StandardMove)
    assert_player(w, 10, (6, 0))
    assert_player(b, 10, (10, 0))

    # Same card for black, but they can only
    # get so close
    assert b.mech.heat == 1
    play_card(b, cards.StandardMove)
    assert_player(w, 10, (6, 0))
    assert_player(b, 10, (7, 0))
    assert b.mech.heat == 2

    # White is looking 'east'
    assert w.rotation == 0
    assert w.facing_toward_enemy()
    # If we move black to be to the 'north'
    b.location = (6, 10)
    assert not w.facing_toward_enemy()
    # Then it will look towards them
    play_card(w, cards.StandingSwivel)
    assert w.rotation == 90
    assert w.facing_toward_enemy()

    # TODO less-than-max rotation
    # TODO if pointing away, will do 0 if it can,
    # or min if it must
    # TODO
    """
    StepUp
    StepBack
    StaggerForward
    JumpPack
    """

def test_utility():
    w, b = get_players()
    # Drawing card, taking more heat
    assert b.hand == []
    assert b.mech.heat == 1
    play_card(b, cards.CombatWit, 1)
    assert len(b.hand) == 1
    assert b.mech.heat == 3

    # Here black plays another card, lowering heat
    play_card(b, cards.CoolOff)
    # Down to 0, but min is 1
    assert b.mech.heat == 1

    # TODO
    """
    ShakeItOff
    SlowItDown
    """

def test_combat():
    w, b = get_players()
    # TODO
    """
    CookCabin
    MeltSensors
    TorchEm
    LooseMissile
    MissileHail
    PushOff
    LaserSnapfire
    BlindingBurst
    TrackingShot
    """
