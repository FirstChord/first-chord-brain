"""
FC Identity Layer Audit — Cross-Reference Script
=================================================
Compares the dashboard students-registry.js (194 students, keyed by MMS ID)
against the Google Sheets student roster (Brain + Payment Pause shared source).

Reports:
  - Students in registry but NOT in Sheets
  - Students in Sheets but NOT in registry
  - Students in Sheets with blank MMS ID
  - Students in both (matched by MMS ID)
  - Tutor name mismatches between registry and Sheets
  - Summary counts

Usage:
    python3 audit_cross_reference.py
"""

import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths (from shared config) ────────────────────────────────────────────────
from config import REGISTRY_PATH

# ── 1. Parse students-registry.js ─────────────────────────────────────────────

def parse_registry(path: Path) -> dict:
    """
    Extract all student records from the JS registry.
    Returns: { mms_id: { firstName, lastName, tutor, instrument, friendlyUrl, ... } }
    """
    text = path.read_text(encoding="utf-8")

    # Match each top-level key block: 'sdt_XXXXX': { ... }
    # We'll use a simple approach: find all sdt_ keys, then extract the block after each
    students = {}

    # Split on student ID keys
    pattern = re.compile(
        r"'(sdt_[A-Za-z0-9]+)'\s*:\s*\{([^}]+)\}",
        re.DOTALL
    )

    for match in pattern.finditer(text):
        mms_id = match.group(1)
        block = match.group(2)

        # Extract individual fields
        def get_field(field_name):
            m = re.search(rf"(?:^|\n)\s*{field_name}\s*:\s*'([^']*)'", block)
            return m.group(1) if m else None

        students[mms_id] = {
            "firstName":   get_field("firstName"),
            "lastName":    get_field("lastName"),
            "friendlyUrl": get_field("friendlyUrl"),
            "tutor":       get_field("tutor"),
            "instrument":  get_field("instrument"),
            "thetaUsername": get_field("thetaUsername"),
            "soundsliceUrl": get_field("soundsliceUrl"),
        }

    return students


# ── 2. Fetch Google Sheets student roster ──────────────────────────────────────

# Apps Script URL — same endpoint used by Payment Pause PWA, no auth required
APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbyVicLCz07cnJ0iTF60-2KlBJ4UaCXUvih6wLwVKzRvHRAf_BXeQLX-vWjR030tMp0RIA/exec"
)

