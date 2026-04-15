"""
Google Sheets Client
Handles adding students to the First Chord Database (Students tab).

Auth: uses ~/token_musiclessons.json refresh token — no browser needed.
Columns: detected from the actual header row, so order changes in Sheets
         won't break writes.
"""

import json
import os
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

load_dotenv()

TOKEN_FILE = Path.home() / "token_musiclessons.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _normalise_header(h: str) -> str:
    """
    Normalise a column header for flexible matching.
    Strips, lowercases, and removes spaces/underscores.
    e.g. 'Student Surname' → 'studentsurname'
         'mms_id'          → 'mmsid'
    """
    return h.strip().lower().replace(" ", "").replace("_", "")


def _get_creds():
    token = json.loads(TOKEN_FILE.read_text())
    creds = Credentials(
        token=None,
        refresh_token=token["refresh_token"],
        client_id=token["client_id"],
        client_secret=token["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


class SheetsClient:
    def __init__(self):
        self.spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
        self._gc = None
        self._spreadsheet = None

    def _connect(self):
        if self._gc is None:
            if not TOKEN_FILE.exists():
                raise FileNotFoundError(f"Token file not found: {TOKEN_FILE}")
            self._gc = gspread.authorize(_get_creds())
            self._spreadsheet = self._gc.open_by_key(self.spreadsheet_id)

    def add_student(self, student_data: dict) -> int | None:
        """
        Append a new student row to the Students tab.

        Reads the header row first so it writes to the correct columns
        regardless of sheet column order. Unknown columns are left blank.

        student_data keys used:
            student_surname, student_forename, tutor_short (or tutor),
            parent_surname, parent_forename, parent_email,
            mms_id, theta_username, soundslice_url, instrument,
            fc_student_id

        Stripe fields (stripe_customer_id, stripe_subscription_id) are
        intentionally left blank — Payment Pause fills those in later.

        Returns: 1-indexed row number of the new row, or None on error.
        """
        try:
            self._connect()
            ws = self._spreadsheet.worksheet("Students")

            # ── Read header row and build column map ─────────────────────────
            headers = ws.row_values(1)
            col_map = {_normalise_header(h): i for i, h in enumerate(headers)}

            # ── Build values list (one entry per column) ──────────────────────
            values = [""] * len(headers)

            def put(col_key, value):
                """Write value to the column matching col_key (normalised)."""
                idx = col_map.get(_normalise_header(col_key))
                if idx is not None:
                    values[idx] = value

            # Core student fields — try both possible header spellings
            put("Student Surname",  student_data.get("student_surname", ""))
            put("Student forename", student_data.get("student_forename", ""))
            put("Tutor",            student_data.get("tutor_short") or student_data.get("tutor", ""))
            put("Parent surname",   student_data.get("parent_surname", ""))
            put("Parent forename",  student_data.get("parent_forename", ""))
            put("Email",            student_data.get("parent_email", ""))
            put("mms_id",           student_data.get("mms_id", ""))

            # Extended fields (if columns exist in the sheet)
            put("Theta Username",   student_data.get("theta_username", ""))
            put("Theta",            student_data.get("theta_username", ""))  # alt header
            put("Soundslice",       student_data.get("soundslice_url", ""))
            put("Instrument",       student_data.get("instrument", ""))
            put("FC Student ID",    student_data.get("fc_student_id", ""))
            put("Lesson length",    student_data.get("lesson_length", ""))

            # Stripe fields intentionally blank — filled later by Payment Pause

            # ── Append row ───────────────────────────────────────────────────
            ws.append_row(values, value_input_option="RAW")
            return len(ws.get_all_values())  # row number of newly added row

        except Exception as e:
            print(f"SheetsClient.add_student error: {e}")
            return None

    def update_mms_id(self, row_number: int, mms_id: str) -> bool:
        """
        Write an MMS student ID to an existing row.
        Called after add_student() when the MMS ID becomes known.

        row_number: 1-indexed row number returned by add_student()
        mms_id:     e.g. 'sdt_2grxJL'
        """
        try:
            self._connect()
            ws = self._spreadsheet.worksheet("Students")
            headers = ws.row_values(1)
            col_map = {_normalise_header(h): i for i, h in enumerate(headers)}
            idx = col_map.get("mmsid")
            if idx is None:
                print("  update_mms_id: could not find mms_id column")
                return False
            col_letter = gspread.utils.rowcol_to_a1(row_number, idx + 1)
            ws.update_acell(col_letter, mms_id)
            return True
        except Exception as e:
            print(f"SheetsClient.update_mms_id error: {e}")
            return False
