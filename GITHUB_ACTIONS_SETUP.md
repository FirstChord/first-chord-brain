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
- `DASHBOARD_REPO_TOKEN`

## Secret notes

### `DASHBOARD_REPO_TOKEN`

This token is used only so the Brain workflow can read the private dashboard repo.

Minimum useful access:

- access to `FirstChord/first-chord-dashbord`
- `Contents: Read`

A fine-grained token is preferable.

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
