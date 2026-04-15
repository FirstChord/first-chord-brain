"""
Message Templates
Contains exact templates from Reference Data
"""

import os
from dotenv import load_dotenv

load_dotenv()

def generate_welcome_message(
    parent_name,
    student_name,
    time,
    day,
    date,
    tutor,
    age,
    experience_level,
    genres,
    is_adult=False
):
    """
    Generate welcome message using exact template from Reference Data

    Args:
        parent_name: Parent/guardian name (e.g., "Helen"), or student name if adult
        student_name: Student name (e.g., "Sarah")
        time: Lesson time (e.g., "4pm")
        day: Day of week (e.g., "Tuesday")
        date: Date (e.g., "17th December")
        tutor: Teacher name (e.g., "Emma")
        age: Student age (e.g., "8"), or None if adult
        experience_level: Must be one of:
            - "a complete beginner"
            - "has some experience"
            - "at an intermediate level"
        genres: Musical interests/genres (e.g., "Pop music and Taylor Swift")
        is_adult: Whether the student is an adult (default False)

    Returns:
        Formatted welcome message string
    """
    payment_link = os.getenv('STRIPE_PAYMENT_LINK')
    handbook_url = os.getenv('HANDBOOK_URL')

    if is_adult:
        template = f"""Hey {student_name}, we've got you down for {time} on {day} {date} with {tutor}. ✨🎶

To give {tutor} some context, you're {experience_level} and love {genres}!

📍The school is inside CC Music Shop at 33 Otago Street G12 8JJ. Just take a seat on the couch by the door when you arrive and {tutor} will come meet you.

Below is the payment link for your lessons, please note that your first payment confirms the lesson slot, for next week.🚨Please let us know when you have done this!

I'll also include a link to our welcome handbook which has more details about our teaching approach, homework, cancellation policies and more. 📖

Feel free to pop down any questions you have and one of us will be sure to get back to you!

Cheers! 😃

{payment_link}

{handbook_url}"""
    else:
        template = f"""Hey {parent_name}, we've got {student_name} down for {time} on {day} {date} with {tutor}. ✨🎶

To give {tutor} some context, {student_name} is {age} and {experience_level}. They love {genres}!

📍The school is inside CC Music Shop at 33 Otago Street G12 8JJ. Just take a seat on the couch by the door when you arrive and {tutor} will come meet you.

Below is the payment link for your lessons, please note that your first payment confirms the lesson slot, for next week.🚨Please let us know when you have done this!

I'll also include a link to our welcome handbook which has more details about our teaching approach, homework, cancellation policies and more. 📖

Feel free to pop down any questions you have and one of us will be sure to get back to you!

Cheers! 😃

{payment_link}

{handbook_url}"""

    return template


def generate_soundslice_followup(student_name, tutor, soundslice_code):
    """
    Generate Soundslice follow-up message

    Args:
        student_name: Student name (e.g., "Sarah")
        tutor: Teacher name (e.g., "Emma")
        soundslice_code: Unique Soundslice course code for this student

    Returns:
        Formatted Soundslice message string
    """
    template = f"""Oo one last important thing to do. If you could head to soundslice.com and make a free account, then head to soundslice.com/coursecode and pop in this code *{soundslice_code}* that will make a folder that {student_name} can access and {tutor} can put in all the songs they are learning 💥"""

    return template


def generate_missed_call_message(parent_name):
    """
    Generate missed call / initial inquiry message

    Args:
        parent_name: Parent/guardian name

    Returns:
        Formatted missed call message string
    """
    handbook_url = os.getenv('HANDBOOK_URL')

    template = f"""Hey {parent_name}! Thanks much for your interest in First Chord Music School! We are excited to get a chat with you sort you out with a first lesson! 😃

Let's organise a call to chat about your musical interests and goals so we can match you with the perfect tutor. Could you let us know which of these times works for you for a welcome call? 📱

Our Welcome Call Times:
• Mondays: 12:00-1:30pm
• Fridays: 12:00-1:30pm
• Sundays: 10:00-11:00am

Just let us know which day and time slot works best, and either Finn or Tom will give you a call then! We're aiming to get you started with lessons right away or schedule you in for August.

Feel free to pop down any questions you have, and one of us will be sure to get back to you!

As we're now working through our waiting list, please do let us know as soon as possible when you'd like your welcome call so we can prioritize getting you sorted.

I'll also include a link to our welcome handbook which has more details about our teaching approach, homework, cancellation policies and more. 📖

{handbook_url}

We can't wait to chat soon and get your musical journey started! 🎸🎹🥁

Cheers!
Finn & Tom
First Chord Music School"""

    return template


# Experience level mappings
EXPERIENCE_LEVELS = {
    'beginner': 'a complete beginner',
    'complete beginner': 'a complete beginner',
    'new': 'a complete beginner',
    '1': 'a complete beginner',

    'some': 'has some experience',
    'some experience': 'has some experience',
    '2': 'has some experience',

    'intermediate': 'at an intermediate level',
    'advanced': 'at an intermediate level',
    '3': 'at an intermediate level',
}


def normalize_experience_level(user_input):
    """
    Convert user input to standardized experience level phrase

    Args:
        user_input: User's input for experience level

    Returns:
        Standardized phrase
    """
    user_input = user_input.lower().strip()
    return EXPERIENCE_LEVELS.get(user_input, 'a complete beginner')
