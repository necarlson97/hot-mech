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

class NamedClassMeta(type):
    # Just a little helper metaclass to keep track of each types name
    # even without instantiation
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

    def __str__(self):
        return f"{self.name} {self.steps}"

    def __repr__(self):
        return self.__str__()
