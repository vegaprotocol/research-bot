from typing import Callable

def by_key(response_list: list[dict], key_getter: Callable[[any], str]) -> dict[str, any]:
    """
    Takes list of dictionaries and key, then returns dictionary, where
    key is value of given <key>.
    """
    return { key_getter(item): item for item in response_list }