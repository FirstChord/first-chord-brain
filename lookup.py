"""
FC Identity Layer — Unified Entity Lookup
==========================================
Search by name, FC ID, MMS ID, Stripe ID, or any external key.
Works offline from local CSVs (always fast).

Usage (CLI):
    python3 lookup.py "Ryan Ofee"
    python3 lookup.py fc_std_e0938e46
    python3 lookup.py sdt_2grxJL
    python3 lookup.py cus_R7DL79Smc0cwBE

Usage (module):
    from lookup import lookup
    result = lookup("Ryan Ofee")
    print(result)
"""

import csv
import re
import sys
from pathlib import Path
from typing import Optional

from config import FC_EXPORTS_DIR

# ── Data files ────────────────────────────────────────────────────────────────
PEOPLE_CSV      = FC_EXPORTS_DIR / "fc_people.csv"
STUDENTS_CSV    = FC_EXPORTS_DIR / "fc_students.csv"
TUTORS_CSV      = FC_EXPORTS_DIR / "fc_tutors.csv"
EXT_IDS_CSV     = FC_EXPORTS_DIR / "fc_external_ids.csv"
LINKS_CSV       = FC_EXPORTS_DIR / "fc_parent_student_links.csv"


# ── CSV loaders ───────────────────────────────────────────────────────────────

def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        print(f"WARNING: {path.name} not found — run generate_fc_ids.py first")
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_all():
    """Load all 5 CSVs into memory. Returns a dict of lists."""
    return {
        "people":   _load_csv(PEOPLE_CSV),
        "students": _load_csv(STUDENTS_CSV),
        "tutors":   _load_csv(TUTORS_CSV),
        "ext_ids":  _load_csv(EXT_IDS_CSV),
        "links":    _load_csv(LINKS_CSV),
    }


# ── Index builders ────────────────────────────────────────────────────────────

def _build_indices(data: dict) -> dict:
    """Build lookup dicts for fast resolution."""
    idx = {}

    # people: by fc_person_id
    idx["person_by_id"] = {r["fc_person_id"]: r for r in data["people"]}

    # students: by fc_student_id, mms_student_id, fc_person_id
    idx["student_by_id"]     = {r["fc_student_id"]: r for r in data["students"]}
    idx["student_by_mms"]    = {r["mms_student_id"]: r for r in data["students"] if r["mms_student_id"]}
    idx["student_by_person"] = {r["fc_person_id"]: r for r in data["students"]}

    # tutors: by fc_tutor_id, mms_teacher_id, fc_person_id
    idx["tutor_by_id"]     = {r["fc_tutor_id"]: r for r in data["tutors"]}
    idx["tutor_by_mms"]    = {r["mms_teacher_id"]: r for r in data["tutors"] if r["mms_teacher_id"]}
    idx["tutor_by_person"] = {r["fc_person_id"]: r for r in data["tutors"]}

    # external IDs: by external_value → entity
    idx["ext_by_value"] = {}
    for r in data["ext_ids"]:
        val = r["external_value"].strip()
        if val:
            idx["ext_by_value"].setdefault(val, []).append(r)

    # external IDs: by fc_entity_id → list of ext records
    idx["ext_by_entity"] = {}
    for r in data["ext_ids"]:
        idx["ext_by_entity"].setdefault(r["fc_entity_id"], []).append(r)

    # parent-student links: by parent fc_person_id AND by student fc_student_id
    idx["links_by_parent"]  = {}
    idx["links_by_student"] = {}
    for r in data["links"]:
        idx["links_by_parent"].setdefault(r["fc_parent_person_id"], []).append(r)
        idx["links_by_student"].setdefault(r["fc_student_id"], []).append(r)

    # students grouped by tutor fc_id
    idx["students_by_tutor"] = {}
    for r in data["students"]:
        t = r.get("tutor_fc_id", "")
        if t:
            idx["students_by_tutor"].setdefault(t, []).append(r)

    return idx


# ── Resolve: turn any query into a list of matching fc_person_ids ─────────────

