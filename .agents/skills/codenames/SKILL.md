---
name: codenames
description: Play one turn of Codenames as spymaster or operative via the codenames MCP.
disable-model-invocation: true
---

# Codenames

Invoke with three tokens: `<game_id> <team> <role>`, e.g. `pointing-spread blue operative`.
`team` is `blue` or `red`, `role` is `spymaster` or `operative`. Ask for any missing arguments
before doing anything else.

Uses the `codenames` MCP: `operative_view`, `spymaster_view`, `guess`, `end_turn`, `next_game`.
Every call takes `game_id`.

Check `turn` on the view before acting. If it isn't `team`'s turn, or `winning_team` is set,
report that and stop.

## Spymaster

Enemy operatives hear your final answer, not your thinking. Keep board words, colors, and
reasoning in your thinking. The final answer holds only the clue and count.

1. Call `spymaster_view`.
2. In thinking, pick one clue word (not a board word, not a substring or superstring of one)
   connecting as many unrevealed `team` words as possible, avoiding the assassin and the other
   team's words.
3. Final answer: the clue and count, nothing else. For example, `ocean 3`.

**DO NOT** guess, end the turn, or leak a board word, color, or reasoning into the final answer.

## Operative

1. Call `operative_view`. The clue and count come from the user's message.
2. Rank unrevealed words by fit to the clue, most confident first, capped at count + 1 guesses.
3. Guess them in that order. Stop the moment a guess reveals a color other than `team`'s, or
   once you run out of confident matches.
4. Call `end_turn` if still on your turn.
5. Report each word guessed (`word -> color`) with a brief summary of why you picked it. No board dump.

**DO NOT** call `spymaster_view`.
