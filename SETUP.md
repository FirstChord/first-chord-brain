# First Chord Brain - Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies ✅

Dependencies are already installed! But if you need to reinstall:

```bash
cd ~/Desktop/first-chord-brain
pip3 install -r requirements.txt
```

### 2. First-Time Google Authentication

The first time you run Brain, you'll need to authenticate with Google Sheets:

```bash
python3 brain.py onboard "Test Student"
```

This will:
1. Open your browser
2. Ask you to log in to Google
3. Request permission to access Google Sheets
4. Save credentials locally for future use

**Grant the requested permissions** - Brain needs to:
- Read from the "Tutors" sheet (to suggest tutors)
- Write to the "Students" sheet (to add new students)

### 3. Test the Workflow

Try onboarding a test student:

```bash
python3 brain.py onboard "Test Student"
```

Follow the prompts. You can cancel at any time with Ctrl+C.

## What You'll Need During Onboarding

Brain will ask you for:

1. **Instrument** (e.g., Piano, Guitar, Drums)
   - Used to suggest a tutor automatically

2. **Lesson Details**
   - Day: Tuesday, Thursday, etc.
   - Time: 4pm, 5:30pm, etc.
   - Date: Dec 17, January 10, etc.

3. **Tutor**
   - Brain will suggest based on instrument
   - You can override if needed

4. **Student Info**
   - Parent name
   - Student age
   - Experience level (1-3)
   - Interests/genres

Then Brain will guide you through the 6 WGCS steps!

## Troubleshooting

### "Could not authenticate with Google"

Run this to re-authenticate:
```bash
cd ~/Desktop/first-chord-brain
rm ~/.credentials/sheets.googleapis.com-python-quickstart.json
python3 brain.py onboard "Test"
```

### "No tutor found for [instrument]"

Check your Google Sheets "Tutors" tab:
- Make sure `DefaultInstrument` column matches (case-insensitive)
- Make sure `Active` column is set to TRUE
- If no match, Brain will ask you to enter a tutor name manually

### "Could not create MMS lesson"

This could be because:
1. MMS Bearer token expired (update in `.env`)
2. Teacher ID not found (add to `src/mms_client.py`)
3. MMS API is down

You can continue with onboarding and create the lesson manually in MMS later.

## What Gets Created

After each onboarding:

1. **Row in Google Sheets** - Student added to row 177+
2. **Lesson in MMS** - First lesson created in calendar
3. **Vault Record** - Markdown file saved to `vault/Onboarding/`

Example vault file: `vault/Onboarding/2024-12-17-sarah-jones.md`

## Tips

- **Messages are auto-copied** - Just paste into WhatsApp
- **All defaults to 30 min / £25** - No need to specify pricing
- **Soundslice is automatic** - Both messages are generated
- **Use Cmd+V** to paste the copied messages

## Next Steps

Once you're comfortable with the workflow, you can:

1. **Open the vault in Obsidian** - Browse all onboarding records
2. **Customize templates** - Edit `src/templates.py`
3. **Add more tutors** - Update Google Sheets "Tutors" tab
4. **Automate more steps** - WhatsApp API, Stripe API, etc.

---

**Ready to onboard?**

```bash
python3 ~/Desktop/first-chord-brain/brain.py onboard "Student Name"
```

Or add an alias to your shell:

```bash
echo 'alias fcb="python3 ~/Desktop/first-chord-brain/brain.py"' >> ~/.zshrc
source ~/.zshrc

# Then just run:
fcb onboard "Student Name"
```
