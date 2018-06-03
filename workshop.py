"""
Make sure you've followed the install instructions in README.md,
then read through this file.

You can modify the "features" or improve the tests, then run

    pytest workshop.py

to see how it works!

Your goal is to fix each of the features, then make tests pass again.

"""

import json
from collections import Counter

from hypothesis import given, strategies as st


##############################################################################


def sort_a_list(lst):
    # TODO: sort the list however you wish (use a builtin OR write a sort func)
    # Consider writing the test first so you see it fail!
    return sorted(lst)


@given(lst=st.lists(st.integers()))
def test_sort_a_list(lst):
    # Note: even before the assertion, we're checking that sort_a_list
    #  doesn't raise an exception for any list of integers!
    new = sort_a_list(lst.copy())
    assert Counter(lst) == Counter(new)  # sorted list must have same elements
    # TODO: assert that the list is in correct order
    assert all(i <= j for i, j in zip(lst, lst[1:]))


##############################################################################


@given(st.lists(st.integers(min_value=1), min_size=2))
def test_sum_of_list_greater_than_max(lst):
    # TODO: *without* changing the test body, write the most general
    #       argument to @given that will pass for lists of integers.
    # hint: both lists() and integers() take arguments that will help.
    #       See https://hypothesis.readthedocs.io/en/latest/data.html
    assert max(lst) < sum(lst)


##############################################################################


def leftpad(string, width, fillchar):
    # TODO: if len(string) < width, add fillchar to the left until it isn't.
    # Bonus points for finding a trivial or pythonic solution.
    return string.rjust(width, fillchar)


@given(st.text(), st.integers(0, 1000), st.characters())
def test_leftpad(string, width, fillchar):
    # TODO: allow any length from zero up to e.g. 1000 (capped for performance)
    padded = leftpad(string, width, fillchar)
    assert len(padded) == max(width, len(string))
    assert padded.endswith(string)
    # TODO: assert that correct padding has been added
    # (the trick is to write code and tests which will have different bugs)
    if width > len(string):
        # We already checked that the length is correct and that the string is
        # in the right place, so we can check padding content without length.
        assert set(padded[:-len(string)]) == {fillchar}


##############################################################################


class Record(object):
    # Consider using the `attrs` package (attrs.org) to reduce boilerplate.

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Record(value={!r})'.format(self.value)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def to_json(self):
        return json.dumps(self.value)

    @classmethod
    def from_json(cls, string):
        value = json.loads(string)
        return cls(value)


# Passinga zero-arg function to `deferred` lets us write recursive definitions!
json_strat = st.deferred(lambda: st.one_of(
    # JSON values are defined as nil, false, true, number, string, ...
    st.none(), st.booleans(), st.floats(allow_nan=False), st.text(),
    # or arrays of json, or "objects" ie string: json dictionaries.
    st.lists(json_strat), st.dictionaries(st.text(), json_strat)
))


# `builds` draws an example from `json_strat`, then calls Record(value=...)
@given(st.builds(Record, value=json_strat))
def test_record_json_roundtrip(record):
    string = record.to_json()
    new = Record.from_json(string)
    #assert record == new
    # TODO: fix the first problem in the code being tested
    # TODO: fix the second problem by using hypothesis.assume in the test,
    #       or an argument to one of the strategies defining json

    # Option A:  see allow_nan=False; excluding from input is good if possible
    # Option B:  best way to deal with edge cases if A is not available
    from hypothesis import assume
    assume(record == record)  # if False, abort test and make another attempt
    assert record == new
    # Option C:  weaker, because we may only rarely check the assertion
    if record == record:
        assert record == new
