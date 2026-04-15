# Copy-Paste Feature 📋

## What's New

At the end of every onboarding, Brain now shows a **tab-separated row** ready to paste directly into Google Sheets!

## How It Works

After completing the 5 WGCS steps, you'll see:

```
┌─────────────────────────────────────────────────┐
│ 📋 GOOGLE SHEETS ROW (Ready to paste)          │
└─────────────────────────────────────────────────┘

Columns: Tutor | Surname | Forename | Email | MMS | Theta | Soundslice | Instrument | Parent Surname | Parent Forename

┌─ Copy this row (Cmd+C) ────────────────────────┐
│                                                 │
│  ARION	Norman	Indy	catcubie@hotmail.com		indyfc	https://www.soundslice.com/courses/14429/	guitar	Cubie	Cat  │
│                                                 │
└─────────────────────────────────────────────────┘

✓ Row copied to clipboard! Just Cmd+V in Google Sheets 📋

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

## Benefits

### 1. **Auto-Copied to Clipboard**
The row is automatically copied to your clipboard. Just:
1. Open Google Sheets
2. Click on the next empty row
3. Press Cmd+V (or Ctrl+V)
4. Done! All cells populate correctly

### 2. **Verification**
See exactly what values will be pasted:
- Column headers shown for reference
- Individual values listed with labels
- Easy to spot any mistakes before pasting

### 3. **Backup Method**
If Google Sheets API fails or you prefer manual entry:
- No need to retype everything
- All data formatted correctly
- Just copy and paste

### 4. **Tab-Separated Format**
The format uses tabs (`\t`) between values, which Google Sheets recognizes as separate cells. When you paste:
- Each value goes into its own column
- Maintains exact order (A through J)
- No manual splitting needed

## Example Usage

**Complete workflow:**

```bash
$ python3 brain.py onboard "Indy Norman"

[... complete onboarding ...]

✅ ONBOARDING COMPLETE! 🎉

✅ W  WhatsApp group notified
✅ G  Google Sheets (row 178)
✅ C  MMS Calendar (Dec 17, 4pm, Arion)
✅ S  Welcome message sent to Cat (payment link included)
✅ S  Soundslice follow-up sent (code: jny sdf 4x2)
✅ 🏘️  Community WhatsApp added

Indy Norman (guitar, age 10)
First lesson: Tuesday Dec 17 at 4pm with Arion Xenos

Saved to: vault/Onboarding/2024-12-17-indy-norman.md

┌─────────────────────────────────────────────────┐
│ 📋 GOOGLE SHEETS ROW (Ready to paste)          │
└─────────────────────────────────────────────────┘

[Tab-separated row shown and copied to clipboard]
```

Now just:
1. Open your Google Sheet
2. Find the next empty row
3. Click on column A of that row
4. Press Cmd+V
5. ✅ All 10 columns populate perfectly!

## Two Methods - Your Choice

### Method 1: Automatic (Google Sheets API)
Brain automatically writes to Google Sheets during Step 2/5

**Pros:**
- Fully automatic
- No manual pasting needed

**Cons:**
- Requires Google authentication (first time only)
- Depends on API working

### Method 2: Manual Copy-Paste
Use the formatted row at the end

**Pros:**
- Works even if API fails
- Can verify before pasting
- No authentication needed
- Faster if you're already in the sheet

**Cons:**
- Manual paste step required

### Best Practice: Both!
Brain does both automatically:
1. Writes via API (Step 2) ← Automatic
2. Shows copy-paste row (End) ← Backup & verification

This way you get:
- ✅ Automatic population
- ✅ Visual confirmation
- ✅ Manual backup option

## What Gets Formatted

**The 10 columns in exact order:**

| # | Column | Example Value |
|---|--------|---------------|
| A | Tutor Name | ARION |
| B | Student surname | Norman |
| C | Student forename | Indy |
| D | Email | catcubie@hotmail.com |
| E | MMS ID | *(blank initially)* |
| F | Theta username | indyfc |
| G | Soundslice URL | https://www.soundslice.com/courses/14429/ |
| H | Instrument | guitar |
| I | Parent surname | Cubie |
| J | Parent forename | Cat |

## Technical Details

**Format:** Tab-separated values (TSV)
**Separator:** Tab character (`\t`)
**Clipboard:** Auto-copied using `pyperclip`
**Encoding:** UTF-8 (handles special characters like "Eléna")

**Why tabs?**
Google Sheets recognizes tabs as column separators. When you paste:
- One tab = move to next column
- Content between tabs = cell value
- Perfect alignment every time

## Quick Reference

**Copy the row:**
Already done! It's auto-copied to clipboard

**Paste in Google Sheets:**
1. Click on first empty cell in column A
2. Cmd+V (Mac) or Ctrl+V (Windows)
3. Done!

**Verify values:**
Check the "Individual values" section before pasting

**Re-copy if needed:**
Click in the panel with the tab-separated text and manually copy

---

**Status:** ✅ Feature complete and tested!
**Works with:** All Google Sheets, Excel, Numbers, any spreadsheet app
