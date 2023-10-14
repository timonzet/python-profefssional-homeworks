#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper, wraps


def disable(f):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """
    return f if callable(f) else lambda f: f


def decorator(f):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def countcalls(func):
    """Decorator that counts calls made to the function decorated."""

    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        res = func(*args, **kwargs)
        return res

    wrapper.calls = 0
    return wrapper


def memo(f):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """
    cache = {}

    @wraps(f)
    def wrapper(*args):
        if args not in cache:
            cache[args] = f(*args)
        update_wrapper(wrapper, f)
        return cache[args]

    return wrapper


def n_ary(f):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """

    @wraps(f)
    def wrapper(x, *args):
        return x if not args else f(x, wrapper(*args))

    return wrapper


def trace(decor_arg):
    """Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....ss

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    """

    def decor_fib(f):
        @wraps(f)
        def wrapper(*args):
            prefix = decor_arg * wrapper.level
            arg = ", ".join(str(a) for a in args)
            print("{} --> {}({})".format(prefix, f.__name__, arg))
            wrapper.level += 1
            result = f(*args)
            print("{} <-- {}({}) == {}".format(prefix, f.__name__, arg, result))
            wrapper.level -= 1

            return result

        wrapper.level = 0

        return wrapper

    return decor_fib


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("____")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n - 1) + fib(n - 2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, "calls made")


if __name__ == "__main__":
    main()
