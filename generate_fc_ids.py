"""
FC Identity Layer — ID Generation Script
=========================================
Generates canonical FC IDs for all students, tutors, and people.
Outputs 5 CSV files ready to import as new Google Sheets tabs:
  - fc_people.csv
  - fc_students.csv
  - fc_tutors.csv
  - fc_parent_student_links.csv
  - fc_external_ids.csv

FC ID formats:
  fc_per_XXXXXXXX  — person (student, parent, tutor, admin)
  fc_std_XXXXXXXX  — student record
  fc_tut_XXXXXXXX  — tutor record

IDs are deterministic: same MMS ID always generates same FC ID.
This means this script can be re-run safely without creating duplicates.

Usage:
    python3 generate_fc_ids.py
"""

import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import date

# ── Paths (from shared config — move FirstChord/ freely without editing here) ──
from config import REGISTRY_PATH, FC_EXPORTS_DIR as OUTPUT_DIR, TOKEN_FILE
ENV_FILE = Path(__file__).parent / ".env"
TODAY         = date.today().isoformat()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load .env for GOOGLE_SPREADSHEET_ID
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ── Apps Script URL ────────────────────────────────────────────────────────────
APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbyVicLCz07cnJ0iTF60-2KlBJ4UaCXUvih6wLwVKzRvHRAf_BXeQLX-vWjR030tMp0RIA/exec"
)

# ── Tutor master list (from Brain's mms_client.py — single source) ──────────────
TUTORS = [
    {"short_name": "Arion",    "full_name": "Arion Xenos",             "mms_teacher_id": "tch_zplpJw", "instruments": ["guitar", "piano"]},
    {"short_name": "Dean",     "full_name": "Dean Louden",             "mms_teacher_id": "tch_zV9TJN", "instruments": ["guitar", "bass"]},
    {"short_name": "Eléna",    "full_name": "Eléna Esposito",          "mms_teacher_id": "tch_zpy4J9", "instruments": ["piano"]},
    {"short_name": "Fennella", "full_name": "Fennella McCallum",       "mms_teacher_id": "tch_C2bJ9",  "instruments": ["singing", "piano"]},
    {"short_name": "Finn",     "full_name": "Finn Le Marinel",         "mms_teacher_id": "tch_QhxJJ",  "instruments": ["guitar", "bass", "ukulele"]},
    {"short_name": "Kenny",    "full_name": "Kenny Bates",             "mms_teacher_id": "tch_zsyfJr", "instruments": ["guitar"]},
    {"short_name": "Kim",      "full_name": "Kim Grant",               "mms_teacher_id": "tch_zVg1Js", "instruments": ["guitar"]},
    {"short_name": "Patrick",  "full_name": "Patrick Shand",           "mms_teacher_id": "tch_zw9SJ3", "instruments": ["guitar", "piano"]},
    {"short_name": "Robbie",   "full_name": "Robbie Tranter",          "mms_teacher_id": "tch_zV9hJ2", "instruments": ["guitar", "bass"]},
    {"short_name": "Stef",     "full_name": "Stef McGlinchey",         "mms_teacher_id": "tch_z5YmJX", "instruments": ["guitar"]},
    {"short_name": "Tom",      "full_name": "Tom Walters",             "mms_teacher_id": "tch_mYJJR",  "instruments": ["guitar", "bass"]},
    {"short_name": "Ines",     "full_name": "Ines Alban Zapata Peréz", "mms_teacher_id": "tch_zHJlJx", "instruments": ["piano"]},
    {"short_name": "David",    "full_name": "David Husz",              "mms_teacher_id": "tch_z2j2Jf", "instruments": ["guitar", "piano"]},
    {"short_name": "Scott",    "full_name": "Scott Brice",             "mms_teacher_id": "tch_zMWrJR", "instruments": ["guitar"]},
    {"short_name": "Calum",    "full_name": "Calum Steel",             "mms_teacher_id": "tch_zMX5Jc", "instruments": ["guitar"]},
    {"short_name": "Chloe",    "full_name": "Chloe Mak",               "mms_teacher_id": "tch_zQbNJk", "instruments": ["guitar", "piano"]},
]

# ── ID generation ──────────────────────────────────────────────────────────────