def fetch_sheets_students() -> list[dict]:
    """
    Fetch students from the Google Apps Script web endpoint.
    This is the same URL used by Payment Pause PWA — no OAuth needed.
    Returns list of student dicts with keys like:
      student_forename, student_surname, email, tutor, mms_id, etc.
    """
    import urllib.request
    import json

    print(f"Fetching students from Apps Script endpoint...")
    try:
        req = urllib.request.Request(
            APPS_SCRIPT_URL,
            headers={"User-Agent": "FC-Audit/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        if isinstance(data, dict) and "students" in data:
            rows = data["students"]
        elif isinstance(data, list):
            rows = data
        else:
            print(f"  Unexpected response format: {type(data)}")
            print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'n/a'}")
            sys.exit(1)

        print(f"  ✓ Fetched {len(rows)} rows from Google Sheets (via Apps Script)")
        return rows
    except Exception as e:
        print(f"ERROR fetching from Apps Script: {e}")
        print("  If this fails, the Apps Script may need to be redeployed as a public web app.")
        sys.exit(1)


# ── 3. Normalise Sheets row keys ───────────────────────────────────────────────

def normalise_sheets_row(row: dict) -> dict:
    """
    Normalise column names from Sheets (case-insensitive, strip spaces).
    Expected columns: Tutor Name, Student Surname, Student Forename, Email,
                      MMS ID, Theta Username, Soundslice, Instrument,
                      Parent Surname, Parent Forename
    """
    normalised = {}
    for k, v in row.items():
        clean_key = k.strip().lower().replace(" ", "_")
        normalised[clean_key] = str(v).strip() if v else ""
    return normalised


# ── 4. Run cross-reference ─────────────────────────────────────────────────────

def run_audit():
    print("\n" + "="*60)
    print("  FC IDENTITY LAYER — CROSS-REFERENCE AUDIT")
    print("="*60 + "\n")

    # --- Load registry ---
    print(f"Loading dashboard registry from:\n  {REGISTRY_PATH}\n")
    registry = parse_registry(REGISTRY_PATH)
    print(f"  ✓ Parsed {len(registry)} students from registry\n")

    # --- Load Sheets ---
    raw_rows = fetch_sheets_students()
    sheets_rows = [normalise_sheets_row(r) for r in raw_rows]
    print()

    # --- Build lookup maps ---
    # Sheets indexed by MMS ID (column E = 'mms_id')
    sheets_by_mms = {}
    sheets_no_mms = []
    sheets_mms_key = None

    # Detect the MMS ID column name
    if sheets_rows:
        sample = sheets_rows[0]
        for key in sample:
            if "mms" in key:
                sheets_mms_key = key
                break

    if not sheets_mms_key:
        print("WARNING: Could not find an MMS ID column in Sheets.")
        print("         Available columns:", list(sheets_rows[0].keys()) if sheets_rows else "none")
        sheets_mms_key = "mms_id"  # assume

    print(f"  Sheets MMS ID column detected as: '{sheets_mms_key}'\n")

    for row in sheets_rows:
        mms_id = row.get(sheets_mms_key, "").strip()
        if mms_id and mms_id.startswith("sdt_"):
            sheets_by_mms[mms_id] = row
        else:
            sheets_no_mms.append(row)

    # --- Cross-reference ---
    registry_ids   = set(registry.keys())
    sheets_ids     = set(sheets_by_mms.keys())

    in_both               = registry_ids & sheets_ids
    in_registry_only      = registry_ids - sheets_ids
    in_sheets_only        = sheets_ids - registry_ids

    # --- Tutor name mismatches (for students in both) ---
    mismatches = []
    for mms_id in in_both:
        reg_tutor    = (registry[mms_id].get("tutor") or "").strip()
        sheets_tutor = (sheets_by_mms[mms_id].get("tutor_name", "") or
                        sheets_by_mms[mms_id].get("tutor", "")).strip().title()
        if reg_tutor and sheets_tutor and reg_tutor.lower() != sheets_tutor.lower():
            mismatches.append({
                "mms_id":       mms_id,
                "name":         f"{registry[mms_id]['firstName']} {registry[mms_id]['lastName']}",
                "registry_tutor": reg_tutor,
                "sheets_tutor":   sheets_tutor,
            })

    # ── Print Results ──────────────────────────────────────────────────────────

    print("="*60)
    print("  SUMMARY")
    print("="*60)
    print(f"  Dashboard registry students : {len(registry_ids)}")
    print(f"  Google Sheets students      : {len(sheets_rows)}")
    print(f"    - With MMS ID             : {len(sheets_by_mms)}")
    print(f"    - Without MMS ID          : {len(sheets_no_mms)}")
    print(f"  Matched (in both)           : {len(in_both)}")
    print(f"  In registry ONLY            : {len(in_registry_only)}")
    print(f"  In Sheets ONLY              : {len(in_sheets_only)}")
    print(f"  Tutor name mismatches       : {len(mismatches)}")
    print()

    # --- Students in registry only (not in Sheets) ---
    if in_registry_only:
        print("="*60)
        print(f"  STUDENTS IN REGISTRY ONLY ({len(in_registry_only)})")
        print("  (in dashboard but no matching MMS ID in Google Sheets)")
        print("="*60)
        for mms_id in sorted(in_registry_only):
            s = registry[mms_id]
            print(f"  {mms_id}  {s['firstName']} {s['lastName']}  [tutor: {s['tutor']}]")
        print()

    # --- Students in Sheets only (not in registry) ---
    if in_sheets_only:
        print("="*60)
        print(f"  STUDENTS IN SHEETS ONLY ({len(in_sheets_only)})")
        print("  (in Google Sheets but not in dashboard registry)")
        print("="*60)
        for mms_id in sorted(in_sheets_only):
            row = sheets_by_mms[mms_id]
            fname = row.get("student_forename", row.get("forename", "?"))
            lname = row.get("student_surname", row.get("surname", "?"))
            tutor = row.get("tutor_name", row.get("tutor", "?"))
            print(f"  {mms_id}  {fname} {lname}  [tutor: {tutor}]")
        print()

    # --- Students in Sheets with no MMS ID ---
    if sheets_no_mms:
        print("="*60)
        print(f"  SHEETS ROWS WITH NO MMS ID ({len(sheets_no_mms)})")
        print("  (onboarded but MMS ID not yet filled in)")
        print("="*60)
        for row in sheets_no_mms:
            fname = row.get("student_forename", row.get("forename", "?"))
            lname = row.get("student_surname", row.get("surname", "?"))
            tutor = row.get("tutor_name", row.get("tutor", "?"))
            email = row.get("email", "?")
            print(f"  {fname} {lname}  [tutor: {tutor}]  [{email}]")
        print()

    # --- Tutor mismatches ---
    if mismatches:
        print("="*60)
        print(f"  TUTOR NAME MISMATCHES ({len(mismatches)})")
        print("  (registry and Sheets disagree on tutor assignment)")
        print("="*60)
        for m in mismatches:
            print(f"  {m['mms_id']}  {m['name']}")
            print(f"    Registry: {m['registry_tutor']}  vs  Sheets: {m['sheets_tutor']}")
        print()

    # --- Tutor distribution from registry ---
    print("="*60)
    print("  TUTOR DISTRIBUTION (from registry)")
    print("="*60)
    tutor_counts = {}
    for s in registry.values():
        t = s.get("tutor") or "Unknown"
        tutor_counts[t] = tutor_counts.get(t, 0) + 1
    for tutor, count in sorted(tutor_counts.items(), key=lambda x: -x[1]):
        print(f"  {tutor:<15} {count} students")
    print()

    print("="*60)
    print("  AUDIT COMPLETE")
    print("="*60)

    # Return structured results for further use
    return {
        "registry":           registry,
        "sheets_by_mms":      sheets_by_mms,
        "sheets_no_mms":      sheets_no_mms,
        "in_both":            in_both,
        "in_registry_only":   in_registry_only,
        "in_sheets_only":     in_sheets_only,
        "mismatches":         mismatches,
    }


if __name__ == "__main__":
    run_audit()
