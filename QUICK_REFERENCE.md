# First Chord Brain - Quick Reference Card 📋

## One Command to Onboard

```bash
python3 ~/Desktop/first-chord-brain/brain.py onboard "Student Name"
```

## What You'll Be Asked

1. **Instrument** (e.g., piano, guitar, bass, singing, ukulele)
2. **Day** (e.g., Tuesday)
3. **Time** (e.g., 4pm)
4. **Date** (e.g., Dec 17)
5. **Tutor** (suggested automatically based on instrument)
6. **Parent name**
7. **Student age**
8. **Experience level** (1=beginner, 2=some experience, 3=intermediate)
9. **Interests/genres** (e.g., "Pop music and Taylor Swift")

## The 6 WGCS Steps

Brain guides you through:

1. **W** - WhatsApp group ("Student Name - WGCS")
2. **G** - Google Sheets (auto-adds to Students tab)
3. **C** - MMS Calendar (auto-creates first lesson)
4. **S** - Welcome message (auto-copied to clipboard)
5. **S** - Soundslice follow-up (auto-copied to clipboard)
6. **💸** - Stripe (link already in welcome message)
7. **🏘️** - Community WhatsApp

## Tips

✅ **Messages are auto-copied** - Just Cmd+V to paste into WhatsApp
✅ **Default is always 30min / £25** - No need to specify
✅ **Soundslice code is automatic** - tnc aux 3x3
✅ **Ctrl+C to cancel** - Anytime during the process

## Tutor Selection Examples

**Piano** → Shows: Arion, Eléna, Fennella, Patrick, Ines, David
**Guitar** → Shows: Arion, Dean, Finn, Kenny, Kim, Patrick, Robbie, Stef, Tom, Maks, David
**Bass** → Shows: Dean, Finn, Robbie, Tom, Maks
**Singing** → Auto-suggests: Fennella
**Ukulele** → Auto-suggests: Finn

## After Onboarding

Check the vault for records:
```bash
ls ~/Desktop/first-chord-brain/vault/Onboarding/
```

Each onboarding creates a file:
```
2024-12-17-student-name.md
```

## Troubleshooting

**"Could not authenticate with Google"**
→ Run the onboarding once to authenticate via browser

**"No teacher ID found"**
→ Teacher data is built-in now, this shouldn't happen!

**"Could not create MMS lesson"**
→ Check MMS_BEARER_TOKEN in .env file
→ Create lesson manually in MMS if needed
→ Onboarding can continue without it

## Make It Even Faster

Add an alias to your shell:

```bash
echo 'alias fcb="python3 ~/Desktop/first-chord-brain/brain.py"' >> ~/.zshrc
source ~/.zshrc
```

Then just run:
```bash
fcb onboard "Student Name"
```

---

**Time saved:** 20 minutes → 3 minutes per student ⚡