def make_fc_id(prefix: str, seed: str) -> str:
    """
    Generate a deterministic FC ID from a seed string.
    Same seed always produces same ID.
    Format: fc_{prefix}_{8 hex chars}
    """
    h = hashlib.sha256(seed.encode()).hexdigest()[:8]
    return f"fc_{prefix}_{h}"


def make_tutor_short_to_id_map(tutors: list) -> dict:
    """Build a map from short name (lowercase) to fc_tut_id."""
    result = {}
    for t in tutors:
        fc_id = make_fc_id("tut", t["mms_teacher_id"])
        result[t["short_name"].lower()] = fc_id
        result[t["full_name"].lower()] = fc_id
        # Also handle first-name only
        result[t["full_name"].split()[0].lower()] = fc_id
    return result


# ── Registry parser ────────────────────────────────────────────────────────────

def parse_registry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    students = {}
    pattern = re.compile(r"'(sdt_[A-Za-z0-9]+)'\s*:\s*\{([^}]+)\}", re.DOTALL)
    for match in pattern.finditer(text):
        mms_id = match.group(1)
        block  = match.group(2)
        def get_field(field_name):
            m = re.search(rf"(?:^|\n)\s*{field_name}\s*:\s*'([^']*)'", block)
            return m.group(1) if m else None
        students[mms_id] = {
            "firstName":     get_field("firstName"),
            "lastName":      get_field("lastName"),
            "friendlyUrl":   get_field("friendlyUrl"),
            "tutor":         get_field("tutor"),
            "instrument":    get_field("instrument"),
            "thetaUsername": get_field("thetaUsername"),
            "soundsliceUrl": get_field("soundsliceUrl"),
        }
    return students


# ── Sheets fetcher ─────────────────────────────────────────────────────────────