def _resolve_query(query: str, data: dict, idx: dict) -> list[str]:
    """
    Returns a list of fc_person_ids that match the query.
    Supports: FC IDs, MMS IDs, Stripe IDs, Soundslice/Theta values, name search.
    """
    q = query.strip()
    matched_person_ids = []

    # ── Direct FC ID ──────────────────────────────────────────────────────────
    if q.startswith("fc_per_"):
        if q in idx["person_by_id"]:
            return [q]

    if q.startswith("fc_std_"):
        rec = idx["student_by_id"].get(q)
        if rec:
            return [rec["fc_person_id"]]

    if q.startswith("fc_tut_"):
        rec = idx["tutor_by_id"].get(q)
        if rec:
            return [rec["fc_person_id"]]

    # ── MMS ID ────────────────────────────────────────────────────────────────
    if q.startswith("sdt_"):
        rec = idx["student_by_mms"].get(q)
        if rec:
            return [rec["fc_person_id"]]

    if q.startswith("tch_"):
        rec = idx["tutor_by_mms"].get(q)
        if rec:
            return [rec["fc_person_id"]]

    # ── External value (Stripe cus_, sub_, Soundslice, Theta, etc.) ──────────
    ext_hits = idx["ext_by_value"].get(q, [])
    if ext_hits:
        for hit in ext_hits:
            entity_id = hit["fc_entity_id"]
            # entity_id may be fc_std_, fc_per_, fc_tut_
            if entity_id.startswith("fc_std_"):
                rec = idx["student_by_id"].get(entity_id)
                if rec:
                    matched_person_ids.append(rec["fc_person_id"])
            elif entity_id.startswith("fc_per_"):
                matched_person_ids.append(entity_id)
            elif entity_id.startswith("fc_tut_"):
                rec = idx["tutor_by_id"].get(entity_id)
                if rec:
                    matched_person_ids.append(rec["fc_person_id"])
        if matched_person_ids:
            return list(dict.fromkeys(matched_person_ids))  # dedupe, preserve order

    # ── Name search (case-insensitive, partial) ───────────────────────────────
    q_lower = q.lower()
    for person in data["people"]:
        full = f"{person['first_name']} {person['last_name']}".lower()
        first = person["first_name"].lower()
        last  = person["last_name"].lower()
        if q_lower in full or q_lower in first or q_lower in last:
            matched_person_ids.append(person["fc_person_id"])

    return list(dict.fromkeys(matched_person_ids))


# ── Build a rich result record for one fc_person_id ──────────────────────────

def _build_result(person_id: str, data: dict, idx: dict) -> dict:
    """Assemble everything known about one person."""
    result = {}

    # ── Person ────────────────────────────────────────────────────────────────
    person = idx["person_by_id"].get(person_id, {})
    result["fc_person_id"] = person_id
    result["first_name"]   = person.get("first_name", "")
    result["last_name"]    = person.get("last_name", "")
    result["full_name"]    = f"{result['first_name']} {result['last_name']}".strip()
    result["email"]        = person.get("email", "")
    result["roles"]        = person.get("roles", "").split(",") if person.get("roles") else []

    # ── Student record ────────────────────────────────────────────────────────
    student = idx["student_by_person"].get(person_id)
    if student:
        result["fc_student_id"]   = student["fc_student_id"]
        result["mms_student_id"]  = student["mms_student_id"]
        result["instrument"]      = student["instrument"]
        result["tutor_name"]      = student["tutor_name"]
        result["tutor_fc_id"]     = student["tutor_fc_id"]
        result["soundslice_url"]  = student["soundslice_url"]
        result["theta_username"]  = student["theta_username"]
        result["friendly_url"]    = student["friendly_url_slug"]
        result["lesson_length"]   = student.get("lesson_length", "")
        result["status"]          = student["status"]
        result["is_adult"]        = student["is_adult"] == "TRUE"
        result["in_registry"]     = student["in_registry"] == "TRUE"
        result["in_sheets"]       = student["in_sheets"] == "TRUE"
    else:
        result["fc_student_id"] = None

    # ── Tutor record ──────────────────────────────────────────────────────────
    tutor = idx["tutor_by_person"].get(person_id)
    if tutor:
        result["fc_tutor_id"]     = tutor["fc_tutor_id"]
        result["mms_teacher_id"]  = tutor["mms_teacher_id"]
        result["tutor_short"]     = tutor["short_name"]
        result["instruments"]     = tutor["instruments"]
        result["active_tutor"]    = tutor["active"] == "TRUE"
        # Their students
        result["students"] = [
            {
                "fc_student_id": s["fc_student_id"],
                "name": f"{s['first_name']} {s['last_name']}",
                "instrument": s["instrument"],
                "mms_student_id": s["mms_student_id"],
            }
            for s in idx["students_by_tutor"].get(tutor["fc_tutor_id"], [])
        ]
    else:
        result["fc_tutor_id"] = None

    # ── External IDs ──────────────────────────────────────────────────────────
    ext_ids = []
    # Collect from fc_person_id and fc_student_id and fc_tutor_id
    for eid in [person_id,
                result.get("fc_student_id"),
                result.get("fc_tutor_id")]:
        if eid:
            for rec in idx["ext_by_entity"].get(eid, []):
                ext_ids.append({
                    "system":  rec["external_system"],
                    "key":     rec["external_key"],
                    "value":   rec["external_value"],
                })
    result["external_ids"] = ext_ids

    # Build quick-access shortcuts from external IDs
    for ext in ext_ids:
        if ext["system"] == "stripe" and ext["key"] == "customer_id":
            result["stripe_customer_id"] = ext["value"]
        if ext["system"] == "stripe" and ext["key"] == "subscription_id":
            result["stripe_subscription_id"] = ext["value"]

    # ── Parent ────────────────────────────────────────────────────────────────
    if result.get("fc_student_id") and not result.get("is_adult"):
        parent_links = idx["links_by_student"].get(result["fc_student_id"], [])
        parents = []
        for lnk in parent_links:
            par_person = idx["person_by_id"].get(lnk["fc_parent_person_id"], {})
            parents.append({
                "fc_person_id": lnk["fc_parent_person_id"],
                "name": f"{par_person.get('first_name','')} {par_person.get('last_name','')}".strip(),
                "email": par_person.get("email", ""),
            })
        result["parents"] = parents
    else:
        result["parents"] = []

    # ── Children (if this person is a parent) ────────────────────────────────
    child_links = idx["links_by_parent"].get(person_id, [])
    if child_links:
        children = []
        for lnk in child_links:
            child_std = idx["student_by_id"].get(lnk["fc_student_id"], {})
            children.append({
                "fc_student_id": lnk["fc_student_id"],
                "name": f"{child_std.get('first_name','')} {child_std.get('last_name','')}".strip(),
                "mms_student_id": child_std.get("mms_student_id", ""),
            })
        result["children"] = children
    else:
        result["children"] = []

    return result


