"""FC ID formula and FC student ID resolution.

This module is the brain's single home for the FC ID formula. The dashboard
mirrors the student formula in lib/admin/fc-id.mjs; neither repo can import the
other, so both pin the same golden value in their tests
(sdt_WFQ7Js -> fc_std_fa157fc5). If either side changes the formula, that test
fails on the side that moved.

An FC student ID is minted once and then stored. The stored value wins over
the formula. Until 2026-09 the dashboard minted from forename:surname:email while
this job recomputed from the MMS ID every hour, so 63 students carried two
different IDs and brain lookup could not find them by the one the dashboard
shows. See music-school-dashboard/docs/plans/active/fc-student-id-convergence.md.
"""

import hashlib
import re

FC_STUDENT_ID_PATTERN = re.compile(r"^fc_std_[0-9a-f]{8}$")

FLAG_CONFLICT = "FC ID CONFLICT"
FLAG_MALFORMED = "FC ID MALFORMED"
FLAG_DUPLICATE = "FC ID DUPLICATE"


def make_fc_id(prefix: str, seed: str) -> str:
    """Deterministic FC ID: fc_{prefix}_{first 8 hex chars of sha256(seed)}."""
    h = hashlib.sha256(seed.encode()).hexdigest()[:8]
    return f"fc_{prefix}_{h}"


def _valid(value) -> str:
    value = (value or "").strip()
    return value if FC_STUDENT_ID_PATTERN.match(value) else ""


def assign_fc_student_ids(candidates: dict) -> tuple[dict, dict]:
    """Choose one FC student ID per MMS student.

    candidates: {mms_id: (registry_fc_student_id, sheets_fc_student_id)}
    Returns ({mms_id: fc_student_id}, {mms_id: [(flag_type, detail), ...]}).

    Order of preference: registry value, then the Students sheet cell, then the
    formula over the MMS ID. The registry wins a disagreement because it is the
    record the dashboard and portal read; the sheet cell is a second copy.

    A stored value that is malformed, or that would give two students the same
    ID, is set aside for the derived one and flagged rather than failing the
    run — an hourly job should not stop over a data condition, and a derived ID
    is unique per MMS ID, so the result is always a valid one-to-one map.
    """
    assigned = {}
    sources = {}
    flags = {}

    def flag(mms_id, flag_type, detail):
        flags.setdefault(mms_id, []).append((flag_type, detail))

    for mms_id, (registry_raw, sheets_raw) in candidates.items():
        registry_raw = (registry_raw or "").strip()
        sheets_raw = (sheets_raw or "").strip()
        registry_id = _valid(registry_raw)
        sheets_id = _valid(sheets_raw)

        if registry_raw and not registry_id:
            flag(mms_id, FLAG_MALFORMED, f"registry={registry_raw}")
        if sheets_raw and not sheets_id:
            flag(mms_id, FLAG_MALFORMED, f"sheets={sheets_raw}")
        if registry_id and sheets_id and registry_id != sheets_id:
            flag(mms_id, FLAG_CONFLICT, f"registry={registry_id} vs sheets={sheets_id}")

        if registry_id:
            assigned[mms_id], sources[mms_id] = registry_id, "registry"
        elif sheets_id:
            assigned[mms_id], sources[mms_id] = sheets_id, "sheets"
        else:
            assigned[mms_id], sources[mms_id] = make_fc_id("std", mms_id), "derived"

    # Resolve shared IDs. Each pass moves every stored holder of a shared ID to
    # its own derived ID; derived IDs are distinct per MMS ID, so this settles
    # in at most two passes (the second catches a stored ID that happened to
    # equal another student's derived one).
    while True:
        holders = {}
        for mms_id in sorted(assigned):
            holders.setdefault(assigned[mms_id], []).append(mms_id)
        shared = {fc_id: ids for fc_id, ids in holders.items() if len(ids) > 1}
        movable = [
            (fc_id, mms_id)
            for fc_id, ids in shared.items()
            for mms_id in ids
            if sources[mms_id] != "derived"
        ]
        if not movable:
            break
        for fc_id, mms_id in movable:
            others = [other for other in shared[fc_id] if other != mms_id]
            flag(mms_id, FLAG_DUPLICATE, f"{fc_id} also held by {', '.join(others)}; using derived id")
            assigned[mms_id], sources[mms_id] = make_fc_id("std", mms_id), "derived"

    return assigned, flags
