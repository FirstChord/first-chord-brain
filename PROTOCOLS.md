# First Chord Brain - Development Protocols 🛠️

**Last Updated:** 2025-11-22

This document outlines development workflows, testing procedures, and maintenance protocols for the First Chord Brain project.

---

## Quick Testing

### Test TSV Export (30 seconds)
Before doing a full onboarding, test that TSV export works:

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

If all tests pass ✅ → TSV export is working correctly!

### Full Onboarding Test (3 minutes)
Test the complete workflow with dummy data:

```bash
python3 brain.py onboard "Test Student"
```

**Use test data:**
- Instrument: Guitar
- Day: Tuesday
- Time: 4pm
- Date: Dec 17
- Tutor: Choose any available
- Parent: Test Parent
- Email: test@example.com
- Age: 10
- Experience: 1 (beginner)
- Interests: Rock music
- Soundslice code: test 123
- Soundslice URL: (leave blank)
- Theta: testfc

**Verify:**
- ✅ All 5 steps complete without errors
- ✅ TSV file created in `exports/`
- ✅ Vault record created
- ✅ Messages copied to clipboard
- ✅ Individual values displayed correctly

---

## Development Workflow

### Adding a New Feature

1. **Plan First**
   - Discuss with Finn what the feature should do
   - Check if it affects existing workflow
   - Consider impact on Google Sheets columns

2. **Update Rules**
   - If coding conventions change → Update `.clauderules`
   - If workflow changes → Update this file (`PROTOCOLS.md`)

3. **Code Changes**
   - Keep modules under 200 lines
   - Add docstrings to new functions
   - Use Rich library for user output
   - Handle errors gracefully

4. **Testing**
   - Write a test in `tests/` if critical functionality
   - Run existing tests: `python3 tests/test_tsv_export.py`
   - Do a full manual onboarding test
   - Verify TSV file format is correct

5. **Documentation**
   - Create an update doc: `UPDATES_YYYY-MM-DD.md`
   - Update `README.md` if user-facing
   - Update `QUICK_REFERENCE.md` if needed

6. **Commit**
   - Clear commit message
   - Reference issue/feature name

### Modifying Message Templates

**IMPORTANT:** Templates must match First Chord's official wording exactly.

**Location:** `src/templates.py`

**Before changing:**
1. Get exact wording from Finn
2. Verify emojis are correct
3. Check link formatting

**After changing:**
1. Test by running full onboarding
2. Copy generated message
3. Compare with official template word-for-word

**Experience level phrases (NEVER CHANGE):**
- "a complete beginner"
- "has some experience"
- "at an intermediate level"

### Updating Teacher Database

**Location:** `src/mms_client.py` → `self.teachers`

**To add a new teacher:**

```python
'NewTeacher': {
    'full_name': 'New Teacher Full Name',
    'teacher_id': 'tch_XXXXXXX',  # Get from MMS
    'instruments': ['guitar', 'piano']
}
```

**To update teacher info:**
1. Find teacher in dictionary
2. Update instruments list
3. Test tutor selection works

**Verify:**
```bash
python3 -c "
from src.mms_client import MMSClient
mms = MMSClient()
print('Guitar tutors:', [t['short_name'] for t in mms.get_tutors_for_instrument('guitar')])
"
```

### Changing Google Sheets Columns

**⚠️ DANGER ZONE ⚠️**

The Google Sheets column order is **sacred**. Changing it affects:
- Existing spreadsheet structure
- TSV import formatting
- API write operations

**If you MUST change:**
1. Discuss with Finn first
2. Update `.clauderules` with new column order
3. Update `src/sheets_client.py` → `add_student()` method
4. Update `src/onboarding.py` → `_show_copy_paste_row()` method
5. Test extensively before using with real data
6. Document the change prominently

**Current column order (A-J):**
```
A: Tutor Name
B: Student Surname
C: Student Forename
D: Email
E: MMS ID
F: Theta Username
G: Soundslice
H: Instrument
I: Parent Surname
J: Parent Forename
```

---

## Maintenance Tasks

### Weekly
- Test full onboarding workflow
- Check exports folder isn't getting too large
- Verify Google Sheets API still works

### Monthly
- Review teacher database for changes
- Check if any teachers added/removed
- Update MMS teacher IDs if needed
- Clean up old test files in `exports/`

### When First Chord Updates
- **New teacher hired:** Add to `src/mms_client.py`
- **Message wording changes:** Update `src/templates.py`
- **New data field needed:** Discuss column additions first
- **Pricing changes:** Update `.env` if needed

---

## Troubleshooting Protocols

### Google Sheets API Fails

