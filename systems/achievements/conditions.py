from __future__ import annotations

from typing import Callable, Dict

from systems.core.event_bus import Event


def rating_tier_at_least(event: Event, params: dict, state: dict) -> bool:
    return event.data.get("rating_tier") == params["tier"]


def event_count_at_least(event: Event, params: dict, state: dict) -> bool:
    key = "count:" + event.type
    state[key] = state.get(key, 0) + 1
    return state[key] >= params["count"]


def field_equals(event: Event, params: dict, state: dict) -> bool:
    return event.data.get(params["field"]) == params["value"]


def rating_tier_count_at_least(event: Event, params: dict, state: dict) -> bool:
    if event.data.get("rating_tier") != params["tier"]:
        return False
    key = f"tier_count:{params['tier']}"
    state[key] = state.get(key, 0) + 1
    return state[key] >= params["count"]


def flagged_perfect(event: Event, params: dict, state: dict) -> bool:
    return event.data.get("rating_tier") == params["tier"] and event.data.get("no_mistakes") is True


CONDITION_CHECKS: Dict[str, Callable] = {
    "rating_tier_at_least": rating_tier_at_least,
    "event_count_at_least": event_count_at_least,
    "field_equals": field_equals,
    "rating_tier_count_at_least": rating_tier_count_at_least,
    "flagged_perfect": flagged_perfect,
}
