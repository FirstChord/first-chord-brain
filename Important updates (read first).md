\# IMPORTANT UPDATES \- Read This First\!

 

 

\---

 

\#\# 🔥 Critical Changes

 

\#\#\# 1\. Pricing is Simple\!

 

\*\*Default onboarding:\*\* Always 30 minutes, £25/month

 

Don't ask about lesson length \- just default to 30 mins. Other pricing exists but onboarding is "pretty much always" 30 mins.

 

\*\*All pricing (for reference):\*\*

\- 30 mins: £25

\- 45 mins: £33 (or £20/person for groups)

\- 60 mins: £41.50

 

\#\#\# 2\. ONE Stripe Link for Everything

 

\`\`\`

https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A

\`\`\`

 

Same link for all students, all lesson types. Don't generate unique links.

 

\#\#\# 3\. Soundslice Follow-Up is REQUIRED

 

After the welcome message, automatically show THIS follow-up message:

 

\`\`\`

Oo one last important thing to do. If you could head to soundslice.com and make a free account, then head to soundslice.com/coursecode and pop in this code \*tnc aux 3x3\* that will make a folder that {STUDENT} can access and {TUTOR} can put in all the songs they are learning 💥

\`\`\`

 

\*\*Soundslice code:\*\* Always \`tnc aux 3x3\`

 

\#\#\# 4\. Tutor Information \- Pull from Google Sheets\!

 

Don't hard-code tutor info. Pull from Google Sheets "Tutors" tab:

\- Columns: TutorName, DefaultInstrument, Active, etc.

\- Filter: Active \= true

\- Match: DefaultInstrument with selected instrument

\- Suggest automatically\!

 

Example:

\`\`\`

User selects: Piano

System queries Sheets: Tutors where DefaultInstrument='Piano' AND Active=true

System suggests: "Emma teaches piano. Use Emma? (y/other)"

\`\`\`

 

\#\#\# 5\. Create NEW Obsidian Vault

 

\*\*Path:\*\* \`./vault\` (inside the first-chord-brain repo)

 

\*\*Don't use an existing vault\!\*\* Claude Code should create fresh structure:

 

\`\`\`

vault/

├── Onboarding/              \# Auto-generated records

├── Templates/               \# Message templates

├── Reference/               \# Reference data

└── README.md               \# Vault documentation

\`\`\`

 

\#\#\# 6\. Exact Template Matching

 

The welcome message template is in \`REFERENCE\_DATA.md\` \- use it EXACTLY.

 

Key details:

\- Address: "33 Otago Street G12 8JJ"

\- Always: "inside CC Music Shop"

\- Handbook: "firstchord.co.uk/handbook"

\- Payment link: https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A

 

\#\#\# 7\. Experience Level Phrasing

 

Use these EXACT phrases:

\- ❌ "beginner"

\- ✅ "\*\*a complete beginner\*\*"

 

\- ❌ "some experience"

\- ✅ "\*\*has some experience\*\*"

 

\- ❌ "intermediate"

\- ✅ "\*\*at an intermediate level\*\*"

 

The "a" and "at" matter for grammar in the sentence\!

 

\#\#\# 8\. Additional Template \- Missed Call

 

Finn also has a "missed call" template (see \`REFERENCE\_DATA.md\`). This could be useful for future features but not needed for WGCS onboarding.

 

\---

 

\#\# 📋 Updated Workflow

 

The WGCS workflow is now:

 

1\. \*\*W\*\* \- WhatsApp group ("Student Name \- WGCS")

2\. \*\*G\*\* \- Google Sheets (auto-add to Students tab)

3\. \*\*C\*\* \- MMS Calendar (create 30-min lesson)

4\. \*\*S\*\* \- Welcome message (generate from template) \+ \*\*Soundslice follow-up\*\*

5\. \*\*💸\*\* \- Stripe (£25/month subscription)

6\. \*\*🏘️\*\* \- Community WhatsApp (manual add)

 

Notice: Step 4 now has TWO messages (welcome \+ soundslice)

 

\---

 

\#\# 🎯 Simplified Prompts

 

Since we're defaulting to 30 mins, you don't need to ask:

\- ❌ "What lesson duration?"

\- ❌ "What's the monthly price?"

\- ❌ "Which Stripe link?"

 

Just use:

\- ✅ Duration: 30 mins

\- ✅ Price: £25/month

\- ✅ Link: https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A

 

The prompts you DO need:

1\. Instrument (for tutor suggestion)

2\. Day (e.g., "Tuesday")

3\. Time (e.g., "4pm")

4\. Date (e.g., "Dec 17")

5\. Tutor (suggest from Sheets, allow override)

6\. Parent name

7\. Student age

8\. Experience level (use exact phrasing\!)

9\. Interests/genres

 

\---

 

\#\# 🔧 Google Sheets Integration

 

\*\*Critical:\*\* You MUST pull tutor info from Google Sheets.

 

\*\*Tutors tab structure:\*\*

\- TutorName

\- DefaultInstrument

\- Active (true/false)

\- (other columns exist but these are key)

 

\*\*Query logic:\*\*

\`\`\`python

\# User selected "piano"

tutors \= sheets\_client.get\_tutors()

active\_tutors \= \[t for t in tutors if t\['active'\]\]

piano\_tutors \= \[t for t in active\_tutors if t\['default\_instrument'\].lower() \== 'piano'\]

 

if piano\_tutors:

    suggest \= piano\_tutors\[0\]\['tutor\_name'\]

    \# Show: "Emma teaches piano. Use Emma? (y/other)"

\`\`\`

 

This keeps tutor info current without manual updates\!

 

\---

 

\#\# 💾 Vault Structure Example

 

When onboarding completes, save to:

 

\`\`\`

vault/Onboarding/2024-12-17-sarah-jones.md

\`\`\`

 

Content should include:

\- Student details

\- Lesson info (always 30 min / £25)

\- WGCS checklist (all 6 steps)

\- Timestamp

\- Tutor assigned

\- Welcome message sent (YES)

\- Soundslice sent (YES)

 

\---

 

\#\# ✅ What to Keep from Original Spec

 

Everything else in \`ONBOARDING\_WORKFLOW\_SPEC.md\` is still valid:

\- Overall architecture

\- File structure

\- CLI command pattern

\- Step-by-step flow

\- Pause/resume functionality

\- Rich console output

\- Error handling

 

Just apply these updates on top\!

 

\---

 

\#\# 📚 Complete Reference

 

\*\*All templates and data:\*\* \`REFERENCE\_DATA.md\`

\*\*Full spec:\*\* \`ONBOARDING\_WORKFLOW\_SPEC.md\` (read second)

\*\*This file:\*\* Read FIRST for latest changes\!

 

\---

 

\#\# 🚀 Ready to Build

 

Claude Code should:

1\. Read this file first

2\. Read REFERENCE\_DATA.md

3\. Read ONBOARDING\_WORKFLOW\_SPEC.md

4\. Ask Finn for:

   \- Google Sheets ID

   \- MMS Bearer token

   \- Confirmation on vault path (\`./vault\` okay?)

5\. Build it\!

 

\*\*Estimated time:\*\* 4-6 hours

\*\*Priority:\*\* WGCS onboarding first, other features later  
