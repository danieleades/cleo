from __future__ import annotations

import pytest

from cleo._utils import find_similar_names
from cleo._utils import format_time


@pytest.mark.parametrize(  # type: ignore[misc]
    "input_secs,expected",
    [
        (0.1, "< 1 sec"),
        (1.0, "1 sec"),
        (2.0, "2 secs"),
        (59.0, "59 secs"),
        (60.0, "1 min"),
        (120.0, "2 mins"),
    ],
)
def test_format_time(input_secs: float, expected: str) -> None:
    assert format_time(input_secs) == expected


@pytest.mark.parametrize(
    ["name", "expected"],
    [
        ("", ["help", "foo1", "foo2", "bar1", "bar2", "foo bar1", "foo bar2"]),
        ("hellp", ["help"]),
        ("bar2", ["bar2", "bar1", "foo bar2"]),
        ("bar1", ["bar1", "bar2", "foo bar1"]),
        ("foo", ["foo1", "foo2", "foo bar1", "foo bar2"]),
    ],
)
def test_find_similar_names(name: str, expected: list[str]) -> None:
    names = ["help", "foo1", "foo2", "bar1", "bar2", "foo bar1", "foo bar2"]
    assert find_similar_names(name, names) == expected
