# Teacher Database Update 🎓

**Updated:** 2025-11-22

## What Changed

Updated the Brain with complete teacher information for smarter tutor selection!

## All Teachers Added

| Name | Instruments | MMS ID |
|------|-------------|---------|
| Arion (Arion Xenos) | guitar, piano | `tch_zplpJw` |
| Dean (Dean Louden) | guitar, bass | `tch_zV9TJN` |
| Eléna (Eléna Esposito) | piano | `tch_zpy4J9` |
| Fennella (Fennella McCallum) | singing, piano | `tch_C2bJ9` |
| Finn (Finn Le Marinel) | guitar, bass, ukulele | `tch_QhxJJ` |
| Kenny (Kenny Bates) | guitar | `tch_zsyfJr` |
| Kim (Kim Grant) | guitar | `tch_zVg1Js` |
| Patrick (Patrick Shand) | guitar, piano | `tch_zw9SJ3` |
| Robbie (Robbie Tranter) | guitar, bass | `tch_zV9hJ2` |
| Stef (Stef McGlinchey) | guitar | `tch_z5YmJX` |
| Tom (Tom Walters) | guitar, bass | `tch_mYJJR` |
| Maks | guitar, bass | `tch_zHdxJZ` |
| Ines | piano | `tch_zHJlJx` |
| David (David Husz) | guitar, piano | `tch_z2j2Jf` |

## Tutor Suggestions by Instrument

**Piano:**
- Arion, Eléna, Fennella, Patrick, Ines, David

**Guitar:**
- Arion, Dean, Finn, Kenny, Kim, Patrick, Robbie, Stef, Tom, Maks, David

**Bass:**
- Dean, Finn, Robbie, Tom, Maks

**Singing:**
- Fennella

**Ukulele:**
- Finn

## Improvements to Brain

### 1. **Smart Tutor Selection**

When you select an instrument, Brain now:
- Shows all tutors who teach that instrument
- If only one tutor → suggests automatically
- If multiple tutors → lets you choose from list
- Always shows what instruments each tutor teaches

**Example for Piano:**
```
Selecting tutor...

6 tutors teach piano:
  1. Arion (Arion Xenos) - guitar, piano
  2. Eléna (Eléna Esposito) - piano
  3. Fennella (Fennella McCallum) - singing, piano
  4. Patrick (Patrick Shand) - guitar, piano
  5. Ines (Ines) - piano
  6. David (David Husz) - guitar, piano

Choose tutor [1/2/3/4/5/6/other]:
```

**Example for Singing:**
```
Selecting tutor...

Suggestion: Fennella teaches singing
Use Fennella? [Y/n]:
```

### 2. **Manual Override**

If you want a different tutor, you can:
- Type `other` to see the full tutor list
- Select from all 14 tutors with their instruments shown

### 3. **No More Google Sheets Dependency**

Previously, tutor suggestions required:
- ✗ Google Sheets authentication
- ✗ Internet connection to Sheets API
- ✗ Correct column naming in Sheets

Now:
- ✓ Instant tutor lookup (no API calls)
- ✓ Works offline
- ✓ Always up-to-date with this file

## How It Works

Teacher data is now stored directly in `src/mms_client.py`:

```python
self.teachers = {
    'Arion': {
        'full_name': 'Arion Xenos',
        'teacher_id': 'tch_zplpJw',
        'instruments': ['guitar', 'piano']
    },
    # ... etc
}
```

When you run onboarding:
1. Brain asks for instrument
2. Brain searches `teachers` dictionary
3. Finds all tutors with that instrument
4. Shows you options
5. Uses the selected tutor's MMS ID for calendar creation

## Testing

Test the tutor lookup:

```bash
cd ~/Desktop/first-chord-brain
python3 -c "
from src.mms_client import MMSClient
mms = MMSClient()

print('Piano tutors:', [t['short_name'] for t in mms.get_tutors_for_instrument('piano')])
print('Guitar tutors:', [t['short_name'] for t in mms.get_tutors_for_instrument('guitar')])
print('Bass tutors:', [t['short_name'] for t in mms.get_tutors_for_instrument('bass')])
print('Singing tutors:', [t['short_name'] for t in mms.get_tutors_for_instrument('singing')])
"
```

**Expected output:**
```
Piano tutors: ['Arion', 'Eléna', 'Fennella', 'Patrick', 'Ines', 'David']
Guitar tutors: ['Arion', 'Dean', 'Finn', 'Kenny', 'Kim', 'Patrick', 'Robbie', 'Stef', 'Tom', 'Maks', 'David']
Bass tutors: ['Dean', 'Finn', 'Robbie', 'Tom', 'Maks']
Singing tutors: ['Fennella']
```

## Adding New Teachers

To add a new teacher in the future:

1. Open `src/mms_client.py`
2. Find the `self.teachers` dictionary
3. Add a new entry:

```python
'NewTeacher': {
    'full_name': 'New Teacher Full Name',
    'teacher_id': 'tch_XXXXXXX',  # Get from MMS
    'instruments': ['guitar', 'piano']  # List all instruments
}
```

4. Save the file
5. Brain will automatically use the new teacher!

## Next Steps for Brain Evolution

With this teacher database, we can now add:

- [ ] **Availability checking** - Check which tutors have free slots
- [ ] **Smart scheduling** - Suggest best times based on tutor availability
- [ ] **Student-tutor matching** - Match based on learning style, genres, etc.
- [ ] **Capacity tracking** - Track how many students each tutor has
- [ ] **Instrument combos** - Suggest tutors for students learning multiple instruments

---

**Files updated:**
- `src/mms_client.py` - Added complete teacher database
- `src/onboarding.py` - Improved tutor selection logic
- This file - Documentation

**Status:** ✅ Complete and tested
