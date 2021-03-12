"""
Utilities to create context and configuration objects
"""
import argparse
from enum import Enum
from typing import List


class Cardinality(Enum):
    """
    Cardinality of a configuration parameter: multiple or singular
    """
    single = "single"
    multiple = "multiple"


class Argument:
    """
    A wrapper class to describe a command-line arguments
    This is practically, a more rigid format for
    :func ArgumentParser.add_argument:
    """
    def __init__(self, name,
                 help: str,
                 type = str,
                 aliases: List = None,
                 default = None,
                 cardinality: Cardinality = Cardinality.single,
                 valid_values = None
                 ):
        if aliases is None:
            aliases = []
        self.name = name
        self.type = type
        self.aliases = aliases
        if self.type == bool and default is None:
            self.default = False
        else:
            self.default = default
        self.cardinality = cardinality
        self.description = help
        self.choices = valid_values

        return

    def get_action(self):
        if self.type == bool:
            if not self.default:
                return 'store_true'
            return 'store_false'
        return None

    def get_nargs(self):
        if self.cardinality == Cardinality.single:
            return None
        if self.default:
            return '*'
        return '+'

    def get_help(self):
        if not self.is_required():
            h = self.description
            if h.strip() and h.strip()[-1] not in {'.', ','}:
                h += ', '
            h += "default: " + str(self.default)
            return h
        return self.description

    def is_required(self):
        return self.default is None

    def add_to(self, parser):
        args = ["--" + self.name]
        for alias in self.aliases:
            if len(alias) == 1:
                args.append("-" + alias)
            else:
                args.append("--" + alias)

        action = self.get_action()
        nargs = self.get_nargs()
        kwargs = {
            "default": self.default,
            "help": self.get_help(),
            "required": self.is_required()
        }
        if action:
            kwargs['action'] = action
        if nargs:
            kwargs['nargs'] = nargs
        if self.choices:
            kwargs["choices"] = self.choices
        parser.add_argument(*args, **kwargs)


class Context:
    """
    Generic class allowing to build context and configuration objects
    and initialize them using command line arguments
    """

    def __init__(self, subclass, description = None):
        """
        Creates a new object
        :param subclass: A concrete class containing configuration information
            Configuration options must be defined as class memebers with names,
            starting with one '_' characters and values be instances of
            :class Argument:
        :param description: Optional text to use as description.
            If not specified, then it is extracted from subclass documentation
        """
        if description:
            self.description = description
        else:
            self.description = subclass.__doc__
        self._attrs = [
            attr[1:] for attr in subclass.__dict__
                if attr[0] == '_' and attr[1] != '_'
        ]
        self.arguments = [getattr(subclass, '_'+attr) for attr in self._attrs]
        parser = argparse.ArgumentParser(self.description)
        for arg in self.arguments:
            arg.add_to(parser)

        args = parser.parse_args()
        for attr in self._attrs:
            setattr(self, attr, self.validate(attr, getattr(args, attr)))

    def __str__(self):
        return "; ".join([
            "{}: {}".format(attr, getattr(self, attr)) for attr in self._attrs
        ])

    def validate(self, attr, value):
        """
        Subclasses can override this method to implement custom handling
        of command line arguments
        :param attr: Command line argument name
        :param value: Value returned by argparse
        :return: value to use
        """
        return value

    @classmethod
    def enum(cls, enum_cls, s: str):
        """
        A helper method to return Enum value by its name

        :param cls: Enum class
        :param s: name of a member in Enum class
        :return: value of the member
        """
        d = {e.name: e for e in enum_cls}
        return d[s]
