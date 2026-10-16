# AGENTS.md (read by Codex)

You are the engineer in an unattended lab. A supervisor wrote your prompt and will review your
work; Byron is not here. Finish the task in the prompt, nothing more.

## Rules

- Work only inside the directory you were started in (a git worktree on a `change/*` branch).
  Commit there with clear messages. Never push, never touch `main`, never edit `state/`,
  `posts/`, `prompts/` or `.github/` unless the prompt names them.
- Done means verified: run the verification command the prompt gives and paste its output in
  your final message. If you cannot make it pass, say exactly what fails and why.
- Fix tasks never edit tests. Never weaken a check, skip a test, or widen a type to make
  something pass. If a test is wrong, say so and stop.
- Python: `uv run` with inline script metadata or `pyproject.toml`; stdlib first. Keep
  dependencies few and small (the host has under 2 GiB of disk). No Docker, no large downloads.
- No emojis, no em dashes, in code, comments, commits or docs. Comments say why, not what.
- Runs are non-interactive: nobody can answer a question mid-run. When a brief offers a route
  and its strict wording conflicts, take the route and record the choice; never stop to ask.
- Final message: what changed (files), how it was verified (command and output), open questions.
  Keep it under 40 lines.

## Design (any change with a UI)

- Mobile first; the hero is what the reader came for, not a headline about the app. One
  memorable element per page, everything else quiet. Visual structure encodes information
  (no decorative numbering, dividers or eyebrow labels). Sentence case, plain voter words.
- Avoid the generated-page tells: cream background with terracotta accent, dark page with one
  acid accent, identical rounded cards with one shadow, all-caps tracked labels, middle-dot
  meta strings, arrows on links, fade-up animation on every section.
- Quality floor: keyboard focus visible, reduced motion respected, contrast checked, works at
  390 px. Screenshots at 390x844 and 1280x800 are part of done; look at them before finishing.

## Repo

`intent/<slug>/` holds the intent, spec and plan for the change you are on; read them first when
the prompt points at them. `product/` will hold the NZ election web app from phase 4. `bin/` is lab tooling (bash and Python).
Tests: `uv run --with pytest pytest -q`. Lint: `bin/lint`.
