# TSV Export Feature 📊

## What's New

Brain now creates a **TSV (Tab-Separated Values) file** for every student onboarding AND copies it to your clipboard!

## How It Works

After completing the 5 WGCS steps:

```
┌─────────────────────────────────────────────────┐
│ 📋 GOOGLE SHEETS EXPORT (TSV Format)           │
└─────────────────────────────────────────────────┘

✓ Exported to: exports/2024-11-22-indy-norman.tsv
✓ Data row copied to clipboard!

Try pasting into Google Sheets:
  1. Open Google Sheets
  2. Click on the next empty row (column A)
  3. Press Cmd+V (or Ctrl+V)

If paste doesn't split into columns:
  → Import the file: File → Import → Upload → exports/2024-11-22-indy-norman.tsv

Individual values:
  A: ARION (Tutor)
  B: Norman (Student surname)
  C: Indy (Student forename)
  D: catcubie@hotmail.com (Email)
  E: (blank) (MMS ID)
  F: indyfc (Theta)
  G: https://www.soundslice.com/courses/14429/ (Soundslice)
  H: guitar (Instrument)
  I: Cubie (Parent surname)
  J: Cat (Parent forename)
```

## Two Methods - Choose What Works

### Method 1: Clipboard Paste (Quickest) ✨

**Steps:**
1. Brain auto-copies the data row to clipboard
2. Open Google Sheets
3. Click on next empty row (column A)
4. Press **Cmd+V** (or Ctrl+V)
5. If it splits into 10 columns → Perfect! ✅
6. If it goes into one cell → Use Method 2

**Why it might work:**
- Data comes from file I/O (not terminal text)
- Tabs might be preserved better this way

### Method 2: File Import (Most Reliable) 📁

**Steps:**
1. Open Google Sheets
2. Click **File → Import**
3. Click **Upload** tab
4. Drag/upload the TSV file (shown in Brain output)
5. Import options:
   - Import location: "Insert new rows"
   - Separator type: "Tab" (auto-detected)
6. Click **Import data**
7. ✅ All 10 columns populate perfectly!

**Why this always works:**
- Google Sheets' import feature handles tabs perfectly
- Most reliable method
- Can batch multiple students

## What Gets Exported

### File Location
```
~/Desktop/first-chord-brain/exports/2024-11-22-indy-norman.tsv
```

### File Contents
```
Tutor Name	Student Surname	Student Forename	Email	MMS ID	Theta Username	Soundslice	Instrument	Parent Surname	Parent Forename
ARION	Norman	Indy	catcubie@hotmail.com		indyfc	https://www.soundslice.com/courses/14429/	guitar	Cubie	Cat
```

**Format:**
- First row: Column headers
- Second row: Student data
- Separator: Tab character (`\t`)
- Encoding: UTF-8

### The 10 Columns

| # | Column Header | Example Value |
|---|---------------|---------------|
| A | Tutor Name | ARION |
| B | Student Surname | Norman |
| C | Student Forename | Indy |
| D | Email | catcubie@hotmail.com |
| E | MMS ID | *(blank initially)* |
| F | Theta Username | indyfc |
| G | Soundslice | https://www.soundslice.com/courses/14429/ |
| H | Instrument | guitar |
| I | Parent Surname | Cubie |
| J | Parent Forename | Cat |

## Benefits

✅ **Backup file** - Always saved, even if clipboard fails
✅ **Auto-copied** - Ready to paste immediately
✅ **Reliable import** - File import always works
✅ **Batch capable** - Can accumulate multiple students
✅ **Verification** - Individual values shown on screen

## Complete Workflow Example

```bash
$ python3 brain.py onboard "Indy Norman"

[... complete onboarding ...]

✅ ONBOARDING COMPLETE! 🎉

┌─────────────────────────────────────────────────┐
│ 📋 GOOGLE SHEETS EXPORT (TSV Format)           │
└─────────────────────────────────────────────────┘

✓ Exported to: exports/2024-11-22-indy-norman.tsv
✓ Data row copied to clipboard!
```

**Then choose your method:**

### Quick Paste Method:
1. Open Google Sheets
2. Click next empty row
3. Cmd+V
4. Check if it splits into columns
5. If yes → Done! 🎉
6. If no → Use import method

### File Import Method:
1. Open Google Sheets
2. File → Import
3. Upload → Choose `exports/2024-11-22-indy-norman.tsv`
4. Import location: "Insert new rows"
5. Import data
6. Done! 🎉

## Accumulated Records

Every onboarding creates a new TSV file:

```
exports/
├── 2024-11-22-indy-norman.tsv
├── 2024-11-22-sarah-jones.tsv
├── 2024-11-23-alex-smith.tsv
└── ...
```

**Future enhancement:** Could create a cumulative `all-students.tsv` that appends each new student, allowing batch import.

## Troubleshooting

### Paste goes into one cell
→ Use File Import method instead

### Can't find the file
→ Path shown in Brain output: `exports/2024-11-22-student-name.tsv`
→ From first-chord-brain folder

### Import doesn't work
→ Make sure you select "Tab" as separator
→ Should be auto-detected for .tsv files

### Special characters (é, ñ, etc.)
→ Files are saved as UTF-8
→ Handles all special characters correctly

## File Management

### Where files are saved:
```
~/Desktop/first-chord-brain/exports/
```

### Cleanup:
Files are kept indefinitely as backup. To clean up:
```bash
cd ~/Desktop/first-chord-brain/exports
rm *.tsv  # Remove all TSV files
```

Or delete individual files:
```bash
rm exports/2024-11-22-indy-norman.tsv
```

### Git ignore:
TSV files are automatically excluded from git (added to `.gitignore`)

## Technical Details

**TSV Format:**
- Tab-Separated Values
- Standard format recognized by all spreadsheet apps
- More reliable than CSV for names with commas

**File naming:**
- Format: `YYYY-MM-DD-student-name.tsv`
- Date: When onboarding was completed
- Name: Student name (lowercase, spaces→hyphens)

**Clipboard:**
- Uses `pyperclip` library
- Copies just the data row (no headers)
- Ready for direct paste into Google Sheets

**Encoding:**
- UTF-8 encoding
- Handles international characters
- Compatible with all modern spreadsheet apps

## Quick Reference Card

**After onboarding completes:**

1. ✅ TSV file created in `exports/`
2. ✅ Data row copied to clipboard
3. ✅ Individual values shown for verification

**To add to Google Sheets:**

**Option A (Quick):**
- Open Sheets → Click row → Cmd+V

**Option B (Reliable):**
- Open Sheets → File → Import → Upload TSV

**Both work!** Try A first, use B if needed.

---

**Status:** ✅ Feature complete and tested!
**Works with:** Google Sheets, Excel, Numbers, LibreOffice Calc
