import re

"""
Module of handy utilities
"""

# TODO clamp

def camel_to_hypens(text):
    return re.sub('([a-z0-9])([A-Z])', '\\1-\\2', text).lower()

def snake_to_title(text):
    return (
        ' '.join(word.title() for word in re.split('[_-]', text) if word)
    )
