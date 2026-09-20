"""MCP server for playing Codenames on horsepaste.com through its JSON API:
  POST /game-state  {game_id, state_id} -> full game object, including the
                     true color layout for every cell (spymaster info).
  POST /guess        {game_id, index}    -> reveals a cell, returns new state.
  POST /end-turn      {game_id, current_round}
  POST /next-game     {game_id, word_set, create_new, timer_duration_ms, enforce_timer}

operative_view() hides colors for unrevealed cells. Use spymaster_view() only
when giving clues.
"""

from typing import Any

import requests
from mcp.server.mcpserver import MCPServer

BASE_URL = "https://www.horsepaste.com"

mcp = MCPServer("codenames")


def _fetch_state(game_id: str) -> dict[str, Any]:
    resp = requests.post(
        f"{BASE_URL}/game-state",
        json={"game_id": game_id, "state_id": ""},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _current_team(game: dict[str, Any]) -> str:
    if game["round"] % 2 == 0:
        return game["starting_team"]
    return "blue" if game["starting_team"] == "red" else "red"


def _remaining_counts(game: dict[str, Any]) -> dict[str, int]:
    counts = {"blue": 0, "red": 0}
    for color, revealed in zip(game["layout"], game["revealed"]):
        if not revealed and color in counts:
            counts[color] += 1
    return counts


def _public_fields(game: dict[str, Any]) -> dict[str, Any]:
    return {
        "game_id": game["id"],
        "round": game["round"],
        "turn": _current_team(game),
        "starting_team": game["starting_team"],
        "remaining": _remaining_counts(game),
        "winning_team": game.get("winning_team"),
    }


def _operative_cells(game: dict[str, Any]) -> list[dict[str, Any]]:
    cells = []
    for i, (word, revealed) in enumerate(zip(game["words"], game["revealed"])):
        cell = {"index": i, "word": word, "revealed": revealed}
        if revealed:
            cell["color"] = game["layout"][i]
        cells.append(cell)
    return cells


def _spymaster_cells(game: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"index": i, "word": word, "revealed": revealed, "color": color}
        for i, (word, revealed, color) in enumerate(
            zip(game["words"], game["revealed"], game["layout"])
        )
    ]


@mcp.tool()
def operative_view(game_id: str) -> dict[str, Any]:
    """Return the board as an operative sees it. Colors are hidden for cells
    that have not been revealed. Use this to decide what to guess.

    game_id is the slug from the game's URL, e.g. horsepaste.com/<game_id>."""
    game = _fetch_state(game_id)
    return {**_public_fields(game), "cells": _operative_cells(game)}


@mcp.tool()
def spymaster_view(game_id: str) -> dict[str, Any]:
    """Return the full board, including each cell's true color.
    Use this only when giving clues. In real Codenames, this is spymaster-only
    information."""
    game = _fetch_state(game_id)
    return {**_public_fields(game), "cells": _spymaster_cells(game)}


@mcp.tool()
def guess(word: str, game_id: str) -> dict[str, Any]:
    """Guess a word on the board and return the updated operative view.
    Raise an error if the word is missing, already revealed, or the game is
    over."""
    game = _fetch_state(game_id)
    words_by_name = {w.upper(): i for i, w in enumerate(game["words"])}
    index = words_by_name.get(word.strip().upper())
    if index is None:
        raise ValueError(f"{word!r} is not a word on this board")
    if game["revealed"][index]:
        raise ValueError(f"{word!r} has already been revealed")
    if game.get("winning_team"):
        raise ValueError(f"game is already over, {game['winning_team']} won")

    resp = requests.post(
        f"{BASE_URL}/guess",
        json={"game_id": game_id, "index": index},
        timeout=10,
    )
    resp.raise_for_status()
    updated = resp.json()
    return {
        "guessed_word": word.upper(),
        "revealed_color": updated["layout"][index],
        **_public_fields(updated),
        "cells": _operative_cells(updated),
    }


@mcp.tool()
def end_turn(game_id: str) -> dict[str, Any]:
    """End the acting team's turn, passing play to the other team."""
    game = _fetch_state(game_id)
    resp = requests.post(
        f"{BASE_URL}/end-turn",
        json={"game_id": game_id, "current_round": game["round"]},
        timeout=10,
    )
    resp.raise_for_status()
    updated = resp.json()
    return {**_public_fields(updated), "cells": _operative_cells(updated)}


@mcp.tool()
def next_game(game_id: str) -> dict[str, Any]:
    """Start a fresh game at the same URL with the same word pool.
    This wipes the current board, so call it only after the game ends or when
    you deliberately want to restart."""
    game = _fetch_state(game_id)
    resp = requests.post(
        f"{BASE_URL}/next-game",
        json={
            "game_id": game_id,
            "word_set": game["word_set"],
            "create_new": False,
            "timer_duration_ms": 0,
            "enforce_timer": False,
        },
        timeout=10,
    )
    resp.raise_for_status()
    updated = resp.json()
    return {**_public_fields(updated), "cells": _operative_cells(updated)}


if __name__ == "__main__":
    mcp.run()
