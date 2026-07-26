# FC Regeneration GitHub Actions Setup

This repo now includes:

- `.github/workflows/regenerate-fc-ids.yml`

It runs `generate_fc_ids.py`:

- manually via `workflow_dispatch`
- automatically every hour

## Why it checks out two repos

`generate_fc_ids.py` reads:

- Google Sheets live student data
- `students-registry.js` from `FirstChord/first-chord-dashbord`

So the workflow checks out:

- `FirstChord/first-chord-brain`
- `FirstChord/first-chord-dashbord`

in a sibling layout that matches `config.py`.

## Required repository secrets

Add these secrets in the `FirstChord/first-chord-brain` GitHub repo:

- `GOOGLE_SPREADSHEET_ID`
- `SHEETS_REFRESH_TOKEN`
- `SHEETS_CLIENT_ID`
- `SHEETS_CLIENT_SECRET`

The dashboard repository is public, so the cross-repository checkout uses the
workflow's built-in `GITHUB_TOKEN`; it does not require a separate long-lived
personal access token. If the dashboard repository becomes private, use a
short-lived GitHub App token or a fine-grained token restricted to that repository
with `Contents: Read`.

## Secret notes

### Sheets OAuth trio

These must match the same working OAuth refresh-token credential set:

- `SHEETS_REFRESH_TOKEN`
- `SHEETS_CLIENT_ID`
- `SHEETS_CLIENT_SECRET`

They are the same values used successfully by the admin dashboard on Railway.

## Current scope

This workflow updates:

- `FC_People`
- `FC_Students`
- `FC_Tutors`
- `FC_Parent_Student_Links`
- `FC_External_IDs`
- `Review_Flags`

It does **not** yet trigger directly from the admin dashboard.

The current automation model is:

1. admin onboarding updates the dashboard/student portal path automatically
2. this workflow keeps the FC identity/review-flags layer fresh on a schedule or manual run

The next improvement, if needed, would be dispatching this workflow from the admin app after onboarding.

## Troubleshooting

### Failure: dashboard checkout reports "Bad credentials"

The public dashboard checkout should not supply a separate token. Confirm the
workflow does not pass a stale `DASHBOARD_REPO_TOKEN`, then re-run it. This
failure occurs before FC regeneration starts and does not indicate a Sheets or
FC identity calculation problem.

### Failure: "the header row in the worksheet contains duplicates: ['']"

Symptom: the scheduled run fails fast (~20s) in `fetch_sheets_students()` with a
`gspread.exceptions.GSpreadException` about duplicate header cells.

Cause: a manual edit to the **Students** sheet left **two or more columns with a
blank header** (e.g. an empty helper column plus an accidentally-emptied column
from header surgery). gspread's `get_all_records()` refuses any duplicate header,
including blank ones.

Fix (already applied): `fetch_sheets_students()` no longer uses
`get_all_records()`. It reads raw values (`get_all_values()`) and builds the
records itself — **skipping blank-header columns and keeping the first value for
any duplicate header**. This mirrors how the admin dashboard reads the same
sheet, so unlabelled/duplicate columns no longer crash regeneration. Nothing
writes to the Students header row, so dropping blank columns is safe.

Prevention (recommended): protect the **Students** header row in Google Sheets —
select row 1 → **Data → Protect sheets and ranges → "Show a warning when editing
this range."** Warning mode catches accidental header edits without hard-blocking
legit changes or the automation (which only reads Students). Do **not** protect
the `FC_*` tabs — this workflow rewrites those each run.
