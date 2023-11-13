from jinja2 import Environment, FileSystemLoader
import os

from src.game_state import GameState
from src.mech import Mech
from src.pilot import Pilot
from src.upgrade import Upgrade
from src.card import Card

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('printout.j2')

# Render the template with your data
gs = GameState()
mechs = [
    m for m in Mech.all_types.values()
    if m.card_types != []
]
pilots = [
    p for p in Pilot.all_types.values()
    # if p.card_types != []
]
upgrades = [
    u for u in Upgrade.all_types.values()
    if u.card_types != []
]
rendered_html = template.render(
    mechs=mechs, pilots=pilots, upgrades=upgrades, Card=Card)

# Write the output to an HTML file
with open('templates/printout.html', 'w') as file:
    file.write(rendered_html)

print("Template rendered successfully!")
