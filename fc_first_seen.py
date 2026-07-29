"""Durable first-seen dates for FC entities.

The FC identity tables are dropped and rebuilt from current source state on
every run, so any date computed at generation time says "today" forever. Before
this module, `created_at` was stamped with `date.today()` on every row on every
hourly run — a student onboarded last November read as created this morning.

The fix is to keep the memory outside the regenerated tables. `fc_first_seen.csv`
is a committed, append-only-in-practice record of the first date each FC id was
observed. It is read before generation and rewritten after: an id gains a row the
first time it is seen and its date never changes again. A wiped or half-written
Sheet cannot reset it, because the seed file is the authority, not the tab.

Entities that have left are deliberately kept. Their row is the only remaining
evidence they were ever here.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

SEED_FILENAME = "fc_first_seen.csv"
SEED_FIELDS = ["key", "first_seen"]

# Where the date came from, for rows we backfilled rather than observed live.
# Registry git history only reaches the standalone-repo split, so students
# present at that commit are "on or before" that date, not "joined on" it.
OBSERVATION_START = "2026-04-15"


def seed_path(base_dir: Path) -> Path:
    return Path(base_dir) / SEED_FILENAME


def load_first_seen(base_dir: Path) -> dict[str, str]:
    """Read the committed seed file. Missing file is not an error — it means
    this is the first run, and every entity is seen today."""
    path = seed_path(base_dir)
    if not path.exists():
        return {}

    memo: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row.get("key") or "").strip()
            value = (row.get("first_seen") or "").strip()
            if key and value:
                memo[key] = value
    return memo


def save_first_seen(base_dir: Path, memo: dict[str, str]) -> Path:
    """Rewrite the seed file, sorted so diffs are readable in review."""
    path = seed_path(base_dir)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEED_FIELDS)
        writer.writeheader()
        for key in sorted(memo):
            writer.writerow({"key": key, "first_seen": memo[key]})
    return path


# Which fields identify each entity, in preference order. The sheet reader and
# the writer both key off this, so they cannot drift apart and start disagreeing
# about what counts as "the same student".
KEY_SPECS = {
    "FC_Students": (["mms_student_id"], ["fc_student_id"]),
    "FC_People": (["email"], ["fc_person_id"]),
    "FC_Tutors": (["mms_teacher_id"], ["fc_tutor_id"]),
    "FC_Parent_Student_Links": (["id"], None),
    "FC_External_IDs": (
        ["external_system", "external_key", "external_value"],
        ["fc_entity_id", "external_system", "external_key"],
    ),
}


# Key fields whose raw value is personal data and must never reach the seed file,
# which is committed to git. Email is the only stable anchor we have for a parent
# (they have no MMS id), so it cannot simply be dropped — it is digested instead.
# Same idiom as make_fc_id in generate_fc_ids.py: deterministic, so the key stays
# stable across runs and still matches what the sheet reader composes.
HASHED_KEY_FIELDS = {"email"}


def _key_part(field: str, value: str) -> str:
    if field in HASHED_KEY_FIELDS and value:
        return hashlib.sha256(value.lower().encode("utf-8")).hexdigest()[:16]
    return value


def _compose(table: str, row: dict, key_fields: list) -> str:
    parts = [
        _key_part(field, str(row.get(field, "") or "").strip())
        for field in key_fields
    ]
    if not any(parts):
        return ""
    return f"{table}:" + "|".join(parts)


def compose_key(table: str, row: dict, key_fields=None, fallback_key_fields=None) -> str:
    """Build the memo key for a row. Passing no fields uses KEY_SPECS, which is
    what callers reading existing rows back out of Sheets should do."""
    if key_fields is None:
        key_fields, fallback_key_fields = KEY_SPECS.get(table, (None, None))
        if key_fields is None:
            return ""
    if isinstance(key_fields, str):
        key_fields = [key_fields]
    if isinstance(fallback_key_fields, str):
        fallback_key_fields = [fallback_key_fields]

    key = _compose(table, row, key_fields)
    if not key and fallback_key_fields:
        key = _compose(table, row, fallback_key_fields)
    return key


def _is_date(value: str) -> bool:
    parts = str(value or "").strip().split("-")
    return len(parts) == 3 and all(p.isdigit() for p in parts) and len(parts[0]) == 4


def merge_first_seen(memo: dict[str, str], observed: dict[str, str]) -> int:
    """Fold dates observed elsewhere (the live tabs) into the memo.

    Earliest wins. "First seen" can only ever move backwards as we learn more —
    a later date is never new information about when something started. This is
    what makes the merge safe to run against tabs that still hold the old
    generation-time stamps: those dates are always later, so they lose.

    Returns the number of keys the memo gained or corrected.
    """
    changed = 0
    for key, value in observed.items():
        if not key or not _is_date(value):
            continue
        current = memo.get(key)
        if current is None or (_is_date(current) and value < current):
            memo[key] = value
            changed += 1
    return changed


def apply_first_seen(
    table: str,
    rows: list,
    key_fields,
    memo: dict[str, str],
    today: str,
    fallback_key_fields=None,
) -> int:
    """Set each row's `created_at` to the first date we ever saw it.

    `key_fields` is one field name or several — several are joined, which is how
    FC_External_IDs is keyed (one entity has many mappings). Rows are mutated in
    place and the number of newly-observed entities is returned.

    Key choice is the whole game here, and it must be an *externally stable*
    anchor rather than an FC id. FC ids are deterministic hashes of whatever
    seed was available at the time, so a student's fc_student_id changes the
    moment their MMS id appears — keying on it would silently reset their
    first-seen date on exactly the day we learned more about them. Prefer the
    MMS/Stripe/email anchor and keep the FC id only as a fallback for entities
    that genuinely have no external identifier yet.

    This never *lowers* a stored date. An id that reappears after a gap keeps
    its original first-seen; rejoining is not being created again.
    """
    if isinstance(key_fields, str):
        key_fields = [key_fields]
    if isinstance(fallback_key_fields, str):
        fallback_key_fields = [fallback_key_fields]

    new_count = 0
    for row in rows:
        key = _compose(table, row, key_fields)
        if not key and fallback_key_fields:
            key = _compose(table, row, fallback_key_fields)

        if not key:
            # No identity to remember it by — fall back to today rather than
            # inventing a shared key that would collide across rows.
            row["created_at"] = today
            continue

        if key not in memo:
            memo[key] = today
            new_count += 1
        row["created_at"] = memo[key]

    return new_count
