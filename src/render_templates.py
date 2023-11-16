from jinja2 import Environment, FileSystemLoader
import os
import glob

from src.game_state import GameState
from src.mech import Mech
from src.pilot import Pilot
from src.upgrade import Upgrade
from src.card import Card
from src.player import Player

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

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

for template_file in glob.glob('templates/*.j2'):
    # Extract the template name without extension
    template_name = os.path.basename(template_file).split('.')[0]
    rendered_html = env.get_template(f'{template_name}.j2').render(
        mechs=mechs, pilots=pilots, upgrades=upgrades, Card=Card,
        Player=Player,
    )

    # Write the output to an HTML file
    with open(f'templates/{template_name}.html', 'w') as file:
        print(f"Rendered {template_name} {rendered_html[200:220]}...")
        file.write(rendered_html)
