import pkgutil

import hope_bitcaster as package


def test_imports():
    prefix = package.__name__ + "."
    for __, modname, __ in pkgutil.iter_modules(package.__path__, prefix):
        __import__(modname, fromlist="dummy")
