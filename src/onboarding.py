"""
Student Onboarding Workflow
Implements the 6-step WGCS onboarding process
"""

import hashlib
import pyperclip
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from .sheets_client import SheetsClient
from .mms_client import MMSClient
from .templates import generate_welcome_message, generate_soundslice_followup, normalize_experience_level

console = Console()

class OnboardingWorkflow:
    def __init__(self):
        self.sheets = SheetsClient()
        self.mms = MMSClient()
        self.student_data = {}

    def start(self, student_name):
        """Start the onboarding workflow"""
        console.print("\n")

        # Offer waiting-list picker first — pre-fills name, MMS ID, parent info
        self._pick_waiting_student()

        # Resolve name: prefer waiting-list selection over CLI argument
        if not self.student_data.get('name'):
            if not student_name:
                student_name = Prompt.ask("Student name")
            self.student_data['name'] = student_name

        resolved_name = self.student_data['name']

        console.print(Panel.fit(
            f"🎵 STUDENT ONBOARDING: {resolved_name}",
            border_style="blue"
        ))
        console.print("\n")

        # Collect information
        self._collect_lesson_details()
        self._select_tutor()
        self._collect_student_info()

        # Confirm before proceeding
        console.print("\n")
        if not Confirm.ask("Ready to start onboarding?"):
            console.print("[yellow]Onboarding cancelled[/yellow]")
            return

        # Execute WGCS steps (now 5 steps)
        console.print("\n")
        self._step_1_whatsapp_group()
        self._step_2_google_sheets()
        self._step_3_mms_calendar()
        self._step_4_welcome_soundslice()
        self._step_5_community_whatsapp()

        # Save to vault
        self._save_to_vault()

        # Show completion
        self._show_completion()

        # Regenerate FC identity layer so new student is immediately visible
        self._regenerate_fc_layer()

        # Add to dashboard registry and deploy
        self._update_dashboard_registry()

    @staticmethod
    def _generate_fc_student_id(student_forename: str, student_surname: str, email: str) -> str:
        """
        Generate a deterministic FC student ID from name and email.
        Format: fc_std_XXXXXXXX (8 hex chars)
        This ID is assigned at onboarding and is stable even before MMS ID is known.
        When the MMS ID is later assigned, link it via FC_External_IDs.
        """
        seed = f"{student_forename.strip().lower()}:{student_surname.strip().lower()}:{email.strip().lower()}"
        return f"fc_std_{hashlib.sha256(seed.encode()).hexdigest()[:8]}"

    def _pick_waiting_student(self):
        """
        Fetch MMS waiting students and let user pick one to pre-fill onboarding.
        Pre-fills: name, MMS ID, parent name/email. Returns True if selected.
        """
        from rich.table import Table as RichTable

        console.print("[bold cyan]Fetching waiting students from MMS...[/bold cyan]")
        result = self.mms.get_waiting_students()

        if not result['success']:
            console.print(f"[yellow]Could not fetch waiting students: {result['error']}[/yellow]")
            console.print("[dim]Proceeding with manual entry[/dim]\n")
            return False

        students = result['students']
        if not students:
            console.print("[yellow]No waiting students found — entering manually[/yellow]\n")
            return False

        table = RichTable(show_header=True, header_style="bold cyan", box=None)
        table.add_column("#", style="dim", width=3)
        table.add_column("Student", min_width=22)
        table.add_column("Parent", min_width=22)
        table.add_column("Email", min_width=28, overflow="fold")

        for i, s in enumerate(students, 1):
            table.add_row(str(i), s['full_name'], s['parent_name'], s['parent_email'])

        console.print(table)
        console.print("[dim]Enter a number to select a waiting student, or 0 to enter manually[/dim]")

        valid = [str(i) for i in range(0, len(students) + 1)]
        choice = Prompt.ask("Select student", choices=valid, default='0')

        if choice == '0':
            console.print()
            return False

        s = students[int(choice) - 1]
        self.student_data['name'] = s['full_name']
        self.student_data['student_forename'] = s['first_name']
        self.student_data['student_surname'] = s['last_name']
        self.student_data['mms_id'] = s['mms_id']
        self.student_data['parent_name'] = s['parent_name']
        self.student_data['parent_forename'] = s['parent_forename']
        self.student_data['parent_surname'] = s['parent_surname']
        self.student_data['parent_email'] = s['parent_email']
        self.student_data['_from_waiting_list'] = True

        console.print(f"[green]✓ Selected:[/green] {s['full_name']} [dim](MMS: {s['mms_id']})[/dim]\n")
        return True

    def _collect_lesson_details(self):
        """Collect lesson day, time, and date"""
        console.print("[bold cyan]Lesson details:[/bold cyan]")

        self.student_data['instrument'] = Prompt.ask("Instrument", default="Piano")
        self.student_data['lesson_length'] = Prompt.ask("Lesson length (mins)", default="30")
        self.student_data['day'] = Prompt.ask("Day", default="Tuesday")
        self.student_data['time'] = Prompt.ask("Time", default="4pm")
        self.student_data['date'] = Prompt.ask("Date", default="Dec 17")

        # Confirm
        console.print(f"\n[green]✓[/green] {self.student_data['day']} at {self.student_data['time']} on {self.student_data['date']}")

    def _select_tutor(self):
        """Select tutor based on instrument"""
        console.print("\n[bold cyan]Selecting tutor...[/bold cyan]")

        # Get tutors for the instrument from MMS client
        tutors = self.mms.get_tutors_for_instrument(self.student_data['instrument'])

        if tutors:
            # Show all matching tutors
            if len(tutors) == 1:
                suggested_tutor = tutors[0]
                console.print(f"[yellow]Suggestion:[/yellow] {suggested_tutor['short_name']} teaches {self.student_data['instrument']}")

                if Confirm.ask(f"Use {suggested_tutor['short_name']}?", default=True):
                    self.student_data['tutor'] = suggested_tutor['full_name']
                    self.student_data['tutor_short'] = suggested_tutor['short_name']
                    self.student_data['fc_tutor_id'] = suggested_tutor.get('fc_tutor_id', '')
                else:
                    self._manual_tutor_selection()
            else:
                # Multiple tutors available - show options
                console.print(f"\n[yellow]{len(tutors)} tutors teach {self.student_data['instrument']}:[/yellow]")
                for i, tutor in enumerate(tutors, 1):
                    instruments_str = ", ".join(tutor['instruments'])
                    console.print(f"  {i}. {tutor['short_name']} ({tutor['full_name']}) - {instruments_str}")

                choice = Prompt.ask(
                    "Choose tutor",
                    choices=[str(i) for i in range(1, len(tutors) + 1)] + ['other'],
                    default='1'
                )

                if choice == 'other':
                    self._manual_tutor_selection()
                else:
                    selected_tutor = tutors[int(choice) - 1]
                    self.student_data['tutor'] = selected_tutor['full_name']
                    self.student_data['tutor_short'] = selected_tutor['short_name']
                    self.student_data['fc_tutor_id'] = selected_tutor.get('fc_tutor_id', '')
        else:
            console.print(f"[yellow]No tutors found for {self.student_data['instrument']}[/yellow]")
            console.print("[dim]Available instruments: guitar, piano, bass, singing, ukulele[/dim]")
            self._manual_tutor_selection()

        console.print(f"[green]✓[/green] Tutor: {self.student_data['tutor_short']} ({self.student_data['tutor']})")

    def _manual_tutor_selection(self):
        """Manually select tutor from full list"""
        all_tutors = self.mms.get_all_tutors()

        console.print("\n[bold cyan]All tutors:[/bold cyan]")
        for i, tutor in enumerate(all_tutors, 1):
            instruments_str = ", ".join(tutor['instruments'])
            console.print(f"  {i}. {tutor['short_name']} - {instruments_str}")

        choice = Prompt.ask(
            "Choose tutor number",
            choices=[str(i) for i in range(1, len(all_tutors) + 1)],
            default='1'
        )

        selected_tutor = all_tutors[int(choice) - 1]
        self.student_data['tutor'] = selected_tutor['full_name']
        self.student_data['tutor_short'] = selected_tutor['short_name']
        self.student_data['fc_tutor_id'] = selected_tutor.get('fc_tutor_id', '')

    def _collect_student_info(self):
        """Collect student information for welcome message"""
        console.print("\n[bold cyan]Student information:[/bold cyan]")

        from_waiting = self.student_data.get('_from_waiting_list', False)
        if from_waiting:
            console.print("[dim]Pre-filled from MMS waiting list — press Enter to accept, or type to override[/dim]")

        # Adult or child?
        is_adult = Confirm.ask("Is this student an adult?", default=False)
        self.student_data['is_adult'] = is_adult

        # Student name — fall back to splitting the full name if not already split
        name_parts = self.student_data.get('name', '').strip().split()
        fallback_forename = name_parts[0] if name_parts else ''
        fallback_surname = ' '.join(name_parts[1:]) if len(name_parts) >= 2 else ''

        self.student_data['student_forename'] = Prompt.ask(
            "Student first name",
            default=self.student_data.get('student_forename') or fallback_forename
        )
        self.student_data['student_surname'] = Prompt.ask(
            "Student surname",
            default=self.student_data.get('student_surname') or fallback_surname
        )

        if is_adult:
            # Adult: message goes directly to them, no parent fields needed
            self.student_data['parent_name'] = f"{self.student_data['student_forename']} {self.student_data['student_surname']}"
            self.student_data['parent_forename'] = self.student_data['student_forename']
            self.student_data['parent_surname'] = self.student_data['student_surname']
            self.student_data['parent_email'] = Prompt.ask(
                "Student email",
                default=self.student_data.get('parent_email', '')
            )
            self.student_data['age'] = None
        else:
            # Child: collect parent information
            self.student_data['parent_name'] = Prompt.ask(
                "Parent full name",
                default=self.student_data.get('parent_name', '')
            )

            # Re-split in case user edited the name
            parent_parts = self.student_data['parent_name'].strip().split()
            if len(parent_parts) >= 2:
                self.student_data['parent_forename'] = parent_parts[0]
                self.student_data['parent_surname'] = ' '.join(parent_parts[1:])
            else:
                self.student_data['parent_forename'] = parent_parts[0] if parent_parts else ''
                self.student_data['parent_surname'] = ''

            self.student_data['parent_email'] = Prompt.ask(
                "Parent email",
                default=self.student_data.get('parent_email', '')
            )

            self.student_data['age'] = Prompt.ask("Student age")

        # Experience level with choices
        console.print("\nExperience level:")
        console.print("  1. Complete beginner")
        console.print("  2. Some experience (1-2 years)")
        console.print("  3. Intermediate (3+ years)")

        exp_choice = Prompt.ask("Choice", choices=['1', '2', '3'], default='1')
        exp_map = {
            '1': 'a complete beginner',
            '2': 'has some experience',
            '3': 'at an intermediate level'
        }
        self.student_data['experience_level'] = exp_map[exp_choice]

        self.student_data['interests'] = Prompt.ask(
            f"What does {self.student_data['name']} love?",
            default="Pop music"
        )

        # Get unique Soundslice code for this student
        self.student_data['soundslice_code'] = Prompt.ask(
            "\nSoundslice course code (for welcome message)",
            default="tnc aux 3x3"
        )

        # Get Soundslice course ID or URL for spreadsheet
        soundslice_input = Prompt.ask(
            "Soundslice course ID or URL (for spreadsheet)",
            default=""
        )

        # Convert to URL if just an ID was provided
        if soundslice_input and not soundslice_input.startswith('http'):
            self.student_data['soundslice_url'] = f"https://www.soundslice.com/courses/{soundslice_input}/"
        else:
            self.student_data['soundslice_url'] = soundslice_input

        # Generate Theta username (firstname + fc)
        suggested_theta = self.student_data['student_forename'].lower() + 'fc'
        self.student_data['theta_username'] = Prompt.ask(
            "Theta username",
            default=suggested_theta
        )

        # MMS student ID — already set if picked from waiting list
        if self.student_data.get('mms_id'):
            console.print(f"\n[green]✓ MMS ID:[/green] {self.student_data['mms_id']} [dim](from MMS waiting list)[/dim]")
        else:
            mms_raw = Prompt.ask(
                "\nMMS student ID [dim](e.g. sdt_2grxJL — press Enter to skip if not yet created)[/dim]",
                default=""
            ).strip()
            self.student_data['mms_id'] = mms_raw if mms_raw.startswith("sdt_") else ""
            if mms_raw and not mms_raw.startswith("sdt_"):
                console.print("[yellow]  MMS ID not recognised (should start with sdt_) — left blank[/yellow]")

        # Generate canonical FC student ID (assigned at onboarding, stable before MMS ID exists)
        self.student_data['fc_student_id'] = self._generate_fc_student_id(
            self.student_data['student_forename'],
            self.student_data['student_surname'],
            self.student_data['parent_email'],
        )
        console.print(f"\n[dim]FC ID: {self.student_data['fc_student_id']}[/dim]")
        if self.student_data['mms_id']:
            console.print(f"[dim]MMS ID: {self.student_data['mms_id']}[/dim]")

    def _step_1_whatsapp_group(self):
        """Step 1: WhatsApp Group (W)"""
        console.print("\n")
        console.print(Panel.fit(
            "STEP 1/5: WhatsApp Group (W)",
            border_style="magenta"
        ))

        message = f"{self.student_data['name']} - WGCS"
        console.print(f"\n[yellow]Message to send in partner WhatsApp:[/yellow]")
        console.print(f"[bold]\"{message}\"[/bold]")

        Prompt.ask("\nSend this message, then press Enter")
        console.print("[green]✅ WhatsApp group[/green]")

    def _step_2_google_sheets(self):
        """Step 2: Google Sheets (G)"""
        console.print("\n")
        console.print(Panel.fit(
            "STEP 2/5: Google Sheets (G)",
            border_style="magenta"
        ))

        console.print("\n[yellow]Adding to Students sheet...[/yellow]")
        console.print(f"  - Name: {self.student_data['student_forename']} {self.student_data['student_surname']}")
        if self.student_data.get('is_adult'):
            console.print(f"  - Email: {self.student_data['parent_email']} (student)")
        else:
            console.print(f"  - Parent: {self.student_data['parent_forename']} {self.student_data['parent_surname']}")
            console.print(f"  - Email: {self.student_data['parent_email']}")
        console.print(f"  - Instrument: {self.student_data['instrument']}")
        console.print(f"  - Teacher: {self.student_data['tutor_short']}")
        console.print(f"  - Theta: {self.student_data['theta_username']}")

        student_data_for_sheet = {
            'tutor': self.student_data['tutor'],          # full name — matches sheet format
            'tutor_short': self.student_data['tutor_short'],
            'student_surname': self.student_data['student_surname'],
            'student_forename': self.student_data['student_forename'],
            'parent_email': self.student_data['parent_email'],
            'mms_id': self.student_data.get('mms_id', ''),
            'theta_username': self.student_data['theta_username'],
            'soundslice_url': self.student_data.get('soundslice_url', ''),
            'instrument': self.student_data['instrument'],
            'parent_surname': self.student_data['parent_surname'],
            'parent_forename': self.student_data['parent_forename'],
            'fc_student_id': self.student_data.get('fc_student_id', ''),
            'lesson_length': self.student_data.get('lesson_length', ''),
        }

        row_number = self.sheets.add_student(student_data_for_sheet)

        if row_number:
            console.print(f"[green]✅ Added to row {row_number}[/green]")
            self.student_data['sheet_row'] = row_number
        else:
            console.print("[red]⚠️  Could not add to sheet (continuing anyway)[/red]")

    def _step_3_mms_calendar(self):
        """Step 3: MMS Calendar (C)"""
        console.print("\n")
        console.print(Panel.fit(
            "STEP 3/5: MMS Calendar (C)",
            border_style="magenta"
        ))

        console.print("\n[yellow]Creating first lesson in MyMusicStaff:[/yellow]")
        console.print(f"  - Student: {self.student_data['name']}")
        console.print(f"  - {self.student_data['day']} {self.student_data['date']} at {self.student_data['time']}")
        console.print(f"  - Teacher: {self.student_data['tutor']}")
        console.print(f"  - Category: First Lesson ⚡")

        result = self.mms.create_lesson(
            student_name=self.student_data['name'],
            tutor_name=self.student_data['tutor'],
            lesson_date=self.student_data['date'],
            lesson_time=self.student_data['time'],
            duration_minutes=30
        )

        if result['success']:
            console.print(f"[green]✅ Lesson created in calendar[/green]")
            self.student_data['lesson_id'] = result.get('lesson_id')
        else:
            console.print(f"[red]⚠️  Could not create lesson: {result.get('error')}[/red]")
            console.print("[yellow]Please create the lesson manually in MMS[/yellow]")

    def _step_4_welcome_soundslice(self):
        """Step 4: Welcome Message + Soundslice (S)"""
        console.print("\n")
        console.print(Panel.fit(
            "STEP 4/5: Welcome Message + Soundslice (S)",
            border_style="magenta"
        ))

        # Generate welcome message
        welcome_msg = generate_welcome_message(
            parent_name=self.student_data['parent_name'],
            student_name=self.student_data['name'],
            time=self.student_data['time'],
            day=self.student_data['day'],
            date=self.student_data['date'],
            tutor=self.student_data['tutor_short'],
            age=self.student_data['age'],
            experience_level=self.student_data['experience_level'],
            genres=self.student_data['interests'],
            is_adult=self.student_data.get('is_adult', False)
        )

        # Display message
        console.print("\n")
        console.print(Panel(
            welcome_msg,
            title="📋 WELCOME MESSAGE (ready to send)",
            border_style="green"
        ))

        # Copy to clipboard
        try:
            pyperclip.copy(welcome_msg)
            console.print("\n[green]✓ Message copied to clipboard! 📋[/green]")
        except:
            console.print("\n[yellow]⚠️  Could not copy to clipboard[/yellow]")

        Prompt.ask("\nPaste and send to parent. Done?")
        console.print("[green]✅ Welcome message sent[/green]")

        # Soundslice follow-up
        console.print("\n[bold cyan]Now sending Soundslice follow-up...[/bold cyan]\n")

        soundslice_msg = generate_soundslice_followup(
            student_name=self.student_data['name'],
            tutor=self.student_data['tutor_short'],
            soundslice_code=self.student_data['soundslice_code']
        )

        console.print(Panel(
            soundslice_msg,
            title="📋 SOUNDSLICE FOLLOW-UP",
            border_style="blue"
        ))

        try:
            pyperclip.copy(soundslice_msg)
            console.print("\n[green]✓ Message copied to clipboard! 📋[/green]")
        except:
            console.print("\n[yellow]⚠️  Could not copy to clipboard[/yellow]")

        Prompt.ask("\nPaste and send. Done?")
        console.print("[green]✅ Soundslice message sent[/green]")

    def _step_5_community_whatsapp(self):
        """Step 5: Community WhatsApp (🏘️)"""
        console.print("\n")
        console.print(Panel.fit(
            "STEP 5/5: Community WhatsApp (🏘️)",
            border_style="magenta"
        ))

        console.print(f"\nAdd {self.student_data['parent_name']} to First Chord community WhatsApp group")
        console.print("\nThen react with: 🏘️")

        Prompt.ask("\nDone?")
        console.print("[green]✅ Community WhatsApp added[/green]")

    def _save_to_vault(self):
        """Save onboarding record to vault"""
        # Create filename
        date_slug = datetime.now().strftime('%Y-%m-%d')
        name_slug = self.student_data['name'].lower().replace(' ', '-')
        filename = f"{date_slug}-{name_slug}.md"
        filepath = f"vault/Onboarding/{filename}"

        # Build age line and contact section based on adult/child
        is_adult = self.student_data.get('is_adult', False)
        age_line = "" if is_adult else f"- **Age:** {self.student_data['age']}\n"
        if is_adult:
            contact_section = f"## Contact Details\n- **Email:** {self.student_data['parent_email']}"
        else:
            contact_section = (
                f"## Parent Details\n"
                f"- **Parent Name:** {self.student_data['parent_name']}\n"
                f"- **Parent Email:** {self.student_data['parent_email']}"
            )

        # Create content
        content = f"""# {self.student_data['name']} - Onboarding Record

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status:** ✅ Complete

## Student Details
- **Name:** {self.student_data['name']}
{age_line}- **Instrument:** {self.student_data['instrument']}
- **Experience:** {self.student_data['experience_level']}
- **Interests:** {self.student_data['interests']}

## Lesson Details
- **Tutor:** {self.student_data['tutor']}
- **Day/Time:** {self.student_data['day']} at {self.student_data['time']}
- **Start Date:** {self.student_data['date']}
- **Duration:** 30 minutes
- **Price:** £25/month

{contact_section}

## Identity
- **FC Student ID:** {self.student_data.get('fc_student_id', 'not assigned')}
- **MMS Student ID:** *(to be filled when created in MMS)*

## WGCS Checklist
- [x] **W** - WhatsApp group notified
- [x] **G** - Google Sheets (row {self.student_data.get('sheet_row', 'N/A')})
- [x] **C** - MMS Calendar (lesson created)
- [x] **S** - Welcome message sent (payment link included)
- [x] **S** - Soundslice follow-up sent
- [x] **🏘️** - Community WhatsApp added

## Notes
First lesson: {self.student_data['day']} {self.student_data['date']} at {self.student_data['time']} with {self.student_data['tutor']}

Payment link: https://buy.stripe.com/fZueVea3y1b29Rb3Bo5J60A (sent in welcome message)
Soundslice code: {self.student_data['soundslice_code']}
"""

        # Save file
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            self.student_data['vault_file'] = filepath
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not save to vault: {e}[/yellow]")

    def _show_completion(self):
        """Show completion summary"""
        console.print("\n")
        console.print(Panel.fit(
            "✅ ONBOARDING COMPLETE! 🎉",
            border_style="green"
        ))

        # Create summary table
        table = Table(show_header=False, box=None)
        table.add_column("Step", style="cyan")
        table.add_column("Status", style="green")

        table.add_row("✅ W", "WhatsApp group notified")
        table.add_row("✅ G", f"Google Sheets (row {self.student_data.get('sheet_row', 'N/A')})")
        table.add_row("✅ C", f"MMS Calendar ({self.student_data['date']}, {self.student_data['time']}, {self.student_data['tutor_short']})")
        table.add_row("✅ S", f"Welcome message sent to {self.student_data['parent_name']} (payment link included)")
        table.add_row("✅ S", f"Soundslice follow-up sent (code: {self.student_data['soundslice_code']})")
        table.add_row("✅ 🏘️", "Community WhatsApp added")

        console.print("\n")
        console.print(table)
        age_str = "" if self.student_data.get('is_adult') else f", age {self.student_data['age']}"
        console.print(f"\n[bold]{self.student_data['name']} ({self.student_data['instrument']}{age_str})[/bold]")
        console.print(f"First lesson: {self.student_data['day']} {self.student_data['date']} at {self.student_data['time']} with {self.student_data['tutor']}")

        if self.student_data.get('vault_file'):
            console.print(f"\n[cyan]Saved to: {self.student_data['vault_file']}[/cyan]")

        console.print("\n")

    def _regenerate_fc_layer(self):
        """
        Regenerate the FC identity layer immediately after onboarding.
        This makes the new student visible in lookup without any manual step.
        Busts the Sheets cache first so the fresh row is picked up.
        """
        import sys
        import importlib
        from pathlib import Path

        console.print("\n")
        console.print(Panel.fit(
            "Updating FC identity layer...",
            border_style="dim"
        ))

        try:
            # Bust the Sheets cache so the new row is fetched fresh
            for cache_name in ["fc_sheets_cache.json", "fc_sheets_cache_v2.json"]:
                cache = Path("/tmp") / cache_name
                if cache.exists():
                    cache.unlink()

            # Ensure the brain root is on the path so generate_fc_ids is importable
            brain_dir = Path(__file__).parent.parent
            if str(brain_dir) not in sys.path:
                sys.path.insert(0, str(brain_dir))

            # Import (or reload if already imported in this session)
            if "generate_fc_ids" in sys.modules:
                mod = importlib.reload(sys.modules["generate_fc_ids"])
            else:
                import generate_fc_ids as mod

            mod.generate()

            name = f"{self.student_data['student_forename']} {self.student_data['student_surname']}"
            fc_id = self.student_data.get('fc_student_id', '')
            console.print(f"\n[green]✓ FC identity layer updated[/green]")
            console.print(f"  [cyan]{name}[/cyan] is now live — lookup ready")
            if fc_id:
                console.print(f"  FC ID: [dim]{fc_id}[/dim]")

        except Exception as e:
            console.print(f"\n[yellow]⚠️  FC layer update skipped: {e}[/yellow]")
            console.print("[dim]Run manually: python3 generate_fc_ids.py[/dim]")

    def _update_dashboard_registry(self):
        """Add student to dashboard students-registry.js and deploy to Railway"""
        import subprocess
        from pathlib import Path

        console.print("\n")
        console.print(Panel.fit(
            "Updating dashboard registry...",
            border_style="dim"
        ))

        mms_id = self.student_data.get('mms_id', '')
        if not mms_id:
            console.print("\n[yellow]⚠️  No MMS ID — skipping dashboard update[/yellow]")
            console.print("[dim]Once MMS ID is known, add manually via the add-student skill[/dim]")
            return

        brain_dir = Path(__file__).parent.parent
        dashboard_dir = brain_dir.parent / "music-school-dashboard"
        registry_path = dashboard_dir / "lib" / "config" / "students-registry.js"
        url_mappings_path = dashboard_dir / "lib" / "student-url-mappings.js"

        if not registry_path.exists():
            console.print(f"[red]✗ Registry not found at {registry_path}[/red]")
            return

        # Check MMS ID not already in registry
        registry_content = registry_path.read_text()
        if mms_id in registry_content:
            console.print(f"[yellow]  {mms_id} already in registry — skipping[/yellow]")
            return

        # Generate friendly URL — firstname, fall back to firstname-lastinitial
        first_name = self.student_data['student_forename'].lower()
        last_initial = self.student_data['student_surname'][0].lower() if self.student_data.get('student_surname') else ''

        friendly_url = first_name
        if url_mappings_path.exists():
            mappings_content = url_mappings_path.read_text()
            if f"'{first_name}'" in mappings_content:
                friendly_url = f"{first_name}-{last_initial}" if last_initial else first_name
                if f"'{friendly_url}'" in mappings_content:
                    friendly_url = Prompt.ask(
                        f"[yellow]'{first_name}' and '{friendly_url}' both taken. Enter unique URL slug[/yellow]",
                        default=f"{first_name}-{self.student_data['student_surname'].lower()[:4]}"
                    )

        console.print(f"  Portal URL: [cyan]/{friendly_url}[/cyan]")

        # Build the registry entry
        name = f"{self.student_data['student_forename']} {self.student_data['student_surname']}"
        tutor = self.student_data['tutor_short']
        instrument = self.student_data['instrument']
        soundslice_raw = self.student_data.get('soundslice_url', '')
        soundslice_val = f"'{soundslice_raw}'" if soundslice_raw else 'null'
        theta = self.student_data.get('theta_username', f"{first_name}fc")
        fc_id = self.student_data.get('fc_student_id', '')

        entry = (
            f"\n  '{mms_id}': {{\n"
            f"    firstName: '{self.student_data['student_forename']}',\n"
            f"    lastName: '{self.student_data['student_surname']}',\n"
            f"    friendlyUrl: '{friendly_url}',\n"
            f"    tutor: '{tutor}',\n"
            f"    instrument: '{instrument}',\n"
            f"    soundsliceUrl: {soundslice_val},\n"
            f"    thetaUsername: '{theta}',\n"
            f"    fcStudentId: '{fc_id}',\n"
            f"  }}, // {name}\n"
        )

        # Insert before the closing `};`
        if not registry_content.rstrip().endswith('};'):
            console.print("[red]✗ Could not find closing }; in registry[/red]")
            return

        updated = registry_content.rstrip()[:-2] + entry + '};\n'
        registry_path.write_text(updated)
        console.print(f"  [green]✓[/green] Added {name} to registry")

        # Regenerate config files
        console.print("  Running generate-configs...")
        result = subprocess.run(
            ['npm', 'run', 'generate-configs'],
            cwd=dashboard_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            console.print(f"[red]✗ generate-configs failed:\n{result.stderr}[/red]")
            return
        console.print("  [green]✓[/green] Configs regenerated")

        # Commit and push
        files_to_stage = [
            'lib/config/students-registry.js',
            'lib/student-url-mappings.js',
            'lib/student-helpers.js',
            'lib/soundslice-mappings.js',
            'lib/config/theta-credentials.js',
            'lib/config/instruments.js',
        ]
        subprocess.run(['git', 'add'] + files_to_stage, cwd=dashboard_dir, capture_output=True)

        commit_msg = f"feat: add {name} ({mms_id}) to {tutor}'s students"
        commit = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=dashboard_dir,
            capture_output=True,
            text=True
        )
        if commit.returncode != 0:
            console.print(f"[yellow]  Commit skipped (nothing changed or already committed)[/yellow]")
            return
        console.print(f"  [green]✓[/green] Committed")

        push = subprocess.run(
            ['git', 'push', '--set-upstream', 'origin', 'main'],
            cwd=dashboard_dir,
            capture_output=True,
            text=True
        )
        if push.returncode != 0:
            console.print(f"[red]✗ Push failed: {push.stderr}[/red]")
            return

        console.print(f"  [green]✓[/green] Pushed → Railway deploying (~2 min)")
        console.print(
            f"\n[green]✅ Dashboard:[/green] "
            f"https://efficient-sparkle-production.up.railway.app/{friendly_url}"
        )
