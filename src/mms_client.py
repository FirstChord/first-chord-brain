"""
MyMusicStaff (MMS) Client
Handles creating lessons in the MMS calendar
"""

import hashlib
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MMSClient:
    def __init__(self):
        self.base_url = os.getenv('MMS_BASE_URL')
        self.school_id = os.getenv('MMS_SCHOOL_ID')
        self.bearer_token = os.getenv('MMS_BEARER_TOKEN')

        # Complete teacher database — single source of truth for Brain
        # Format: short_name -> {full_name, teacher_id, fc_tutor_id, instruments}
        # fc_tutor_id is deterministic: sha256(teacher_id)[:8]
        # To add a new tutor: add entry here and run `npm run generate-configs` on dashboard.
        self.teachers = {
            'Arion': {
                'full_name': 'Arion Xenos',
                'teacher_id': 'tch_zplpJw',
                'instruments': ['guitar', 'piano']
            },
            'Calum': {
                'full_name': 'Calum Steel',
                'teacher_id': 'tch_zMX5Jc',
                'instruments': ['guitar']
            },
            'Chloe': {
                'full_name': 'Chloe Mak',
                'teacher_id': 'tch_zQbNJk',
                'instruments': ['guitar', 'piano']
            },
            'David': {
                'full_name': 'David Husz',
                'teacher_id': 'tch_z2j2Jf',
                'instruments': ['guitar', 'piano']
            },
            'Dean': {
                'full_name': 'Dean Louden',
                'teacher_id': 'tch_zV9TJN',
                'instruments': ['guitar', 'bass']
            },
            'Eléna': {
                'full_name': 'Eléna Esposito',
                'teacher_id': 'tch_zpy4J9',
                'instruments': ['piano']
            },
            'Fennella': {
                'full_name': 'Fennella McCallum',
                'teacher_id': 'tch_C2bJ9',
                'instruments': ['singing', 'piano']
            },
            'Finn': {
                'full_name': 'Finn Le Marinel',
                'teacher_id': 'tch_QhxJJ',
                'instruments': ['guitar', 'bass', 'ukulele']
            },
            'Ines': {
                'full_name': 'Ines Alban Zapata Peréz',
                'teacher_id': 'tch_zHJlJx',
                'instruments': ['piano']
            },
            'Kenny': {
                'full_name': 'Kenny Bates',
                'teacher_id': 'tch_zsyfJr',
                'instruments': ['guitar']
            },
            'Kim': {
                'full_name': 'Kim Grant',
                'teacher_id': 'tch_zVg1Js',
                'instruments': ['guitar']
            },
            'Patrick': {
                'full_name': 'Patrick Shand',
                'teacher_id': 'tch_zw9SJ3',
                'instruments': ['guitar', 'piano']
            },
            'Robbie': {
                'full_name': 'Robbie Tranter',
                'teacher_id': 'tch_zV9hJ2',
                'instruments': ['guitar', 'bass']
            },
            'Scott': {
                'full_name': 'Scott Brice',
                'teacher_id': 'tch_zMWrJR',
                'instruments': ['guitar']
            },
            'Stef': {
                'full_name': 'Stef McGlinchey',
                'teacher_id': 'tch_z5YmJX',
                'instruments': ['guitar']
            },
            'Tom': {
                'full_name': 'Tom Walters',
                'teacher_id': 'tch_mYJJR',
                'instruments': ['guitar', 'bass']
            },
        }

        # Enrich each teacher with their canonical FC tutor ID
        # fc_tut_XXXXXXXX is deterministic from MMS teacher_id
        for info in self.teachers.values():
            h = hashlib.sha256(info['teacher_id'].encode()).hexdigest()[:8]
            info['fc_tutor_id'] = f"fc_tut_{h}"

        # Create reverse lookup dictionary for teacher IDs
        # Maps both short names and full names to teacher IDs
        self.teacher_ids = {}
        for short_name, info in self.teachers.items():
            self.teacher_ids[short_name] = info['teacher_id']
            self.teacher_ids[info['full_name']] = info['teacher_id']

    def get_teacher_id(self, tutor_name):
        """Get MMS teacher ID from tutor name"""
        return self.teacher_ids.get(tutor_name, None)

    def get_tutors_for_instrument(self, instrument):
        """
        Get list of tutors who teach a specific instrument

        Args:
            instrument: Instrument name (e.g., 'guitar', 'piano', 'bass')

        Returns:
            List of tutor dictionaries with short_name, full_name, teacher_id
        """
        instrument = instrument.lower().strip()
        matching_tutors = []

        for short_name, info in self.teachers.items():
            if instrument in [i.lower() for i in info['instruments']]:
                matching_tutors.append({
                    'short_name': short_name,
                    'full_name': info['full_name'],
                    'teacher_id': info['teacher_id'],
                    'fc_tutor_id': info['fc_tutor_id'],
                    'instruments': info['instruments']
                })

        return matching_tutors

    def get_all_tutors(self):
        """
        Get complete list of all tutors

        Returns:
            List of all tutor dictionaries
        """
        all_tutors = []
        for short_name, info in self.teachers.items():
            all_tutors.append({
                'short_name': short_name,
                'full_name': info['full_name'],
                'teacher_id': info['teacher_id'],
                'fc_tutor_id': info['fc_tutor_id'],
                'instruments': info['instruments']
            })
        return all_tutors

    def get_waiting_students(self, max_age_days=120):
        """
        Fetch students with 'Waiting' status from MMS, ordered most recent first.
        Students added more than max_age_days ago are excluded (default 4 months).
        Returns a list of student dicts with name, mms_id, date_started, and family info.
        """
        from datetime import datetime, timedelta

        endpoint = 'https://api.mymusicstaff.com/v1/search/students'
        params = {
            'offset': 0,
            'limit': 100,
            'fields': 'Family',
            'orderby': '-DateStarted'
        }
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'x-schoolbox-version': 'main'
        }
        payload = {
            'IDs': [],
            'SearchText': '',
            'FirstName': None,
            'LastName': None,
            'EmailAddress': None,
            'Statuses': ['Waiting'],
            'StudentGroupIDs': [],
            'TeacherIDs': [],
            'FamilyIDs': []
        }

        cutoff = datetime.now() - timedelta(days=max_age_days)

        try:
            response = requests.post(endpoint, params=params, json=payload, headers=headers)
            if not response.ok:
                return {'success': False, 'error': f'{response.status_code}: {response.text}'}

            data = response.json()
            students_raw = data.get('ItemSubset', [])

            students = []
            for s in students_raw:
                # Parse DateStarted
                date_started = None
                date_str = s.get('DateStarted', '')
                if date_str:
                    try:
                        date_started = datetime.fromisoformat(date_str.replace('Z', ''))
                    except ValueError:
                        pass

                # Skip entries older than max_age_days
                if date_started and date_started < cutoff:
                    continue

                family = s.get('Family') or {}
                parents = family.get('Parents') or []
                parent = parents[0] if parents else {}
                parent_email_obj = parent.get('Email') or {}

                students.append({
                    'mms_id':          s.get('ID', ''),
                    'first_name':      s.get('FirstName', ''),
                    'last_name':       s.get('LastName', ''),
                    'full_name':       f"{s.get('FirstName','')} {s.get('LastName','')}".strip(),
                    'date_started':    date_started,
                    'parent_forename': parent.get('FirstName', ''),
                    'parent_surname':  parent.get('LastName', ''),
                    'parent_name':     parent.get('FormalName', ''),
                    'parent_email':    parent_email_obj.get('EmailAddress', ''),
                })

            return {'success': True, 'students': students}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_student_details(self, mms_id):
        """
        Fetch full student record from MMS including the Note field,
        which contains sign-up form submission data (instrument, age,
        experience, genres, songs).

        Returns a dict with keys:
            success, status, date_started, note, email, telephone, parsed

        'parsed' is the output of _parse_note_fields() — a dict with any
        of: instrument, age, experience, genres, songs.
        """
        endpoint = f'https://api.mymusicstaff.com/v1/students/{mms_id}'
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'x-schoolbox-version': 'main'
        }
        try:
            r = requests.get(endpoint, headers=headers)
            if not r.ok:
                return {'success': False, 'error': f'{r.status_code}: {r.text}'}

            data = r.json()
            email_obj  = data.get('Email')     or {}
            tel_obj    = data.get('Telephone') or {}
            note       = data.get('Note', '') or ''

            return {
                'success':      True,
                'status':       data.get('Status', ''),
                'date_started': data.get('DateStarted', ''),
                'note':         note,
                'email':        email_obj.get('EmailAddress', ''),
                'telephone':    tel_obj.get('TelephoneNumber', ''),
                'parsed':       self._parse_note_fields(note),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _parse_note_fields(self, note_text):
        """
        Parse the structured sign-up form data embedded in MMS student Notes.

        The form generates lines like:
            Students Age: 21
            What instruments are they interested in learning?: Piano & Keyboard
            Do they already have some music background/experience?: No
            Favourite genres of music?: Classical
            Which song(s) would you love to learn?: Moonlight Sonata

        Returns a dict with any of: instrument, age, experience, genres, songs.
        Values of '(Not Provided)' / blank are omitted.
        """
        if not note_text:
            return {}

        SKIP = {'(not provided)', '(not available)', 'not provided', 'n/a', ''}
        result = {}

        for line in note_text.split('\n'):
            line = line.strip()
            if ':' not in line:
                continue

            key_raw, _, value = line.partition(':')
            key   = key_raw.strip().lower()
            value = value.strip()

            if value.lower().strip('()') in SKIP:
                continue

            if 'instrument' in key:
                result['instrument'] = value
            elif 'age' in key and 'students' in key:
                result['age'] = value
            elif 'background' in key or ('experience' in key and 'music' in key):
                result['experience'] = value   # "Yes" or "No"
            elif 'genre' in key:
                result['genres'] = value
            elif 'song' in key:
                result['songs'] = value

        return result

    def create_lesson(self, student_name, tutor_name, lesson_date, lesson_time, duration_minutes=30):
        """
        Create a lesson in MMS calendar

        Args:
            student_name: Student's full name
            tutor_name: Tutor's name
            lesson_date: Date string (e.g., "Dec 17, 2024")
            lesson_time: Time string (e.g., "4pm")
            duration_minutes: Lesson duration in minutes (default: 30)

        Returns:
            Dictionary with success status and lesson details
        """
        teacher_id = self.get_teacher_id(tutor_name)
        if not teacher_id:
            return {
                'success': False,
                'error': f'No teacher ID found for {tutor_name}'
            }

        # Parse the date and time
        # This is a simplified version - you may need to improve date parsing
        try:
            # Convert "Dec 17, 2024" and "4pm" to ISO datetime
            # For now, this is a placeholder
            # You'll need proper date/time parsing logic
            lesson_datetime = self._parse_datetime(lesson_date, lesson_time)
        except Exception as e:
            return {
                'success': False,
                'error': f'Could not parse date/time: {e}'
            }

        # Make API request to create lesson
        endpoint = f'{self.base_url}/events'
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'x-schoolbox-version': 'main'
        }

        payload = {
            'SchoolID': self.school_id,
            'TeacherID': teacher_id,
            'StudentName': student_name,
            'EventStartDate': lesson_datetime,
            'EventDuration': duration_minutes,
            'Category': 'First Lesson ⚡',
            'Subject': 'Lesson',
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers)

            if response.ok:
                return {
                    'success': True,
                    'lesson_id': response.json().get('ID'),
                    'datetime': lesson_datetime
                }
            else:
                return {
                    'success': False,
                    'error': f'MMS API error: {response.status_code} - {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Request failed: {e}'
            }

    def _parse_datetime(self, date_str, time_str):
        """
        Parse date and time strings into ISO format

        Args:
            date_str: e.g., "Dec 17, 2024" or "17th December"
            time_str: e.g., "4pm" or "16:00"

        Returns:
            ISO datetime string
        """
        # This is a simplified parser
        # You may want to use dateutil.parser for more robust parsing
        from datetime import datetime

        # Remove ordinal suffixes (st, nd, rd, th)
        date_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')

        # Try different date formats
        date_formats = [
            '%b %d, %Y',      # Dec 17, 2024
            '%d %B',          # 17 December
            '%B %d',          # December 17
        ]

        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                # If year is missing, use current year
                if parsed_date.year == 1900:
                    parsed_date = parsed_date.replace(year=datetime.now().year)
                break
            except ValueError:
                continue

        if not parsed_date:
            raise ValueError(f'Could not parse date: {date_str}')

        # Parse time
        time_str = time_str.lower().strip()
        if 'pm' in time_str or 'am' in time_str:
            hour = int(time_str.replace('pm', '').replace('am', '').strip())
            if 'pm' in time_str and hour != 12:
                hour += 12
            elif 'am' in time_str and hour == 12:
                hour = 0
            minute = 0
        else:
            # 24-hour format
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0

        # Combine date and time
        lesson_datetime = parsed_date.replace(hour=hour, minute=minute)

        # Return ISO format
        return lesson_datetime.isoformat()