def fetch_sheets_students() -> list[dict]:
    import gspread, json, time
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    CACHE = Path("/tmp/fc_sheets_cache_v2.json")
    # Use cached data if fresh (within 10 min)
    if CACHE.exists() and (time.time() - CACHE.stat().st_mtime) < 600:
        rows = json.loads(CACHE.read_text())
        print(f"  ✓ Loaded {len(rows)} rows from cache")
        return rows

    print(f"  Connecting to Google Sheets...")
    token = json.loads(TOKEN_FILE.read_text())
    creds = Credentials(
        token=None,
        refresh_token=token["refresh_token"],
        client_id=token["client_id"],
        client_secret=token["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    creds.refresh(Request())
    gc = gspread.authorize(creds)
    spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID", "")
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet("Students")
    rows = ws.get_all_records()  # list of dicts, keys are exact header names
    CACHE.write_text(json.dumps(rows))
    print(f"  ✓ Fetched {len(rows)} rows from Google Sheets (direct)")
    return rows

def normalise(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        out[k.strip().lower().replace(" ", "_")] = str(v).strip() if v else ""
    return out

def is_header_row(row: dict) -> bool:
    surname  = row.get("student_surname", "")
    forename = row.get("student_forename", "")
    email    = row.get("email", "")
    mms      = row.get("mms_id", "")
    return (not forename and not email and not mms and surname and
            surname == surname.upper() and len(surname) > 2)


# ── Main generation ────────────────────────────────────────────────────────────

def generate():
    print("\n" + "="*60)
    print("  FC IDENTITY LAYER — ID GENERATION")
    print("="*60 + "\n")

    # ── Load data ──
    print("Loading registry...")
    registry = parse_registry(REGISTRY_PATH)
    print(f"  ✓ {len(registry)} students in registry\n")

    print("Fetching Google Sheets students...")
    raw_rows = fetch_sheets_students()
    all_rows = [normalise(r) for r in raw_rows]
    real_rows = [r for r in all_rows if not is_header_row(r)]
    sheets_by_mms = {r["mms_id"]: r for r in real_rows if r.get("mms_id","").startswith("sdt_")}
    print(f"  ✓ {len(real_rows)} real student rows from Sheets")
    print(f"  ✓ {len(sheets_by_mms)} with MMS IDs\n")

    # ── Build tutor map ──
    tutor_short_to_fc = make_tutor_short_to_id_map(TUTORS)

    # ── Merge student universe ──
    # Union of registry + sheets (by MMS ID)
    all_mms_ids = set(registry.keys()) | set(sheets_by_mms.keys())
    print(f"Total unique student MMS IDs (union): {len(all_mms_ids)}\n")

    # ── OUTPUT 1: FC_Tutors ────────────────────────────────────────────────────
    fc_tutors = []
    for t in TUTORS:
        fc_tut_id = make_fc_id("tut", t["mms_teacher_id"])
        fc_per_id = make_fc_id("per", t["mms_teacher_id"])
        first = t["full_name"].split()[0]
        last  = " ".join(t["full_name"].split()[1:]) if len(t["full_name"].split()) > 1 else ""
        fc_tutors.append({
            "fc_tutor_id":    fc_tut_id,
            "fc_person_id":   fc_per_id,
            "mms_teacher_id": t["mms_teacher_id"],
            "short_name":     t["short_name"],
            "full_name":      t["full_name"],
            "first_name":     first,
            "last_name":      last,
            "instruments":    ",".join(t["instruments"]),
            "active":         "TRUE",
            "created_at":     TODAY,
        })

    write_csv("fc_tutors.csv", fc_tutors, [
        "fc_tutor_id","fc_person_id","mms_teacher_id","short_name","full_name",
        "first_name","last_name","instruments","active","created_at"
    ])
    print(f"  ✓ fc_tutors.csv — {len(fc_tutors)} tutors")

    # ── OUTPUT 2: FC_People (tutors) + FC_People (students) ───────────────────
    fc_people = []

    # Tutors as people
    for t in fc_tutors:
        fc_people.append({
            "fc_person_id": t["fc_person_id"],
            "first_name":   t["first_name"],
            "last_name":    t["last_name"],
            "email":        "",
            "roles":        "tutor",
            "created_at":   TODAY,
            "notes":        f"Tutor: {t['full_name']}",
        })

    # ── OUTPUT 3: FC_Students + FC_People (students) ───────────────────────────
    fc_students = []
    fc_external_ids = []
    fc_parents = {}   # email → fc_person record (deduplicated)
    fc_parent_student_links = []

    # Flags for review
    review_flags = []

    for mms_id in sorted(all_mms_ids):
        reg  = registry.get(mms_id)
        sh   = sheets_by_mms.get(mms_id)

        # ── Resolve name ──
        first = last = tutor_short = instrument = soundslice_url = theta_username = ""

        if reg:
            first            = reg.get("firstName") or ""
            last             = reg.get("lastName") or ""
            tutor_short      = reg.get("tutor") or ""
            instrument       = reg.get("instrument") or ""
            soundslice_url   = reg.get("soundsliceUrl") or ""
            theta_username   = reg.get("thetaUsername") or ""

        if sh:
            if not first: first = sh.get("student_forename","")
            if not last:  last  = sh.get("student_surname","")

        # ── Adult detection (done early so it feeds into student record) ──
        if sh:
            par_fore = sh.get("parent_forename","").strip()
            par_sur  = sh.get("parent_surname","").strip()
            _adult = (
                bool(first.strip()) and bool(last.strip()) and
                par_fore.lower() == first.strip().lower() and
                par_sur.lower()  == last.strip().lower()
            )
        else:
            _adult = False

        # ── Resolve tutor ──
        tutor_full = ""
        if sh:
            tutor_full = sh.get("tutor","")
        elif tutor_short:
            # Map short name to full name from TUTORS list
            for t in TUTORS:
                if t["short_name"].lower() == tutor_short.lower():
                    tutor_full = t["full_name"]
                    break

        tutor_fc_id = tutor_short_to_fc.get(tutor_full.split()[0].lower() if tutor_full else "")

        # ── Flag: tutor conflict ──
        if reg and sh and tutor_short and tutor_full:
            sheets_first = tutor_full.split()[0].lower()
            if tutor_short.lower() != sheets_first:
                review_flags.append(f"TUTOR CONFLICT  {mms_id}  {first} {last}: "
                                    f"registry={tutor_short} vs sheets={tutor_full}")

        # ── Flag: missing from one side ──
        if not reg:
            review_flags.append(f"SHEETS ONLY     {mms_id}  {first} {last}  [{tutor_full}]")
        if not sh:
            review_flags.append(f"REGISTRY ONLY   {mms_id}  {first} {last}  [{tutor_short}]")

        # ── Generate FC IDs ──
        fc_per_id  = make_fc_id("per", mms_id)
        fc_std_id  = make_fc_id("std", mms_id)
        friendly   = reg.get("friendlyUrl","") if reg else ""

        # Student as person
        fc_people.append({
            "fc_person_id": fc_per_id,
            "first_name":   first,
            "last_name":    last,
            "email":        sh.get("email","") if sh else "",
            "roles":        "student",
            "created_at":   TODAY,
            "notes":        "",
        })

        # Student record
        lesson_length = sh.get("lesson_length", "") if sh else ""
        fc_students.append({
            "fc_student_id":    fc_std_id,
            "fc_person_id":     fc_per_id,
            "mms_student_id":   mms_id,
            "first_name":       first,
            "last_name":        last,
            "instrument":       instrument,
            "tutor_fc_id":      tutor_fc_id or "",
            "tutor_name":       tutor_full,
            "soundslice_url":   soundslice_url,
            "theta_username":   theta_username,
            "friendly_url_slug": friendly,
            "lesson_length":    lesson_length,
            "status":           "active",
            "is_adult":         "TRUE" if _adult else "FALSE",
            "in_registry":      "TRUE" if reg else "FALSE",
            "in_sheets":        "TRUE" if sh else "FALSE",
            "created_at":       TODAY,
        })

        # External IDs
        fc_external_ids.append({
            "fc_entity_id":    fc_std_id,
            "fc_entity_type":  "student",
            "external_system": "mms",
            "external_key":    "student_id",
            "external_value":  mms_id,
            "created_at":      TODAY,
        })

        if sh:
            if sh.get("stripe_customer_id","").startswith("cus_"):
                fc_external_ids.append({
                    "fc_entity_id":    fc_per_id,
                    "fc_entity_type":  "person",
                    "external_system": "stripe",
                    "external_key":    "customer_id",
                    "external_value":  sh["stripe_customer_id"],
                    "created_at":      TODAY,
                })
            if sh.get("stripe_subscription_id","").startswith("sub_"):
                fc_external_ids.append({
                    "fc_entity_id":    fc_std_id,
                    "fc_entity_type":  "student",
                    "external_system": "stripe",
                    "external_key":    "subscription_id",
                    "external_value":  sh["stripe_subscription_id"],
                    "created_at":      TODAY,
                })

        if soundslice_url:
            # Extract course ID from URL
            m = re.search(r"/courses/(\d+)/", soundslice_url)
            if m:
                fc_external_ids.append({
                    "fc_entity_id":    fc_std_id,
                    "fc_entity_type":  "student",
                    "external_system": "soundslice",
                    "external_key":    "course_id",
                    "external_value":  m.group(1),
                    "created_at":      TODAY,
                })

        if theta_username:
            fc_external_ids.append({
                "fc_entity_id":    fc_std_id,
                "fc_entity_type":  "student",
                "external_system": "theta",
                "external_key":    "username",
                "external_value":  theta_username,
                "created_at":      TODAY,
            })

        # ── Parent / guardian link ──
        if sh:
            parent_email   = sh.get("email","")
            parent_fore    = sh.get("parent_forename","")
            parent_surname = sh.get("parent_surname","")

            if not _adult:
                if parent_email and parent_email not in fc_parents:
                    parent_per_id = make_fc_id("per", f"parent:{parent_email}")
                    fc_parents[parent_email] = {
                        "fc_person_id": parent_per_id,
                        "first_name":   parent_fore,
                        "last_name":    parent_surname,
                        "email":        parent_email,
                        "roles":        "parent",
                        "created_at":   TODAY,
                        "notes":        "",
                    }

                if parent_email and parent_email in fc_parents:
                    fc_parent_student_links.append({
                        "id":                   make_fc_id("lnk", f"{parent_email}:{mms_id}"),
                        "fc_parent_person_id":  fc_parents[parent_email]["fc_person_id"],
                        "fc_student_id":        fc_std_id,
                        "relationship":         "parent",
                        "created_at":           TODAY,
                    })

    # ── Pre-MMS students (onboarded but no MMS ID yet) ────────────────────────
    # These use forename:surname:email as seed — same as onboarding.py — so the
    # FC ID is stable and consistent from the moment of onboarding.
    no_mms_rows = [r for r in real_rows if not r.get("mms_id","").startswith("sdt_")]
    pre_mms_count = 0
    for row in no_mms_rows:
        fore  = row.get("student_forename","").strip()
        sur   = row.get("student_surname","").strip()
        email = row.get("email","").strip()
        if not fore or not sur or not email:
            continue  # Not enough data

        seed      = f"{fore.lower()}:{sur.lower()}:{email.lower()}"
        fc_per_id = make_fc_id("per", seed)
        fc_std_id = make_fc_id("std", seed)

        # Skip if already in people list (shouldn't happen but safety check)
        if any(p["fc_person_id"] == fc_per_id for p in fc_people):
            continue

        # Adult detection
        par_fore = row.get("parent_forename","").strip()
        par_sur  = row.get("parent_surname","").strip()
        _adult = (
            bool(fore) and bool(sur) and
            par_fore.lower() == fore.lower() and
            par_sur.lower()  == sur.lower()
        )

        # Best-effort tutor lookup (handles both short uppercase and full name)
        tutor_raw = (row.get("tutor_name","") or row.get("tutor","")).strip()
        tutor_fc_id = (
            tutor_short_to_fc.get(tutor_raw.lower()) or
            tutor_short_to_fc.get(tutor_raw.split()[0].lower() if tutor_raw else "") or
            ""
        )

        instrument = row.get("instrument","").strip()
        soundslice_raw = (row.get("soundslice","") or row.get("soundsliceurl","")).strip()
        if soundslice_raw and not soundslice_raw.startswith("http"):
            soundslice_url = f"https://www.soundslice.com/courses/{soundslice_raw}/"
        else:
            soundslice_url = soundslice_raw
        theta_username = (row.get("theta","") or row.get("theta_username","")).strip()

        # Person
        fc_people.append({
            "fc_person_id": fc_per_id,
            "first_name":   fore,
            "last_name":    sur,
            "email":        email,
            "roles":        "student",
            "created_at":   TODAY,
            "notes":        "pre-MMS: onboarded, MMS ID not yet assigned",
        })

        # Student record
        pre_mms_lesson_length = (row.get("lesson_length","") or row.get("lessonlength","")).strip()
        fc_students.append({
            "fc_student_id":     fc_std_id,
            "fc_person_id":      fc_per_id,
            "mms_student_id":    "",
            "first_name":        fore,
            "last_name":         sur,
            "instrument":        instrument,
            "tutor_fc_id":       tutor_fc_id,
            "tutor_name":        tutor_raw,
            "soundslice_url":    soundslice_url,
            "theta_username":    theta_username,
            "friendly_url_slug": fore.lower(),
            "lesson_length":     pre_mms_lesson_length,
            "status":            "pending",
            "is_adult":          "TRUE" if _adult else "FALSE",
            "in_registry":       "FALSE",
            "in_sheets":         "TRUE",
            "created_at":        TODAY,
        })

        # External IDs
        if theta_username:
            fc_external_ids.append({
                "fc_entity_id":    fc_std_id,
                "fc_entity_type":  "student",
                "external_system": "theta",
                "external_key":    "username",
                "external_value":  theta_username,
                "created_at":      TODAY,
            })
        if soundslice_url:
            m = re.search(r"/courses/(\d+)/", soundslice_url)
            if m:
                fc_external_ids.append({
                    "fc_entity_id":    fc_std_id,
                    "fc_entity_type":  "student",
                    "external_system": "soundslice",
                    "external_key":    "course_id",
                    "external_value":  m.group(1),
                    "created_at":      TODAY,
                })

        # Parent link
        if not _adult and email:
            if email not in fc_parents:
                parent_per_id = make_fc_id("per", f"parent:{email}")
                fc_parents[email] = {
                    "fc_person_id": parent_per_id,
                    "first_name":   par_fore,
                    "last_name":    par_sur,
                    "email":        email,
                    "roles":        "parent",
                    "created_at":   TODAY,
                    "notes":        "",
                }
            fc_parent_student_links.append({
                "id":                  make_fc_id("lnk", f"{email}:{seed}"),
                "fc_parent_person_id": fc_parents[email]["fc_person_id"],
                "fc_student_id":       fc_std_id,
                "relationship":        "parent",
                "created_at":          TODAY,
            })

        pre_mms_count += 1

    if pre_mms_count:
        print(f"  ✓ {pre_mms_count} pre-MMS student(s) included (onboarded, no MMS ID yet)\n")

    # Add tutor external IDs
    for t in TUTORS:
        fc_tut_id = make_fc_id("tut", t["mms_teacher_id"])
        fc_per_id = make_fc_id("per", t["mms_teacher_id"])
        fc_external_ids.append({
            "fc_entity_id":    fc_tut_id,
            "fc_entity_type":  "tutor",
            "external_system": "mms",
            "external_key":    "teacher_id",
            "external_value":  t["mms_teacher_id"],
            "created_at":      TODAY,
        })

    # Add parents to fc_people
    for parent in fc_parents.values():
        fc_people.append(parent)

    # ── Write all CSVs ──
    STUDENTS_FIELDS = [
        "fc_student_id","fc_person_id","mms_student_id","first_name","last_name",
        "instrument","tutor_fc_id","tutor_name","soundslice_url","theta_username",
        "friendly_url_slug","lesson_length","status","is_adult","in_registry","in_sheets","created_at"
    ]
    PEOPLE_FIELDS = ["fc_person_id","first_name","last_name","email","roles","created_at","notes"]
    TUTORS_FIELDS = [
        "fc_tutor_id","fc_person_id","mms_teacher_id","short_name","full_name",
        "first_name","last_name","instruments","active","created_at"
    ]
    LINKS_FIELDS  = ["id","fc_parent_person_id","fc_student_id","relationship","created_at"]
    EXT_FIELDS    = ["fc_entity_id","fc_entity_type","external_system","external_key","external_value","created_at"]
    FLAGS_FIELDS  = ["flag_type","mms_id","student_name","detail","generated_date"]

    write_csv("fc_students.csv",            fc_students,            STUDENTS_FIELDS)
    write_csv("fc_people.csv",              fc_people,              PEOPLE_FIELDS)
    write_csv("fc_external_ids.csv",        fc_external_ids,        EXT_FIELDS)
    write_csv("fc_parent_student_links.csv",fc_parent_student_links,LINKS_FIELDS)
    print(f"  ✓ fc_students.csv — {len(fc_students)} students")
    print(f"  ✓ fc_people.csv — {len(fc_people)} people ({len(fc_tutors)} tutors + {len(fc_students)} students + {len(fc_parents)} unique parents)")
    print(f"  ✓ fc_external_ids.csv — {len(fc_external_ids)} external ID mappings")
    print(f"  ✓ fc_parent_student_links.csv — {len(fc_parent_student_links)} parent-student links")

    # ── Parse review flags into structured rows (for Sheets + admin dashboard) ──
    def _parse_flag(s: str) -> dict:
        for ftype in ("TUTOR CONFLICT", "SHEETS ONLY", "REGISTRY ONLY"):
            if s.startswith(ftype):
                rest = s[len(ftype):].strip()
                parts = rest.split(None, 1)
                mms_id = parts[0] if parts else ""
                body = parts[1].strip() if len(parts) > 1 else ""
                if ": " in body:
                    name, detail = body.split(": ", 1)
                elif "  [" in body:
                    name, detail = body.split("  [", 1)
                    detail = detail.rstrip("]")
                else:
                    name, detail = body, ""
                return {"flag_type": ftype, "mms_id": mms_id,
                        "student_name": name.strip(), "detail": detail.strip(),
                        "generated_date": TODAY}
        return {"flag_type": "UNKNOWN", "mms_id": "", "student_name": "",
                "detail": s, "generated_date": TODAY}

    fc_review_flags = [_parse_flag(f) for f in review_flags]

    # ── Write directly to Google Sheets ──────────────────────────────────────
    write_to_sheets({
        "FC_Students":             (fc_students,            STUDENTS_FIELDS),
        "FC_People":               (fc_people,              PEOPLE_FIELDS),
        "FC_Tutors":               (fc_tutors,              TUTORS_FIELDS),
        "FC_Parent_Student_Links": (fc_parent_student_links,LINKS_FIELDS),
        "FC_External_IDs":         (fc_external_ids,        EXT_FIELDS),
        "Review_Flags":            (fc_review_flags,        FLAGS_FIELDS),
    })

    # ── Write review flags ──
    flags_path = OUTPUT_DIR / "review_flags.txt"
    with open(flags_path, "w") as f:
        f.write(f"FC Identity Layer — Items Requiring Review\n")
        f.write(f"Generated: {TODAY}\n\n")
        for flag in review_flags:
            f.write(flag + "\n")
    print(f"\n  ✓ review_flags.txt — {len(review_flags)} items need your attention")

    # ── Summary ──
    stripe_count = len([x for x in fc_external_ids if x["external_system"] == "stripe" and x["external_key"] == "customer_id"])
    sub_count    = len([x for x in fc_external_ids if x["external_system"] == "stripe" and x["external_key"] == "subscription_id"])
    ss_count     = len([x for x in fc_external_ids if x["external_system"] == "soundslice"])
    theta_count  = len([x for x in fc_external_ids if x["external_system"] == "theta"])
    mms_count    = len([x for x in fc_external_ids if x["external_system"] == "mms"])

    print(f"\n{'='*60}")
    print(f"  GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Unique students:  {len(fc_students)}")
    print(f"  Tutors:           {len(fc_tutors)}")
    print(f"  Unique parents:   {len(fc_parents)}")
    print(f"  Total people:     {len(fc_people)}")
    print(f"  External ID mappings:")
    print(f"    MMS IDs:            {mms_count}")
    print(f"    Stripe customer:    {stripe_count}")
    print(f"    Stripe sub:         {sub_count}")
    print(f"    Soundslice courses: {ss_count}")
    print(f"    Theta usernames:    {theta_count}")
    print(f"  Review flags:     {len(review_flags)}")
    print(f"\n  Google Sheets tabs updated automatically.")
    print(f"  CSVs also saved to: {OUTPUT_DIR}")


def write_csv(filename: str, rows: list, fields: list):
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ── Sheets writer ───────────────────────────────────────────────────────────────

FC_TABS = [
    "FC_People",
    "FC_Students",
    "FC_Tutors",
    "FC_Parent_Student_Links",
    "FC_External_IDs",
    "Review_Flags",   # structured review flags — readable by admin dashboard via Sheets API
]

def write_to_sheets(tab_data: dict):
    """
    Write all FC identity layer tables directly to Google Sheets.

    tab_data: {tab_name: (rows: list[dict], fields: list[str])}

    Uses token_musiclessons.json for OAuth (refresh token — no browser needed).
    Spreadsheet ID is read from GOOGLE_SPREADSHEET_ID env var / .env file.
    """
    spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID")
    if not spreadsheet_id:
        print("  ✗ GOOGLE_SPREADSHEET_ID not set — skipping Sheets write")
        return False

    if not TOKEN_FILE.exists():
        print(f"  ✗ Token file not found: {TOKEN_FILE} — skipping Sheets write")
        return False

    try:
        import gspread
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
    except ImportError as e:
        print(f"  ✗ Missing library ({e}) — skipping Sheets write")
        return False

    print("\nConnecting to Google Sheets...")
    token = json.loads(TOKEN_FILE.read_text())
    creds = Credentials(
        token=None,
        refresh_token=token["refresh_token"],
        client_id=token["client_id"],
        client_secret=token["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    creds.refresh(Request())
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(spreadsheet_id)
    print(f"  ✓ Opened: {sh.title}")

    # Build map of existing tabs (strip trailing spaces from names)
    existing = {}
    for ws in sh.worksheets():
        existing[ws.title.strip()] = ws

    for tab_name in FC_TABS:
        rows, fields = tab_data[tab_name]

        # Get existing worksheet, fix trailing space if present
        ws = existing.get(tab_name)
        if ws is None:
            # Try with trailing space (artefact from CSV import)
            ws = existing.get(tab_name + " ")
            if ws:
                ws.update_title(tab_name)
                print(f"  ✓ Renamed '{tab_name} ' → '{tab_name}'")

        if ws is None:
            ws = sh.add_worksheet(
                title=tab_name,
                rows=max(len(rows) + 20, 100),
                cols=len(fields) + 2,
            )
            print(f"  + Created tab: {tab_name}")
        else:
            ws.clear()

        # Write header + all data rows in one API call
        header = [fields]
        data   = [[row.get(f, "") for f in fields] for row in rows]
        ws.update(header + data, value_input_option="RAW")
        print(f"  ✓ {tab_name:<30} {len(rows):>4} rows")

    print("  Sheets update complete.\n")
    return True


if __name__ == "__main__":
    generate()