**Symptoms:**
- "Could not add to sheet" error
- Authentication browser window opens repeatedly

**Fix:**
1. Check internet connection
2. Re-authenticate: Delete cached credentials
3. Verify spreadsheet ID in `.env` is correct
4. Check Google account has edit permissions
5. Use TSV import as fallback

**Fallback:**
- TSV files are always created
- Import manually: File → Import → Upload TSV

### TSV Files Not Creating

**Quick test:**
```bash
python3 tests/test_tsv_export.py
```

**If test fails:**
- Check `exports/` folder exists
- Verify write permissions
- Check disk space

**If test passes but onboarding fails:**
- Check the error message
- Verify path resolution in `src/onboarding.py`

### MMS Calendar Fails

**Symptoms:**
- "Could not create lesson" message
- MMS API errors

**Fix:**
1. Check MMS bearer token in `.env`
2. Token might have expired
3. Check teacher ID exists in `src/mms_client.py`
4. Verify MMS API is accessible

**Fallback:**
- Note shown: "Create lesson manually in MMS"
- Workflow continues
- Vault record still saved

### Clipboard Not Working

**Symptoms:**
- "Could not copy to clipboard" warning

**Why:**
- `pyperclip` library issue
- Terminal doesn't have clipboard access

**Fix:**
- Install/reinstall: `pip3 install pyperclip`
- Grant terminal clipboard permissions

**Fallback:**
- Values shown on screen
- TSV file can be imported
- Manual copy still possible

---

## Testing Checklist

Before considering a feature "done":

- [ ] Code compiles: `python3 -m py_compile src/*.py`
- [ ] TSV test passes: `python3 tests/test_tsv_export.py`
- [ ] Full onboarding works with test data
- [ ] TSV file created correctly
- [ ] Vault record saved
- [ ] Messages match official templates
- [ ] Error handling works (try invalid inputs)
- [ ] Documentation updated

---

## File Naming Conventions

### TSV Exports
- Format: `YYYY-MM-DD-student-name.tsv`
- Example: `2025-11-22-indy-norman.tsv`
- Lowercase, hyphens for spaces

### Vault Records
- Format: `YYYY-MM-DD-student-name.md`
- Example: `2024-12-17-sarah-jones.md`
- Lowercase, hyphens for spaces

### Update Documentation
- Format: `UPDATES_YYYY-MM-DD.md`
- Example: `UPDATES_2025-11-22.md`
- Date of the changes

---

## API Credentials Management

### Location
All credentials in `.env` file (git-ignored)

### Never Commit
- MMS Bearer Token
- Google Service Account JSON
- Stripe API keys
- Any email addresses or phone numbers

### Sharing with Finn
If Finn needs to run Brain on new machine:
1. Copy `.env` file separately (not via git)
2. Send via secure method
3. Or have Finn create own `.env` from `.env.example`

### Rotation
- MMS tokens expire → Update when they do
- Google OAuth tokens refresh automatically
- Document when credentials are updated

---

## Emergency Procedures

### Brain Completely Broken

1. **Don't panic** - Students can still be onboarded manually
2. **Use manual process** - Back to WhatsApp/Sheets/MMS by hand
3. **Check recent changes** - What was changed last?
4. **Revert if needed** - Git reset to last working version
5. **Test piece by piece** - Use `tests/` to isolate issue

### Lost API Access

**Google Sheets:**
- Use TSV import as full alternative
- Re-authenticate when access restored

**MyMusicStaff:**
- Create lessons manually
- Update MMS_BEARER_TOKEN when available

### Data Loss Prevention

**Always generated:**
- TSV files (in `exports/`)
- Vault records (in `vault/Onboarding/`)
- Messages shown on screen

**Even if all APIs fail:**
- You have TSV to import
- You have messages to copy
- You have vault record for reference

---

## Future Enhancements (Ideas)

- [ ] Cumulative TSV file (all students in one file)
- [ ] Auto-update MMS ID after lesson creation
- [ ] Batch import multiple students
- [ ] Check for duplicate students before adding
- [ ] WhatsApp API integration (auto-send messages)
- [ ] Stripe API integration (auto-create subscriptions)
- [ ] Dashboard for viewing all onboarded students
- [ ] Export vault to PDF reports

---

## Contact

**Questions about protocols?**
- Check `.clauderules` for coding standards
- Check this file for workflows
- Ask Finn for First Chord-specific questions

**Updating this file:**
- Add date to "Last Updated" at top
- Add notes about what changed
- Keep it practical and actionable

---

**Remember:** Brain is a tool to save time, not create stress.
If something breaks, manual processes still work.
Test early, test often, save backups!
