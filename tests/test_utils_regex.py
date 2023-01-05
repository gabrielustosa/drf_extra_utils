import re

from drf_extra_utils.utils.regex import match_iterator_pattern


def test_match_iterator_pattern():
    given = ['test', 'list', 'page(1)']

    pattern = re.compile(r'page\(([0-9_]+)\)')
    match = match_iterator_pattern(pattern, given)

    assert match == '1'


def test_match_iterator_pattern_return_first_match():
    given = ['test', 'list', 'page(3)', 'page(1)']

    pattern = re.compile(r'page\(([0-9_]+)\)')
    match = match_iterator_pattern(pattern, given)

    assert match == '3'


def test_match_iterator_pattern_default_value():
    given = ['test', 'list']

    pattern = re.compile(r'page\(([0-9_]+)\)')
    match = match_iterator_pattern(pattern, given, 'default')

    assert match == 'default'


def test_match_iterator_pattern_without_default_value():
    given = ['test', 'list']

    pattern = re.compile(r'page\(([0-9_]+)\)')
    match = match_iterator_pattern(pattern, given)

    assert match is None
