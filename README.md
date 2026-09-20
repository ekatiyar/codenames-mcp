# Codenames MCP

MCP server for playing Codenames on [horsepaste.com](https://www.horsepaste.com).

## How to Use

Clone this repository locally, and ensure you have `python3` and `uv` installed.

Claude Code automatically loads the project MCP server from `.mcp.json`, while 
Codex loads it from `.codex/config.toml`. This mcp server is automatically loaded
when either harness is started from this repository.

## Tools

- `operative_view(game_id)`
- `spymaster_view(game_id)`
- `guess(word, game_id)`
- `end_turn(game_id)`
- `next_game(game_id)` -- resets the board, keeping the same word pool and URL

`game_id` is required on every call. It is the slug from the game's URL
(`horsepaste.com/<game_id>`). This mcp server is stateless, with every call
fetching the latest data from the site's API.