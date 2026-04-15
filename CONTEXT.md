# First Chord — System Context

**Read this file first.** It describes the full system, how the tools connect, where credentials live, and how to perform common tasks. Maintained in `first-chord-brain/` which is the system hub.

---

## What First Chord Is

A music school run by Finn Le Marinel. ~200 active students, 16 tutors. Students have lessons booked via MyMusicStaff (MMS), pay via Stripe, and access learning materials via Soundslice and Theta Music Trainer.

---

## Workspace Structure

```
~/Desktop/FirstChord/
├── first-chord-brain/        ← YOU ARE HERE — hub, FC identity layer, onboarding CLI
├── music-school-dashboard/   ← Next.js student portal + tutor dashboard (Railway)
└── payment-pause-pwa/        ← Firebase PWA for pausing/resuming Stripe subscriptions
```

All cross-tool paths are defined in `first-chord-brain/config.py`. Never hardcode paths elsewhere.

---

## The Three Tools

### 1. first-chord-brain
- **What it does:** Interactive CLI for onboarding new students (WGCS workflow). Also houses the FC identity layer — the canonical ID and cross-reference system for the whole school.
- **Run onboarding:** `python3 brain.py onboard "Student Name"`
- **Regenerate FC identity layer:** `python3 generate_fc_ids.py` (writes CSVs + updates Google Sheets directly)
- **Audit registry vs Sheets:** `python3 audit_cross_reference.py`
- **Key files:**
  - `config.py` — all workspace paths
  - `generate_fc_ids.py` — generates FC IDs, writes to Sheets
  - `src/mms_client.py` — tutor master list + MMS API
  - `src/onboarding.py` — full WGCS onboarding flow
  - `src/sheets_client.py` — writes new students to Google Sheets
  - `exports/fc_identity_layer/` — local CSV backup of FC identity layer

### 2. music-school-dashboard
- **What it does:** Next.js app. Student-facing portal (Soundslice, Theta login). Tutor-facing dashboard (MMS API). Deployed on Railway.
- **Git remote:** `https://github.com/FirstChord/first-chord-dashbord.git`
- **Deploy:** `git push` → Railway auto-deploys in ~2 min
- **Registry:** `lib/config/students-registry.js` — 200 students, keyed by MMS ID. **Only file you manually edit.**
- **Add a student:** use the `add-student` Claude skill (see `~/.claude/skills/add-student/SKILL.md`)
- **Regenerate configs:** `npm run generate-configs` (run from dashboard root after editing registry)
- **Validate:** `npm run validate`

### 3. payment-pause-pwa
- **What it does:** Firebase PWA + Cloud Functions. Allows pausing/resuming a student's Stripe subscription and marking MMS attendance. Used by school admin.
- **Deployed to:** Firebase Hosting + Functions
- **Local dev:** `bash start-dev.sh` (from payment-pause-pwa root)
- **Deploy:** `npx firebase deploy`
- **Key config:** `functions/.env.local` (Stripe + MMS keys), `firebase.json`

---

## FC Identity Layer

The canonical identity system linking all external IDs together.

### ID Formats
| Format | Represents | Seed |
|---|---|---|
| `fc_per_XXXXXXXX` | A person (student, parent, tutor) | MMS ID or `parent:{email}` |
| `fc_std_XXXXXXXX` | A student record | MMS student ID |
| `fc_tut_XXXXXXXX` | A tutor record | MMS teacher ID |

IDs are **deterministic**: `sha256(seed)[:8]`. Same seed always → same ID. Safe to regenerate.

New students onboarded via Brain get `fc_std_` from `forename:surname:email` (pre-MMS). Once MMS ID is known, it's linked via `FC_External_IDs`.

### Google Sheets Tabs (First Chord Database)
| Tab | Contents |
|---|---|
| `Students` | Live student roster (Brain + Payment Pause source of truth) |
| `Pause History` | Log of payment pauses |
| `FC_Students` | 199 students with FC IDs, `is_adult` flag |
| `FC_People` | 349 people: tutors + students + parents |
| `FC_Tutors` | 16 active tutors with FC + MMS IDs |
| `FC_Parent_Student_Links` | 150 parent→student relationships |
| `FC_External_IDs` | 942 mappings: MMS, Stripe, Soundslice, Theta |

**To regenerate:** `python3 generate_fc_ids.py` — fetches live data, writes all 5 FC tabs directly.

### Adult Students
38 students are adults (no parent). Detected by: parent name == student name in Sheets. `is_adult=TRUE` in `FC_Students`. No ghost parent entity or parent-student link is created for them.

---

## Tutor Roster (16 active)

