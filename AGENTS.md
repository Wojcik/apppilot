# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

AppPilot is an early-stage Python project for experimenting with LLM providers.
It is currently at milestone **M0**: send one prompt to Anthropic (Claude) and
OpenAI, then compare the answers and token usage.

## Layout

```
pyproject.toml        # project metadata, deps, dev group, `apppilot` script entry
uv.lock               # locked dependencies (managed by uv; never edit by hand)
.python-version       # 3.12
src/apppilot/
  __init__.py         # `main()` behind the `apppilot` console script (placeholder)
  llm.py              # M0: ask_claude / ask_openai + CLI comparison
```

Uses the `src/` layout with the `uv_build` backend. There is no `tests/`
directory yet.

## Setup and commands

Use [uv](https://docs.astral.sh/uv/) for everything; do not call `pip` directly.

```bash
uv sync                                   # install deps + dev group into .venv
uv run python -m apppilot.llm "a prompt"  # run the M0 comparison
uv run apppilot                           # console script (placeholder)
uv run ruff check .                       # lint
uv run ruff format .                      # format
uv run pytest                             # tests (put them under tests/)
```

Add dependencies with `uv add <pkg>` (or `uv add --dev <pkg>` for tooling) so
`pyproject.toml` and `uv.lock` stay in sync.

## Configuration and secrets

Settings come from a `.env` file in the repo root, loaded via `python-dotenv`:

| Variable            | Required | Purpose                                         |
| ------------------- | -------- | ----------------------------------------------- |
| `ANTHROPIC_API_KEY` | yes      | Read by the `anthropic` SDK                     |
| `OPENAI_API_KEY`    | yes      | Read by the `openai` SDK                        |
| `OPENAI_MODEL`      | yes      | OpenAI model id; `llm.py` exits if unset        |
| `ANTHROPIC_MODEL`   | no       | Claude model id; defaults to `claude-haiku-5-5` |

`.env` is git-ignored. Never commit it, print key values, or hard-code keys.
Running `llm.py` makes real, billed API calls; don't run it in automated checks
unless asked. Tests must mock the provider clients rather than hit the network.

## Code conventions

- Python 3.12+: use built-in generics and `X | None` (e.g. `tuple[str, int, int]`).
- Type-hint public functions and give them a short docstring stating the return shape.
- Keep modules small and script-like; each module may carry a top docstring
  with its milestone and a `Run:` line, as `llm.py` does.
- Provider helpers return plain tuples/values (`answer, input_tokens, output_tokens`)
  so results across providers are comparable.
- Prefer cheap, small models by default for experiments.
- Ruff runs with its default settings (no config in `pyproject.toml`). Run
  `ruff check` and `ruff format` on files you touch before committing.

## Commits

Short, imperative-ish summaries (e.g. "Bootstrap AppPilot: uv project, deps,
layout"). Keep changes focused on the task at hand.
