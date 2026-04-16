#!/usr/bin/env python3
"""
Backfill Contact Number column in Google Sheets Students tab.

Reads all rows that have an mms_id but an empty Contact Number,
fetches the telephone from MMS for each one, and writes it back.

Usage:
    cd ~/Desktop/FirstChord/first-chord-brain
    python3 backfill_contact_numbers.py           # normal run
    python3 backfill_contact_numbers.py --debug   # print raw MMS response for first student and stop
"""

import json
import os
import sys
import time
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from rich.console import Console

from src.mms_client import MMSClient

load_dotenv()

console = Console()

TOKEN_FILE = Path.home() / "token_musiclessons.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


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


def _norm(h: str) -> str:
    return h.strip().lower().replace(" ", "").replace("_", "")


def main():
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
    if not spreadsheet_id:
        console.print("[red]✗ GOOGLE_SPREADSHEET_ID not set in .env[/red]")
        return

    console.print("[bold cyan]Connecting to Google Sheets...[/bold cyan]")
    gc = gspread.authorize(_get_creds())
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet("Students")

    all_values = ws.get_all_values()
    headers = all_values[0] if all_values else []
    col_map = {_norm(h): i for i, h in enumerate(headers)}

    mms_col    = col_map.get("mmsid")
    phone_col  = col_map.get("contactnumber")
    name_f_col = col_map.get("studentforename")
    name_s_col = col_map.get("studentsurname")

    if mms_col is None:
        console.print("[red]✗ Could not find mms_id column[/red]")
        return
    if phone_col is None:
        console.print("[red]✗ Could not find 'Contact Number' column — make sure the header is added to the Students tab[/red]")
        return

    # ── Collect rows that need filling ──────────────────────────────────────
    to_fill = []
    for row_idx, row in enumerate(all_values[1:], start=2):
        def cell(col):
            return row[col].strip() if col is not None and len(row) > col else ""

        mms_id = cell(mms_col)
        phone  = cell(phone_col)

        if mms_id.startswith("sdt_") and not phone:
            to_fill.append({
                "row":    row_idx,
                "mms_id": mms_id,
                "name":   f"{cell(name_f_col)} {cell(name_s_col)}".strip(),
            })

    console.print(f"\n[bold]{len(to_fill)} students[/bold] have an MMS ID but no contact number\n")

    if not to_fill:
        console.print("[green]Nothing to backfill — all done![/green]")
        return

    mms    = MMSClient()

    # ── Debug mode: dump raw MMS response for first student and stop ────────
    if "--debug" in sys.argv:
        first = to_fill[0]
        console.print(f"\n[bold yellow]DEBUG MODE — raw MMS response for {first['name']} ({first['mms_id']})[/bold yellow]\n")
        import requests as req
        from dotenv import load_dotenv
        load_dotenv()
        r = req.get(
            f"https://api.mymusicstaff.com/v1/students/{first['mms_id']}",
            params={"fields": "Family"},
            headers={
                "Authorization": f"Bearer {os.getenv('MMS_BEARER_TOKEN')}",
                "Accept": "application/json, text/plain, */*",
                "x-schoolbox-version": "main",
            },
        )
        console.print(f"Status: {r.status_code}")
        console.print(json.dumps(r.json(), indent=2, default=str))
        return

    filled  = []
    missing = []
    errors  = []

    console.print("[dim]Fetching from MMS (~1 request/sec)...[/dim]\n")

    for i, student in enumerate(to_fill, 1):
        label = f"[{i}/{len(to_fill)}] {student['name']} ({student['mms_id']})"
        console.print(f"  {label}...", end=" ")

        try:
            details = mms.get_student_details(student["mms_id"])

            if not details.get("success"):
                console.print(f"[red]API error: {details.get('error', '?')}[/red]")
                errors.append(student)
                time.sleep(1)
                continue

            # Student's own number first; fall back to parent's for child students
            telephone = details.get("telephone", "").strip()
            if not telephone:
                telephone = details.get("parent_telephone", "").strip()

            if not telephone:
                console.print("[dim]no number in MMS[/dim]")
                missing.append(student)
                time.sleep(1)
                continue

            # Write to the correct cell
            col_letter = gspread.utils.rowcol_to_a1(student["row"], phone_col + 1)
            ws.update_acell(col_letter, telephone)
            console.print(f"[green]✓ {telephone}[/green]")
            filled.append({**student, "telephone": telephone})

        except Exception as e:
            console.print(f"[red]exception: {e}[/red]")
            errors.append(student)

        time.sleep(1)  # stay polite with the MMS API

    # ── Summary ─────────────────────────────────────────────────────────────
    console.print(f"\n{'─' * 50}")
    console.print(f"  [green]✓ Filled:[/green]      {len(filled)}")
    console.print(f"  [dim]○ No number:[/dim]   {len(missing)}")
    console.print(f"  [red]✗ Errors:[/red]      {len(errors)}")
    console.print(f"{'─' * 50}\n")

    if errors:
        console.print("[yellow]The following students had API errors — check manually:[/yellow]")
        for s in errors:
            console.print(f"  {s['mms_id']}  {s['name']}")


if __name__ == "__main__":
    main()
