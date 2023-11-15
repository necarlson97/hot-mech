from src.game_state import GameState
from src.player import Choices
from src.mech import Skeleton
from src.pilot import NamelessDegenerate
import src.card as cards


def assert_player(player, health=10, location=(0, 0), reset=True):
    loc = tuple(map(lambda x: round(x), player.location))
    assert player.mech.hp == health
    assert loc == location
    if reset:
        player.mech.heat = 1

def play_card(player, card_type, card_limit=None):
    card = card_type(GameState.get_last(), player)
    player.hand.append(card)
    player.discard = []
    player.deck = []
    player.play_card(card)

def assert_heat(player, heat=1, reset=True):
    assert player.mech.heat == heat
    if reset:
        player.mech.heat = 1

def get_players():
    # Create two blank mechs
    gs = GameState(
        Choices(NamelessDegenerate, Skeleton),
        Choices(NamelessDegenerate, Skeleton),
    )
    # shorthand
    w = gs.white
    b = gs.black
    w.pilot.name = "white"
    b.pilot.name = "black"

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
    assert_player(b, 10, (7, 0), reset=False)
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
    assert w.rotation == w.angle_to_enemy()

    # If they can't rotate enough, they will do max:
    w.rotation = 190
    assert_player(w, 10, (6, 0))
    play_card(w, cards.StepUp)
    assert w.rotation == 100  # Wanted to get to 90
    # Would have got 6,6 if it could turn the whole way,
    # but it can't
    assert_player(w, 10, (5, 6))

    # Steps back 2" at angle
    play_card(w, cards.StepBack)
    assert_player(w, 10, (4, 4))

    # Lets try easier to read

    w.location = (0, 2)
    b.location = (0, 12)
    play_card(w, cards.StepBack)
    assert_player(w, 10, (0, 0))

    # Even though white is facing away, it has to move
    w.rotation = -90
    play_card(w, cards.StaggerForward)
    assert_player(w, 10, (2, 0))
    assert w.rotation == 0

    # Now it can turn all the way
    play_card(w, cards.JumpPack)
    assert_player(w, 10, (2, 11))
    assert w.rotation == 90


    # TODO less-than-max rotation
    # TODO if pointing away, will do 0 if it can,
    # or min if it must
    # TODO
    """
    Push Forward
    Rushing Wind
    Survey Landscape

    Giddy Retreat
    Drive Harder
    Lightning Inspiration

    Jolt Forward
    Blast Off
    """

def test_utility():
    w, b = get_players()
    # Drawing card, taking more heat
    assert b.hand == []
    assert b.mech.heat == 1
    play_card(b, cards.CombatWit, 1)
    assert len(b.hand) == 1
    assert b.mech.heat == 2

    # Here black plays another card, lowering heat
    play_card(b, cards.CoolOff)
    # Down to 0, but min is 1
    assert b.mech.heat == 1

    # TODO
    """
    ShakeItOff
    SlowItDown

    Chart Study
    Recall Wisdom
    Hateful Glare
    Boast Challenge
    Cover Eyes
    Blissful Ignorance

    Slow Sizzle
    Jettison Heatsinks
    Steam Blowoff
    Take Reading
    Lock On
    """

def test_combat():
    w, b = get_players()

    # Start at 10
    assert w.mech.hp == 10
    assert b.mech.hp == 10

    # And out of range
    b.location = (13, 0)
    play_card(w, cards.LooseMissile)
    assert w.mech.hp == 10
    assert b.mech.hp == 10
    assert_heat(w, 2)

    # But once we move in range, we can attack
    b.location = (10, 0)
    play_card(w, cards.LooseMissile)
    assert w.mech.hp == 10
    assert b.mech.hp == 8
    assert_heat(w, 2)

    # Attack also discards
    c1 = cards.StandardMove(GameState.get_last(), b)
    c2 = cards.StandardMove(GameState.get_last(), b)
    c3 = cards.StandardMove(GameState.get_last(), b)
    b.hand = [c1, c2, c3]
    assert len(b.hand) == 3
    play_card(w, cards.MeltSensors)
    assert w.mech.hp == 10
    assert b.mech.hp == 8
    assert len(b.hand) == 1
    assert_heat(w, 4)

    b.hand = [c1, c2, c3]
    b.location = (6, 0)
    play_card(w, cards.CookCabin)
    assert w.mech.hp == 10
    assert b.mech.hp == 3
    assert len(b.hand) == 2
    assert_heat(w, 4)

    # Some cards are retired after use
    assert len(b.retired) == 0
    play_card(b, cards.MissileHail)
    assert w.mech.hp == 6
    assert b.mech.hp == 3
    assert len(b.retired) == 1
    assert_heat(b, 4)

    # Don't die yet!
    w.mech.hp = 10
    b.mech.hp = 10

    # Some attacks let you move
    assert w.location == (0, 0)
    play_card(w, cards.LaserSnapfire)
    assert w.mech.hp == 10
    assert b.mech.hp == 7
    assert w.location == (2, 0)
    assert_heat(w, 3)

    # Some force the enemy to rotate
    assert b.rotation == 180
    play_card(w, cards.BlindingBurst)
    assert w.mech.hp == 10
    assert b.mech.hp == 2
    assert b.rotation == 270
    assert_heat(w, 4)

    # can't play until we turn towards them
    play_card(b, cards.LooseMissile)
    assert w.mech.hp == 10
    assert b.mech.hp == 2
    assert_heat(b, 2)

    # This lets us turn
    assert b.rotation == 270
    play_card(b, cards.TrackingShot)
    assert b.rotation == 180
    assert w.mech.hp == 8
    assert b.mech.hp == 2
    assert_heat(b, 3)

    # Some heat them up
    play_card(b, cards.TorchEm)
    assert w.mech.hp == 6
    assert b.mech.hp == 2
    assert_heat(b, 4)
    assert_heat(w, 3)

    # Some push you back
    b.location = (4, 0)
    assert w.location == (2, 0)
    play_card(b, cards.PushOff)
    assert w.mech.hp == 0
    assert b.mech.hp == 2
    assert b.location == (10, 0)
    assert_heat(b, 2)

    # TODO
    """
    Rip Vitals
    Targeted Strike
    """

def test_cost():
    # Check to see that all cards are balanced, according to
    # how powerful their steps are
    w, b = get_players()
    gs = GameState.get_last()

    for card_type in cards.Card.all_types.values():
        card = card_type(gs, w)
        # TODO can be a bit off
        step_costs = ', '.join(f'{s} {s.cost()}c' for s in card.steps)
        msg = (
            f"{card.name} {card.cost()}c != {card.heat}h"
            f" (-1 for card, {step_costs})"
        )
        allowed_heat = range(card.heat-1, card.heat + 2)
        assert card.cost() in allowed_heat, msg
        if card.cost() != card.heat:
            print(msg + " but within +/-1")
