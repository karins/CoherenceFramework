"""
This module declares a helper class which can be used as a decorator to declare commands.

A command function should receive an empty argument parser and configure it.
As part of the configuration process, the function should assign a default function to be called in case the command is used.

@author: wilkeraziz
"""

from collections import defaultdict

_COMMANDS_ = defaultdict(dict)


class command(object):
    """
    A command decorator which accepts two arguments (the command name and its group, e.g 'sgml', 'preprocessing')
    """

    def __init__(self, name, cls=''):

        self.name_ = name
        self.cls_ = cls

    def __call__(self, command):
        existing = _COMMANDS_[self.cls_].get(self.name_, None)
        if existing is not None and existing is not command:
            raise Exception('Conflicting command: %s (class=%s)', self.name_, self.cls_)
        _COMMANDS_[self.cls_][self.name_] = command
        return command


def itercommands(cls):
    """iterates over commands of a given class"""
    return _COMMANDS_[cls].iteritems()


def iterclasses():
    return _COMMANDS_.iterkeys()