| Short name | Full name | MMS ID | FC Tutor ID |
|---|---|---|---|
| Arion | Arion Xenos | tch_zplpJw | fc_tut_aeba5d62 |
| Calum | Calum Steel | tch_zMX5Jc | fc_tut_c4d8acd0 |
| Chloe | Chloe Mak | tch_zQbNJk | fc_tut_10f79b99 |
| David | David Husz | tch_z2j2Jf | fc_tut_31a1e455 |
| Dean | Dean Louden | tch_zV9TJN | fc_tut_6133f361 |
| Eléna | Eléna Esposito | tch_zpy4J9 | fc_tut_563694ef |
| Fennella | Fennella McCallum | tch_C2bJ9 | fc_tut_1aacc30d |
| Finn | Finn Le Marinel | tch_QhxJJ | fc_tut_b9b45f54 |
| Ines | Ines Alban Zapata Peréz | tch_zHJlJx | fc_tut_e22aab88 |
| Kenny | Kenny Bates | tch_zsyfJr | fc_tut_41c8e78a |
| Kim | Kim Grant | tch_zVg1Js | fc_tut_ed4fa93b |
| Patrick | Patrick Shand | tch_zw9SJ3 | fc_tut_e3b01d7a |
| Robbie | Robbie Tranter | tch_zV9hJ2 | fc_tut_6398f1e6 |
| Scott | Scott Brice | tch_zMWrJR | fc_tut_12949202 |
| Stef | Stef McGlinchey | tch_z5YmJX | fc_tut_3cfe36ee |
| Tom | Tom Walters | tch_mYJJR | fc_tut_084e84bf |

Single source of truth: `first-chord-brain/src/mms_client.py`. To add a tutor: add entry there, run `npm run generate-configs` in dashboard.

---

## Credentials

| What | Where | Used by |
|---|---|---|
| Google Sheets OAuth token | `~/token_musiclessons.json` | Brain, generate_fc_ids.py |
| Google OAuth client credentials | `~/credentials_musiclessons.json` | Brain |
| Google Spreadsheet ID | `first-chord-brain/.env` → `GOOGLE_SPREADSHEET_ID` | generate_fc_ids.py, sheets_client.py |
| MMS Bearer Token | `first-chord-brain/.env` → `MMS_BEARER_TOKEN` | mms_client.py |
| Stripe keys | `payment-pause-pwa/functions/.env.local` | Payment Pause Firebase functions |
| Firebase config | `payment-pause-pwa/public/firebase-config.js` | Payment Pause frontend |

Google token refreshes automatically — no browser login needed.

---

## Common Tasks

### Add a new student (dashboard)
Use the `add-student` Claude skill: `~/.claude/skills/add-student/SKILL.md`
Summary: generate `fcStudentId` → edit `students-registry.js` → `npm run generate-configs` → `npm run validate` → git push

### Look up any person, student, or tutor
```bash
python3 ~/Desktop/FirstChord/first-chord-brain/brain.py lookup "Ryan Ofee"
python3 ~/Desktop/FirstChord/first-chord-brain/brain.py lookup sdt_2grxJL
python3 ~/Desktop/FirstChord/first-chord-brain/brain.py lookup cus_R7DL79Smc0cwBE
python3 ~/Desktop/FirstChord/first-chord-brain/brain.py lookup "Elena"
```
Returns: FC IDs, MMS ID, Stripe IDs, tutor, instrument, Soundslice, Theta, parent/children.
Also importable: `from lookup import lookup; result = lookup("Ryan Ofee")`

### Onboard a new student (full WGCS flow)
```bash
python3 ~/Desktop/FirstChord/first-chord-brain/brain.py onboard "Student Name"
```

### Regenerate FC identity layer
```bash
cd ~/Desktop/FirstChord/first-chord-brain
python3 generate_fc_ids.py
```
Fetches fresh data from Sheets + registry, regenerates all FC IDs, writes 5 tabs to First Chord Database.

### Edit Google Sheets directly (Python)
```python
import json, gspread
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

token = json.loads(Path.home().joinpath('token_musiclessons.json').read_text())
creds = Credentials(token=None, refresh_token=token['refresh_token'],
    client_id=token['client_id'], client_secret=token['client_secret'],
    token_uri='https://oauth2.googleapis.com/token',
    scopes=['https://www.googleapis.com/auth/spreadsheets'])
creds.refresh(Request())
gc = gspread.authorize(creds)
sh = gc.open_by_key('1Rn6fJEkT3-vTFfOTyanp1AJDzfxPpx9REWGQ-WK8Q2o')
ws = sh.worksheet('Students')  # or any tab name
```

### Deploy dashboard
```bash
cd ~/Desktop/FirstChord/music-school-dashboard
git add . && git commit -m "..." && git push
# Railway auto-deploys from GitHub
```

### Deploy Payment Pause
```bash
cd ~/Desktop/FirstChord/payment-pause-pwa
npx firebase deploy
```

---

## Data Quality — Known Issues (28 review flags)

Run `cat exports/fc_identity_layer/review_flags.txt` for the full list. These are **known, tracked defects** — not random breakage. The system functions correctly with them present.

| Category | Count | Meaning | Urgency |
|---|---|---|---|
| `TUTOR CONFLICT` | 6 | Registry and Sheets disagree on tutor assignment (e.g. Eléna↔Ines, Scott↔Kenny swapped) | Low — cosmetic only |
| `REGISTRY ONLY` | 12 | In dashboard registry but missing a Sheets row | Low — student has a dashboard page but no Sheets entry |
| `SHEETS ONLY` | 10 | In Sheets but not in dashboard registry | Low — student is known to Brain/identity but has no dashboard page |

To re-run flags: `python3 generate_fc_ids.py` (flags are regenerated each time).

---

## What's NOT Yet Done
- Dashboard `generate-configs` doesn't yet pass `fcStudentId` through to generated config files
- When a pre-MMS student gets their MMS ID added to Sheets, their FC ID changes (from name/email seed to MMS seed) — future work to preserve the old ID as a legacy link in `FC_External_IDs`
