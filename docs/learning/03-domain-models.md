# Step 3 — Domain models

> **Task:** create `src/apppilot/models.py` with four frozen dataclasses: `Review`, `Ticket`,
> `CrashReport`, `Release`. Give them the fields the real things have (ids, dates, app version,
> rating, text…).

**Check your work at any time:**

```bash
uv run pytest tests/test_step03_models.py -q
```

Each failing test prints a `💡 HINT:` that says what's missing. Fix one thing and run the check again.
You're done when everything passes. The last test is a stretch goal and is skipped until you try it.

---

## Why this step matters

AppPilot will pull data from app stores, a help desk, a crash reporter and your release history,
then give it to an LLM. Every source returns its own messy JSON. Models give the rest of your code
**one clean, typed shape** per thing, no matter where it came from. `frozen=True` means once a
`Review` is built it can't be changed by accident halfway through the pipeline.

## The pattern

This example uses a model that is *not* one of your four:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AppInfo:
    """One app we track."""

    id: str                      # the store's id, kept as text even if it looks like a number
    name: str
    platform: str                # "ios" | "android"
    bundle_id: str               # e.g. "com.example.app"
    created_at: datetime
    icon_url: str | None = None  # optional fields (with defaults) go LAST
```

```python
>>> app = AppInfo("123", "Pilot", "ios", "com.x.pilot", datetime(2026, 1, 1))
>>> app.name = "Other"
dataclasses.FrozenInstanceError: cannot assign to field 'name'
```

## Your job: research first, then code

Don't guess the fields. Open the real API docs and write down what each source returns.
This is the core skill for this step. For each model, fill in a table like this in your notes:

| Field in the API | What it means | Keep it? | My name + type |
|---|---|---|---|
| `starRating` | 1–5 stars | yes | `rating: int` |

### Where to look

| Model | Real-world sources (read the "attributes" / "fields" / "schema" section) |
|---|---|
| **Review** | Apple: [App Store Connect API — CustomerReview](https://developer.apple.com/documentation/appstoreconnectapi/customerreview) · Google: [Play Developer API — reviews](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews) (open the `Review` and `UserComment` objects) |
| **Ticket** | [Zendesk — Tickets](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/) (the "JSON format" table) · or [Linear GraphQL `Issue`](https://linear.app/developers/graphql) / Jira issue fields if your team uses those |
| **CrashReport** | [Firebase Crashlytics — BigQuery export schema](https://firebase.google.com/docs/crashlytics/bigquery-export) · [Sentry — list a project's issues](https://docs.sentry.io/api/events/list-a-projects-issues/) |
| **Release** | Apple: [App Store Connect API — AppStoreVersion](https://developer.apple.com/documentation/appstoreconnectapi/appstoreversion) · Google: [Play Developer API — edits.tracks](https://developers.google.com/android-publisher/api-ref/rest/v3/edits.tracks) · [GitHub Releases](https://docs.github.com/en/rest/releases/releases) |

Python reference: [`dataclasses`](https://docs.python.org/3/library/dataclasses.html).

### What the checker requires (the minimum)

You choose the names, and any name from the "accepted" list passes. Add any other fields you find useful.

| Model | Must have a field for… |
|---|---|
| Review | id · rating (`int`) · text (`str`) · app version (`str`) · creation date (`datetime`) |
| Ticket | id · subject (`str`) · description (`str`) · status (`str` or an `Enum`) · creation date (`datetime`) |
| CrashReport | id · app version (`str`) · when it happened (`datetime`) · what crashed (`str`) · stack trace |
| Release | version (`str`) · release date (`datetime`/`date`) · release notes (`str`) |

All four must be `@dataclass(frozen=True)` and must not use `list` / `dict` / `set` fields.

---

## Hints

Open these one at a time, only when you're stuck.

<details>
<summary><b>Hint 1:</b> my tests say "no field for its creation date" but I have <code>date: str</code></summary>

The checker found the field but wants a real `datetime`. A string like `"2026-10-01T12:00:00Z"`
can't be compared or sorted by time, and it can't be subtracted. Converting from JSON strings is a
later step (parsing). Your model should hold the *clean* value:
`from datetime import datetime` and `created_at: datetime`.
</details>

<details>
<summary><b>Hint 2:</b> what type should <code>id</code> be?</summary>

Usually `str`, even when the id looks numeric. Ids are labels, not numbers: you never add them
together, and some sources mix in letters (Jira `APP-123`, Sentry hex ids). The checker accepts any type
for `id`.
</details>

<details>
<summary><b>Hint 3:</b> "TypeError: non-default argument follows default argument"</summary>

In a dataclass, every field with a default value (`= None`, `= ""`) must come **after** all fields
without one. Move optional fields to the bottom.
</details>

<details>
<summary><b>Hint 4:</b> "list is still mutable"? But I used <code>frozen=True</code>!</summary>

`frozen` blocks `review.tags = [...]`. It does **not** block `review.tags.append("x")`.
Use `tags: tuple[str, ...] = ()` for a truly read-only collection. For a stack trace,
`tuple[str, ...]` (one string per frame) or a single `str` both work.
</details>

<details>
<summary><b>Hint 5:</b> status / platform / priority: string or Enum?</summary>

A plain `str` passes. An `Enum` is better because a typo like `"opne"` becomes impossible:

```python
from enum import Enum

class TicketStatus(str, Enum):
    NEW = "new"
    OPEN = "open"
    ...
```
Then `status: TicketStatus`. Look at the docs for the real list of statuses.
</details>

<details>
<summary><b>Hint 6:</b> one source has a field the other doesn't (e.g. Apple reviews have a title, Google's don't)</summary>

Your model is the *union of what's useful*, not a copy of one API. Fields that only some sources
have become optional: `title: str | None = None`. Also add a `source` / `platform` field so you
always know where a record came from.
</details>

<details>
<summary><b>Hint 7:</b> half a skeleton for <code>Review</code></summary>

```python
@dataclass(frozen=True)
class Review:
    id: str
    platform: str          # where it came from
    rating: int            # 1..5
    # text?  app version?  when was it written?  who wrote it?  language/country?
    # ...look at UserComment in the Google docs and CustomerReview in the Apple docs
```
</details>

<details>
<summary><b>Stretch goal:</b> validate the rating</summary>

A frozen dataclass can still check its inputs in `__post_init__`:

```python
def __post_init__(self) -> None:
    if not 1 <= self.rating <= 5:
        raise ValueError(f"rating must be 1..5, got {self.rating}")
```
Once you add this, the stretch test stops skipping. Try the same idea elsewhere, for example a
`Release` version that can't be an empty string.
</details>

---

## Self-review before moving on

- [ ] `uv run pytest tests/test_step03_models.py -q` passes
- [ ] For every field, I can name the API field(s) it comes from
- [ ] Optional fields have defaults and come last
- [ ] Each class has a one-line docstring
- [ ] `uv run ruff check src/` is clean
- [ ] In `uv run python`, I built one of each and confirmed I can't change it
