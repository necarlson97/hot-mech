from jinja2 import Environment, FileSystemLoader
import os

from src.game_state import GameState
from src.mech import Mech
from src.card import Card

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('printout.j2')

# Render the template with your data
gs = GameState()
mechs = [m(gs, gs.white) for m in Mech.all_types.values()]
rendered_html = template.render(mechs=mechs, Card=Card)

# Write the output to an HTML file
with open('templates/printout.html', 'w') as file:
    file.write(rendered_html)

print("Template rendered successfully!")
