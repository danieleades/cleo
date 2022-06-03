from __future__ import annotations

import math

from dataclasses import dataclass
from html.parser import HTMLParser

from pylev import levenshtein


class TagStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)

        self.reset()
        self.fed: list[str] = []

    def handle_data(self, d: str) -> None:
        self.fed.append(d)

    def handle_entityref(self, name: str) -> None:
        self.fed.append("&%s;" % name)

    def handle_charref(self, name: str) -> None:
        self.fed.append("&#%s;" % name)

    def get_data(self) -> str:
        return "".join(self.fed)


def _strip(value: str) -> str:
    s = TagStripper()
    s.feed(value)
    s.close()

    return s.get_data()


def strip_tags(value: str) -> str:
    while "<" in value and ">" in value:
        new_value = _strip(value)
        if value.count("<") == new_value.count("<"):
            break

        value = new_value

    return value


def find_similar_names(name: str, names: list[str]) -> list[str]:
    """
    Finds names similar to a given command name.
    """
    threshold = 1e3
    distance_by_name = {}
    suggested_names = []

    for actual_name in names:
        # Get Levenshtein distance between the input and each command name
        distance = levenshtein(name, actual_name)

        is_similar = distance <= len(name) / 3
        is_sub_string = actual_name.find(name) != -1

        if is_similar or is_sub_string:
            distance_by_name[actual_name] = (
                distance,
                actual_name.find(name) if is_sub_string else float("inf"),
            )

    # Only keep results with a distance below the threshold
    distance_by_name = {
        k: v for k, v in distance_by_name.items() if v[0] < 2 * threshold
    }

    # Display results with shortest distance first
    for k, _v in sorted(distance_by_name.items(), key=lambda i: (i[1][0], i[1][1])):
        if k not in suggested_names:
            suggested_names.append(k)

    return suggested_names


@dataclass
class TimeFormat:
    threshold: int
    alias: str
    divisor: int | None = None

    def apply(self, secs: float) -> str:
        if self.divisor:
            return f"{math.ceil(secs / self.divisor)} {self.alias}"
        return self.alias


_TIME_FORMATS: list[TimeFormat] = [
    TimeFormat(0, "< 1 sec"),
    TimeFormat(2, "1 sec"),
    TimeFormat(59, "secs", 1),
    TimeFormat(60, "1 min"),
    TimeFormat(3600, "mins", 60),
    TimeFormat(5400, "1 hr"),
    TimeFormat(86400, "hrs", 3600),
    TimeFormat(129600, "1 day"),
    TimeFormat(604800, "days", 86400),
]


def format_time(secs: float) -> str:
    format = next(fmt for fmt in _TIME_FORMATS if secs <= fmt.threshold)
    return format.apply(secs)
