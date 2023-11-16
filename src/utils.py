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

def get_range(range_a, range_b=None):
    """
    Given a min and max, return a tuple of min, max.
    If a single tuple argument is given, return it.
    If two arguments are given, order them and return as (min, max).
    """
    if isinstance(range_a, tuple):
        return range_a
    else:
        if range_b is not None:
            return (min(range_a, range_b), max(range_a, range_b))
        else:
            return (0, range_a)

class NamedClassMeta(type):
    """
    Just a little helper metaclass to keep track of each types name
    even without instantiation
    """
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        new_class.name = camel_to_hypens(name)
        return new_class

class NamedClass(metaclass=NamedClassMeta):
    """
    Parent class that help keep track of the names of a type with many
    subtypes (such as cards, mechs, etc)
    """

    @classmethod
    def human_name(cls):
        return snake_to_title(cls.name)

    @classmethod
    def short_name(cls):
        # 1s word plus 1st letter of next word
        words = cls.name.split('-')
        if len(words) == 1:
            return words[0]
        return words[0].title() + cls.name.split('-')[1][0].title()

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()

    # A dict that holds all defined subtypes by:
    # string of class name -> type
    # (just for checking name conflicts)
    all_named_types = {}
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register each subclass in the all_cards dictionary
        cls.all_named_types[cls.__name__] = cls
        # TODO check for conflict here
