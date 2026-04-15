# Prompt to Give Claude Code in Your IDE

I need you to build the WGCS student onboarding workflow for First Chord Music School.

## Task
Build a CLI command: `python brain.py onboard "Student Name"` that guides me through 6-step student onboarding.

## Read These Files First
1. **IMPORTANT_UPDATES.md** - Latest requirements (READ FIRST!)
2. **REFERENCE_DATA.md** - All templates, pricing, exact wording
3. **ONBOARDING_WORKFLOW_SPEC.md** - Technical implementation spec

## Key Requirements
- Default to 30 min lessons / £25
- Stripe link: https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A (same for all)
- Pull tutor info from Google Sheets (Tutors tab)
- Include Soundslice follow-up message (code: tnc aux 3x3)
- Create new vault at ./vault
- Use EXACT templates from REFERENCE_DATA.md

## Before You Start
Ask me for:
1. Google Sheets spreadsheet ID
2. MyMusicStaff Bearer token
3. Vault path confirmation (./vault okay?)

Then build following ONBOARDING_WORKFLOW_SPEC.md

## WGCS Steps
W - WhatsApp group notification
G - Google Sheets addition (automatic)
C - MMS Calendar creation (automatic)
S - Welcome message + Soundslice follow-up
💸 - Stripe subscription (automatic)
🏘️ - Community WhatsApp addition

Time saved: ~20 min manual → ~3 min with Brain