# ── Public API ────────────────────────────────────────────────────────────────

def lookup(query: str) -> list[dict]:
    """
    Look up one or more entities by name or ID.

    Args:
        query: Any of — full/partial name, fc_per_*, fc_std_*, fc_tut_*,
               sdt_*, tch_*, cus_*, sub_*, or any external value.

    Returns:
        List of result dicts (empty list if nothing found).
        Each dict contains all known fields for that entity.
    """
    data = _load_all()
    idx  = _build_indices(data)
    matched_ids = _resolve_query(query, data, idx)
    return [_build_result(pid, data, idx) for pid in matched_ids]


# ── Pretty-print for CLI ──────────────────────────────────────────────────────

def _print_result(r: dict):
    W = 60
    print("\n" + "═" * W)

    # Header
    print(f"  {r['full_name']}")
    print(f"  Roles: {', '.join(r['roles']) or 'unknown'}")
    print("─" * W)

    # IDs
    print(f"  fc_person_id   {r['fc_person_id']}")
    if r.get("fc_student_id"):
        print(f"  fc_student_id  {r['fc_student_id']}")
    if r.get("fc_tutor_id"):
        print(f"  fc_tutor_id    {r['fc_tutor_id']}")
    if r.get("mms_student_id"):
        print(f"  mms_student_id {r['mms_student_id']}")
    if r.get("mms_teacher_id"):
        print(f"  mms_teacher_id {r['mms_teacher_id']}")
    if r.get("email"):
        print(f"  email          {r['email']}")

    # Student detail
    if r.get("fc_student_id"):
        print("─" * W)
        print(f"  Status         {r.get('status','')}")
        print(f"  Is adult       {'Yes' if r.get('is_adult') else 'No'}")
        print(f"  Instrument     {r.get('instrument') or '—'}")
        if r.get("lesson_length"):
            print(f"  Lesson length  {r['lesson_length']} mins")
        print(f"  Tutor          {r.get('tutor_name') or '—'}  ({r.get('tutor_fc_id','') })")
        if r.get("soundslice_url"):
            print(f"  Soundslice     {r['soundslice_url']}")
        if r.get("theta_username"):
            print(f"  Theta          {r['theta_username']}")
        if r.get("friendly_url"):
            print(f"  Dashboard URL  /{r['friendly_url']}")
        if r.get("stripe_customer_id"):
            print(f"  Stripe cus     {r['stripe_customer_id']}")
        if r.get("stripe_subscription_id"):
            print(f"  Stripe sub     {r['stripe_subscription_id']}")

    # Tutor detail
    if r.get("fc_tutor_id"):
        print("─" * W)
        print(f"  Instruments    {r.get('instruments') or '—'}")
        students = r.get("students", [])
        print(f"  Students ({len(students)}):")
        for s in sorted(students, key=lambda x: x["name"]):
            inst = f"  [{s['instrument']}]" if s.get("instrument") else ""
            print(f"    {s['mms_student_id']:<14} {s['name']}{inst}")

    # External IDs
    ext = r.get("external_ids", [])
    if ext:
        print("─" * W)
        print("  External IDs:")
        for e in ext:
            print(f"    {e['system']:<12} {e['key']:<20} {e['value']}")

    # Parents
    if r.get("parents"):
        print("─" * W)
        print("  Parent(s):")
        for p in r["parents"]:
            email_str = f"  <{p['email']}>" if p["email"] else ""
            print(f"    {p['fc_person_id']}  {p['name']}{email_str}")
    elif r.get("fc_student_id") and r.get("is_adult"):
        print("─" * W)
        print("  Parent        n/a (adult student)")

    # Children (if this person is a parent)
    if r.get("children"):
        print("─" * W)
        print("  Children (students):")
        for c in r["children"]:
            print(f"    {c['fc_student_id']}  {c['name']}  ({c['mms_student_id']})")

    print("═" * W)


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lookup.py <name or ID>")
        print("       python3 lookup.py \"Ryan Ofee\"")
        print("       python3 lookup.py sdt_2grxJL")
        print("       python3 lookup.py cus_R7DL79Smc0cwBE")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = lookup(query)

    if not results:
        print(f"\nNo results found for: {query!r}")
        sys.exit(0)

    print(f"\nFound {len(results)} result(s) for: {query!r}")
    for r in results:
        _print_result(r)
