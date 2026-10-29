"""Step 3 checker: domain models in src/apppilot/models.py.

Run:  uv run pytest tests/test_step03_models.py -q

Every failure message is a HINT, not just an error. Read it, fix one thing, run again.
The lesson (with field references and more hints) is in docs/learning/03-domain-models.md.
"""
import dataclasses
import importlib
import types
import typing
from datetime import date, datetime
from enum import Enum

import pytest

LESSON = "docs/learning/03-domain-models.md"

# For each model: concept -> (accepted field names, accepted types or None for "any").
# You choose the exact name; any name in the tuple counts. Add as many extra fields as you like.
DATES = (datetime, date)
REQUIRED: dict[str, dict[str, tuple[tuple[str, ...], tuple[type, ...] | None]]] = {
    "Review": {
        "id": (("id", "review_id"), None),
        "rating": (("rating", "star_rating", "stars"), (int,)),
        "text": (("text", "body", "comment", "content"), (str,)),
        "app version": (("app_version", "version", "version_name"), (str,)),
        "creation date": (("created_at", "created", "date", "submitted_at", "last_modified"), DATES),
    },
    "Ticket": {
        "id": (("id", "ticket_id", "key"), None),
        "subject": (("subject", "title", "summary"), (str,)),
        "description": (("description", "body", "text"), (str,)),
        "status": (("status", "state"), (str, Enum)),
        "creation date": (("created_at", "created", "opened_at"), DATES),
    },
    "CrashReport": {
        "id": (("id", "crash_id", "issue_id", "event_id"), None),
        "app version": (("app_version", "version", "release"), (str,)),
        "when it happened": (("occurred_at", "timestamp", "created_at", "crashed_at", "first_seen", "last_seen"), DATES),
        "what crashed": (
            ("exception_type", "exception", "error_type", "title", "error_message", "message"),
            (str,),
        ),
        "stack trace": (("stack_trace", "stacktrace", "frames", "backtrace"), None),
    },
    "Release": {
        "version": (("version", "version_string", "app_version", "version_name"), (str,)),
        "release date": (("released_at", "release_date", "published_at", "created_at"), DATES),
        "release notes": (("release_notes", "notes", "whats_new", "changelog"), (str,)),
    },
}


def _hint(msg: str) -> None:
    pytest.fail(f"\n💡 HINT: {msg}\n   (more help: {LESSON})", pytrace=False)


def _import_models():
    try:
        return importlib.import_module("apppilot.models")
    except ModuleNotFoundError:
        return None


def test_models_file_exists():
    if _import_models() is None:
        _hint("Create the file src/apppilot/models.py (it must be importable as `apppilot.models`).")


@pytest.fixture(scope="module")
def models():
    module = _import_models()
    if module is None:
        pytest.skip("create src/apppilot/models.py first")
    return module


def _fmt(tp) -> str:
    return tp.__name__ if isinstance(tp, type) else str(tp)


def _cls(models, name):
    cls = getattr(models, name, None)
    if cls is None:
        _hint(f"`{name}` is missing in models.py. Define `class {name}:` (spelling and case matter).")
    return cls


def _hints(cls):
    try:
        return typing.get_type_hints(cls)
    except NameError as e:
        _hint(f"{cls.__name__}: an annotation uses a name that isn't imported ({e}). Check your imports.")


def _base_types(tp) -> tuple:
    """`X | None` / Optional[X] -> (X,). Everything else -> (origin or tp,)."""
    origin = typing.get_origin(tp)
    if origin in (typing.Union, types.UnionType):
        return tuple(a for arg in typing.get_args(tp) if arg is not type(None) for a in _base_types(arg))
    return (origin or tp,)


def _type_ok(tp, allowed: tuple[type, ...]) -> bool:
    return all(isinstance(b, type) and issubclass(b, allowed) for b in _base_types(tp))


@pytest.mark.parametrize("name", list(REQUIRED))
def test_is_frozen_dataclass(models, name):
    cls = _cls(models, name)
    if not dataclasses.is_dataclass(cls):
        _hint(f"`{name}` is a plain class. Put `@dataclass(frozen=True)` on the line above `class {name}:`.")
    if not cls.__dataclass_params__.frozen:
        _hint(f"`{name}` is a dataclass but not frozen. Use `@dataclass(frozen=True)` so instances can't change.")


@pytest.mark.parametrize("name", list(REQUIRED))
def test_has_real_world_fields(models, name):
    cls = _cls(models, name)
    if not dataclasses.is_dataclass(cls):
        pytest.skip("fix test_is_frozen_dataclass first")
    fields = _hints(cls)
    for concept, (names, allowed) in REQUIRED[name].items():
        found = [n for n in names if n in fields]
        if not found:
            _hint(
                f"`{name}` has no field for its {concept}. Look at what the real API returns "
                f"(links in the lesson). Accepted names: {', '.join(names)}."
            )
        if allowed and not _type_ok(fields[found[0]], allowed):
            want = " or ".join(t.__name__ for t in allowed)
            _hint(
                f"`{name}.{found[0]}` is annotated as `{_fmt(fields[found[0]])}`, expected {want}. "
                + ("Dates should be real `datetime` objects, not strings: you can compare and sort them."
                   if allowed is DATES else "Pick the type that matches what the value really is.")
            )


@pytest.mark.parametrize("name", list(REQUIRED))
def test_no_mutable_collections(models, name):
    cls = _cls(models, name)
    if not dataclasses.is_dataclass(cls):
        pytest.skip("fix test_is_frozen_dataclass first")
    for field, tp in _hints(cls).items():
        if any(b in (list, dict, set) for b in _base_types(tp)):
            _hint(
                f"`{name}.{field}` is a `{_fmt(tp)}`. frozen=True stops reassigning the field, but the list/dict "
                f"itself can still be changed. Use `tuple[str, ...]` (or `frozenset`) instead."
            )


def test_review_rating_is_validated(models):
    """Stretch goal: a Review with rating 6 should be impossible to create."""
    cls = _cls(models, "Review")
    if not hasattr(cls, "__post_init__"):
        pytest.skip("stretch goal: add __post_init__ to Review that rejects ratings outside 1..5")
