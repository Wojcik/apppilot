# AppPilot learning journey

Each step has a lesson (what to build, where to look things up, hints you open one at a time)
and, where you write code, a checker test whose failures print `💡 HINT:` messages.

| Step | Lesson | Check it |
|---|---|---|
| M0 | Call two LLM providers and compare answers/tokens (`src/apppilot/llm.py`) | `uv run python -m apppilot.llm "hi"` |
| 3 | [Domain models](03-domain-models.md): `Review`, `Ticket`, `CrashReport`, `Release` | `uv run pytest tests/test_step03_models.py -q` |

How to work a step:
1. Read the lesson, then do the research part (real API docs) **before** writing code.
2. Write the code yourself.
3. Run the checker. Fix the first hint, run again.
4. Stuck? Open the next `<details>` hint in the lesson. Don't open them all at once.
5. Go through the self-review checklist, then commit.
