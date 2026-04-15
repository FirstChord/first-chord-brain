# 🧠 First Chord Brain

**CLI tool for First Chord Music School student onboarding**

Automates the 5-step WGCS (WhatsApp → Google Sheets → MMS Calendar → Welcome + Soundslice → Community) onboarding workflow.

**Time saved:** ~20 min manual → ~3 min with Brain ⚡

## Quick Start

### 1. Install Dependencies

```bash
cd ~/Desktop/first-chord-brain
pip3 install -r requirements.txt
```

### 2. Authenticate with Google Sheets

The first time you run the tool, you'll need to authenticate with Google:

```bash
cd ~/Desktop/first-chord-brain
python3 brain.py onboard "Test Student"
```

This will open a browser window for OAuth. Grant access to your Google account.

### 3. Onboard a Student

```bash
cd ~/Desktop/first-chord-brain
python3 brain.py onboard "Sarah Jones"
```

## Testing

Before running a full onboarding, verify the TSV export functionality works:

```bash
cd ~/Desktop/first-chord-brain
python3 tests/test_tsv_export.py
```

**Expected output:**
```
🧪 Testing TSV Export Functionality...
...
🎉 ALL TESTS PASSED!
```

This quick test (30 seconds) verifies:
- TSV file creation works
- File format is correct (10 columns, tab-separated)
- Exports directory is accessible
- File I/O works with UTF-8 encoding

**For full testing protocol**, see `PROTOCOLS.md`

## What It Does

The Brain guides you through 5 steps:

1. **W** - WhatsApp group notification ("Student Name - WGCS")
2. **G** - Google Sheets addition (automatic - also creates TSV file for import)
3. **C** - MMS Calendar creation (automatic first lesson)
4. **S** - Welcome message + Soundslice follow-up (auto-generated, copied to clipboard)
5. **🏘️** - Community WhatsApp addition

## Features

✅ **Smart tutor suggestion** - Filters tutors by instrument (15 teachers supported)
✅ **Exact templates** - Uses official First Chord messaging templates
✅ **Default pricing** - Always 30 min / £25 (as per latest requirements)
✅ **Per-student Soundslice** - Unique course code for each student
✅ **TSV export** - Creates backup file + copies to clipboard for Google Sheets
✅ **Auto-generated usernames** - Theta usernames (firstnamefc pattern)
✅ **Vault records** - Auto-saves to `./vault/Onboarding/` for tracking
✅ **Rich console UI** - Beautiful terminal interface with colors and panels

## Architecture

```
first-chord-brain/
├── brain.py                    # Main CLI entry point
├── src/
│   ├── onboarding.py          # Main workflow orchestration
│   ├── sheets_client.py       # Google Sheets integration
│   ├── mms_client.py          # MyMusicStaff API client
│   └── templates.py           # Message templates
├── tests/
│   └── test_tsv_export.py     # Automated TSV export test
├── exports/                   # TSV files (git-ignored)
├── vault/                     # Obsidian vault for records
│   ├── Onboarding/           # Auto-generated onboarding records
│   ├── Templates/
│   └── Reference/
├── .env                       # API credentials (NOT in git)
├── .clauderules               # Coding standards
├── PROTOCOLS.md               # Development workflows
└── requirements.txt           # Python dependencies
```

## Configuration

All API credentials are in `.env` (git-ignored for security):

- `GOOGLE_SPREADSHEET_ID` - Your Google Sheets spreadsheet ID
- `MMS_BEARER_TOKEN` - MyMusicStaff JWT token
- `MMS_SCHOOL_ID` - Your MMS school ID
- `STRIPE_PAYMENT_LINK` - Universal payment link (same for all students)

## Templates

All message templates match the exact wording from First Chord's official templates:

- **Welcome message** - Full onboarding message with address, payment link, handbook
- **Soundslice follow-up** - Instructions for creating Soundslice account
- **Missed call** - Initial inquiry response (future feature)

Experience levels use exact phrasing:
- "a complete beginner"
- "has some experience"
- "at an intermediate level"

## Google Sheets Export

Each onboarding creates a **TSV (Tab-Separated Values) file** in `exports/` and attempts to add directly to Google Sheets.

### TSV Export Features
- ✅ Auto-saved to `exports/YYYY-MM-DD-student-name.tsv`
- ✅ Data row auto-copied to clipboard
- ✅ Two import methods:
  - **Quick paste:** Cmd+V into Google Sheets
  - **File import:** File → Import → Upload TSV (most reliable)

### The 10 Columns

| # | Column Header | Example |
|---|---------------|---------|
| A | Tutor Name | ARION |
| B | Student Surname | Norman |
| C | Student Forename | Indy |
| D | Email | parent@example.com |
| E | MMS ID | *(blank initially)* |
| F | Theta Username | indyfc |
| G | Soundslice | https://www.soundslice.com/courses/14429/ |
| H | Instrument | guitar |
| I | Parent Surname | Cubie |
| J | Parent Forename | Cat |

**See `TSV_EXPORT_FEATURE.md` for detailed guide**

## Vault Integration

Each onboarding creates a markdown file in `vault/Onboarding/`:

```
2024-12-17-sarah-jones.md
```

This contains:
- Student details (age, instrument, experience, interests)
- Lesson details (tutor, day, time, date)
- WGCS checklist (all 5 steps)
- Timestamp and notes

You can open `vault/` as an Obsidian vault to browse all records.

## Default Behavior

The Brain automatically defaults to:
- **Duration:** 30 minutes
- **Price:** £25/month
- **Payment link:** https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A (same for all)
- **Theta username:** firstnamefc (auto-suggested, can override)

It prompts you for:
- Student forename and surname (auto-suggested from full name)
- Instrument (for tutor suggestion)
- Day (e.g., "Tuesday")
- Time (e.g., "4pm")
- Date (e.g., "Dec 17")
- Tutor (filtered by instrument, can override)
- Parent name and email
- Student age
- Experience level (standardized phrases: beginner/some/intermediate)
- Interests/genres
- Soundslice code (unique per student)
- Soundslice URL (optional - for spreadsheet)

## Troubleshooting

**"Could not add to sheet"**
- Check your Google Sheets authentication
- Make sure the spreadsheet ID is correct
- Ensure you have edit permissions

**"No teacher ID found for [tutor]"**
- Check that the tutor name matches Google Sheets exactly
- Or, add their MMS teacher ID to `src/mms_client.py`

**"Could not create lesson"**
- Check that MMS_BEARER_TOKEN is valid
- Verify the tutor has a valid teacher ID in MMS
- Manually create the lesson in MMS if needed

**"TSV file not created"**
- Run the test: `python3 tests/test_tsv_export.py`
- Check exports directory exists and has write permissions
- See `PROTOCOLS.md` for troubleshooting steps

## Documentation

- **`.clauderules`** - Coding standards, conventions, and patterns
- **`PROTOCOLS.md`** - Development workflows, testing procedures, maintenance tasks
- **`TSV_EXPORT_FEATURE.md`** - Complete guide to TSV export and Google Sheets import
- **`QUICK_REFERENCE.md`** - Quick reference for common tasks (if exists)

## Next Steps

**Future features to add:**
- [ ] Missed call template automation
- [ ] Bulk onboarding for multiple students
- [ ] WhatsApp API integration (auto-send messages)
- [ ] Stripe API integration (auto-create subscriptions)
- [ ] Weekly meeting notes generation
- [ ] Student profile pages

## Credits

Built for **First Chord Music School** by Claude Code (Anthropic)

Based on requirements from:
- `Important updates (read first).md`
- `Reference Data.md`
- `Onboarding Workflow.md`
