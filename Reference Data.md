\# First Chord Brain \- Reference Data

 

\*\*Last updated:\*\* 2024-12-14

\*\*Purpose:\*\* Complete reference for all templates, pricing, and configuration

 

\---

 

\#\# 💰 Pricing Structure

 

\*\*Standard onboarding:\*\* 30 minutes, £25/month (this is the default)

 

\*\*All pricing:\*\*

\- \*\*30 mins\*\*: £25/month (individual)

\- \*\*45 mins\*\*: £33/month (individual) OR £20/person (groups, max 3 students)

\- \*\*60 mins\*\*: £41.50/month (individual)

 

\*\*Stripe payment link (same for all):\*\*

\`\`\`

https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A

\`\`\`

 

\*\*Note:\*\* When onboarding, we "pretty much always" start with 30 mins, so default to £25.

 

\---

 

\#\# 📧 Message Templates

 

\#\#\# Template 1: Welcome Message (Post-Trial Confirmation)

 

\*\*When to use:\*\* After trial lesson, confirming enrollment

 

\*\*Variables:\*\*

\- \`{NAME}\` \- Parent/guardian name

\- \`{STUDENT}\` \- Student name

\- \`{TIME}\` \- Lesson time (e.g., "4pm")

\- \`{DAY}\` \- Day of week (e.g., "Tuesday")

\- \`{DATE}\` \- Date (e.g., "17th December")

\- \`{TUTOR}\` \- Teacher name

\- \`{AGE}\` \- Student age

\- \`{EXPERIENCE\_LEVEL}\` \- "a complete beginner" / "has some experience" / "at an intermediate level"

\- \`{GENRES}\` \- Musical interests/genres

 

\*\*Template:\*\*

\`\`\`

Hey {NAME}, we've got {STUDENT} down for {TIME} on {DAY} {DATE} with {TUTOR}. ✨🎶

 

To give {TUTOR} some context, {STUDENT} is {AGE} and {EXPERIENCE\_LEVEL}. They love {GENRES}\!

 

📍The school is inside CC Music Shop at 33 Otago Street G12 8JJ. Just take a seat on the couch by the door when you arrive and {TUTOR} will come meet you.

 

Below is the payment link for your lessons, please note that your first payment confirms the lesson slot, for next week.🚨Please let us know when you have done this\!

 

I'll also include a link to our welcome handbook which has more details about our teaching approach, homework, cancellation policies and more. 📖

 

Feel free to pop down any questions you have and one of us will be sure to get back to you\!

 

Cheers\! 😃

 

https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A

 

firstchord.co.uk/handbook

\`\`\`

 

\---

 

\#\#\# Template 2: Soundslice Follow-Up

 

\*\*When to use:\*\* Immediately after welcome message

 

\*\*Variables:\*\*

\- \`{STUDENT}\` \- Student name

\- \`{TUTOR}\` \- Teacher name

 

\*\*Template:\*\*

\`\`\`

Oo one last important thing to do. If you could head to soundslice.com and make a free account, then head to soundslice.com/coursecode and pop in this code \*tnc aux 3x3\* that will make a folder that {STUDENT} can access and {TUTOR} can put in all the songs they are learning 💥

\`\`\`

 

\*\*Soundslice code:\*\* \`tnc aux 3x3\`

 

\---

 

\#\#\# Template 3: Missed Call / Initial Inquiry

 

\*\*When to use:\*\* When prospect doesn't answer initial call

 

\*\*Variables:\*\*

\- \`{NAME}\` \- Parent/guardian name

 

\*\*Template:\*\*

\`\`\`

Hey {NAME}\! Thanks much for your interest in First Chord Music School\! We are excited to get a chat with you sort you out with a first lesson\! 😃

 

Let's organise a call to chat about your musical interests and goals so we can match you with the perfect tutor. Could you let us know which of these times works for you for a welcome call? 📱

 

Our Welcome Call Times:

• Mondays: 12:00-1:30pm

• Fridays: 12:00-1:30pm

• Sundays: 10:00-11:00am

 

Just let us know which day and time slot works best, and either Finn or Tom will give you a call then\! We're aiming to get you started with lessons right away or schedule you in for August.

 

Feel free to pop down any questions you have, and one of us will be sure to get back to you\!

 

As we're now working through our waiting list, please do let us know as soon as possible when you'd like your welcome call so we can prioritize getting you sorted.

 

I'll also include a link to our welcome handbook which has more details about our teaching approach, homework, cancellation policies and more. 📖

 

firstchord.co.uk/handbook

 

We can't wait to chat soon and get your musical journey started\! 🎸🎹🥁

 

Cheers\!

Finn & Tom

First Chord Music School

\`\`\`

 

\---

 

\#\# 🏫 School Information

 

\*\*Address (always the same):\*\*

\`\`\`

33 Otago Street

Glasgow G12 8JJ

\`\`\`

 

\*\*Location details:\*\*

"Inside CC Music Shop. Just take a seat on the couch by the door when you arrive."

 

\*\*Handbook link (always the same):\*\*

\`\`\`

firstchord.co.uk/handbook

\`\`\`

 

\*\*Soundslice:\*\*

\- Website: soundslice.com

\- Course code page: soundslice.com/coursecode

\- First Chord code: \`tnc aux 3x3\`

 

\---

 

\#\# 📞 Welcome Call Schedule

 

\*\*Available times for initial prospect calls:\*\*

\- \*\*Mondays:\*\* 12:00-1:30pm

\- \*\*Fridays:\*\* 12:00-1:30pm

\- \*\*Sundays:\*\* 10:00-11:00am

 

\*\*Who does calls:\*\* Finn or Tom (business partners)

 

\---

 

\#\# 👥 Tutor Information

 

\*\*Source:\*\* Pull from Google Sheets "Tutors" tab

 

\*\*Sheet structure:\*\*

\- TutorName

\- ShortName

\- TeacherID

\- HourlyRate

\- DefaultInstrument

\- Active (true/false)

\- Email

 

\*\*How to keep relevant:\*\*

\- Read from Google Sheets (source of truth)

\- Cache for 5 minutes (like dashboard does)

\- Show active tutors only during onboarding

\- Suggest based on DefaultInstrument match

 

\*\*Example smart suggestion:\*\*

\`\`\`

User selects: Piano

Brain suggests: "Emma teaches piano and is active. Use Emma? (y/other)"

\`\`\`

 

\---

 

\#\# 🎓 Student Information Patterns

 

\*\*Age ranges (common):\*\*

\- Under 8

\- 8-12 (most common)

\- 13-17

\- Adult (18+)

 

\*\*Experience levels (standardized):\*\*

\- \*\*"a complete beginner"\*\* \- Never played before

\- \*\*"has some experience"\*\* \- 1-2 years, some lessons

\- \*\*"at an intermediate level"\*\* \- 3+ years, can read music

 

\*\*Common genres/interests:\*\*

\- Pop music / Taylor Swift

\- Rock / Guitar rock

\- Classical

\- Jazz

\- Film music / Disney

\- Video game music

 

\---

 

\#\# 🗓️ Scheduling Patterns

 

\*\*Default onboarding:\*\*

\- Duration: 30 minutes

\- Price: £25/month

 

\*\*Common trial lesson times:\*\*

\- Tuesday 4pm

\- Thursday 4pm

\- Saturday morning (popular for kids)

 

\*\*When asked for date:\*\*

\- Default to next available Tuesday/Thursday

\- Format: "Tuesday 17th December" or "Dec 17"

 

\---

 

\#\# 🔧 API Configuration

 

\*\*MyMusicStaff:\*\*

\- Base URL: \`https://api.mymusicstaff.com/v1\`

\- School ID: \`sch\_Fx5JQ\`

\- Auth: Bearer token (JWT) \- stored in .env

\- Source: Copy from dashboard \`lib/mms-client.js\` line 9-10

 

\*\*Google Sheets:\*\*

\- Spreadsheet ID: \[TO BE PROVIDED\]

\- Service account: \`./secrets/google-service-account.json\`

\- Sheets:

  \- Students (row 177+)

  \- Tutors (for teacher info)

  \- Instruments

  \- Config

 

\*\*Stripe:\*\*

\- Payment link: https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A (same for all)

\- API key: \[TO BE PROVIDED\]

\- Default subscription: £25/month (30 min lessons)

 

\---

 

\#\# 📂 Obsidian Vault Structure

 

\*\*Location:\*\* NEW vault to be created by Claude Code

 

\*\*Suggested path:\*\* \`./vault\` (inside first-chord-brain repo)

 

\*\*Structure:\*\*

\`\`\`

vault/

├── Onboarding/                 \# Auto-generated onboarding records

│   └── YYYY-MM-DD-student-name.md

│

├── Students/                   \# Student profiles (future)

│

├── Meetings/                   \# Weekly meeting notes (future)

│   ├── Monday/

│   ├── Wednesday/

│   └── Friday/

│

├── Projects/                   \# Active projects (creative corner, etc)

│

├── Templates/                  \# Reference templates

│   ├── Welcome-Message.md

│   ├── Soundslice-Setup.md

│   └── Missed-Call-Response.md

│

└── Reference/                  \# This file and other reference data

    └── Pricing-and-Templates.md

\`\`\`

 

\*\*Note:\*\* Claude Code should create this vault structure fresh, not use an existing Obsidian vault.

 

\---

 

\#\# 🎯 Default Behaviors

 

\*\*When onboarding a student, default to:\*\*

1\. Lesson duration: 30 minutes

2\. Price: £25/month

3\. Tutor: Suggest based on instrument from Google Sheets

4\. Experience: "a complete beginner" (most common)

5\. Genre: Ask user (varies too much)

 

\*\*Smart suggestions:\*\*

\- If instrument \= Piano → suggest tutors where DefaultInstrument \= Piano

\- If age \< 12 → might suggest Saturday morning slots

\- If user types "beginner" → use "a complete beginner"

\- If user types "some" → use "has some experience"

 

\---

 

\#\# 💡 Implementation Notes

 

\*\*For Claude Code:\*\*

 

1\. \*\*Template generation:\*\* Use \`src/utils/message\_templates.py\`

   \- Function: \`generate\_welcome\_message()\`

   \- Function: \`generate\_soundslice\_followup()\`

   \- Function: \`generate\_missed\_call\_message()\`

 

2\. \*\*Pricing:\*\* Hard-code for now

   \- Default: £25 (30 min)

   \- Can add prompts for 45min/60min later

   \- Stripe link is same for all

 

3\. \*\*Tutor info:\*\* Pull from Google Sheets Tutors tab

   \- Cache for 5 minutes

   \- Filter: Active \= true

   \- Match: DefaultInstrument \= selected instrument

   \- Show: TutorName, DefaultInstrument

 

4\. \*\*Soundslice:\*\* Send follow-up automatically after welcome message

   \- Same code for everyone: \`tnc aux 3x3\`

   \- Format message with student/tutor names

 

5\. \*\*Vault creation:\*\*

   \- Create \`./vault\` directory structure

   \- Initialize with README explaining structure

   \- Auto-generate onboarding records to \`Onboarding/\` folder

 

\---

 

\#\# ✅ Checklist for Claude Code

 

Before implementing WGCS workflow, ensure:

 

\- \[ \] This reference file is read and understood

\- \[ \] Vault structure is created at \`./vault/\`

\- \[ \] Welcome message template matches exactly (including emojis\!)

\- \[ \] Soundslice follow-up is sent after welcome message

\- \[ \] Default to 30 min / £25 for all onboardings

\- \[ \] Tutor suggestions pull from Google Sheets

\- \[ \] Payment link is: https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A

\- \[ \] Experience level phrases match exactly ("a complete beginner", etc.)

 

\---

 

\*\*This file should be the single source of truth for all templates and reference data.\*\*  
