"""Canonical durable tutor identities shared by Brain and the dashboard.

Operational availability (active, leaving, or retired) belongs to the dashboard's
Tutor_Lifecycle state. Keep former tutors here so historical IDs remain stable.
"""

import re


TUTORS = [
    {"short_name": "Arion", "full_name": "Arion Xenos", "mms_teacher_id": "tch_zplpJw", "instruments": ["guitar", "piano"]},
    {"short_name": "Calum", "full_name": "Calum Steel", "mms_teacher_id": "tch_zMX5Jc", "instruments": ["guitar"]},
    {"short_name": "Chloe", "full_name": "Chloe Mak", "mms_teacher_id": "tch_zQbNJk", "instruments": ["singing", "piano"]},
    {"short_name": "David", "full_name": "David Husz", "mms_teacher_id": "tch_z2j2Jf", "instruments": ["guitar", "piano"]},
    {"short_name": "Dean", "full_name": "Dean Louden", "mms_teacher_id": "tch_zV9TJN", "instruments": ["guitar", "bass"]},
    {"short_name": "Eléna", "full_name": "Eléna Esposito", "mms_teacher_id": "tch_zpy4J9", "instruments": ["piano"]},
    {"short_name": "Fennella", "full_name": "Fennella McCallum", "mms_teacher_id": "tch_C2bJ9", "instruments": ["singing", "piano"]},
    {"short_name": "Finn", "full_name": "Finn Le Marinel", "mms_teacher_id": "tch_QhxJJ", "instruments": ["guitar", "bass", "ukulele"]},
    {"short_name": "Hamish", "full_name": "Hamish Roberts", "mms_teacher_id": "tch_zLnnJw", "instruments": ["guitar"]},
    {"short_name": "Ines", "full_name": "Ines Alban Zapata Peréz", "mms_teacher_id": "tch_zHJlJx", "instruments": ["piano"]},
    {"short_name": "Kenny", "full_name": "Kenny Bates", "mms_teacher_id": "tch_zsyfJr", "instruments": ["guitar"]},
    {"short_name": "Kim", "full_name": "Kim Grant", "mms_teacher_id": "tch_zVg1Js", "instruments": ["guitar"]},
    {"short_name": "Matthew", "full_name": "Matthew Leung", "mms_teacher_id": "tch_zLY8Jn", "instruments": ["piano"]},
    {"short_name": "Patrick", "full_name": "Patrick Shand", "mms_teacher_id": "tch_zw9SJ3", "instruments": ["guitar", "piano"]},
    {"short_name": "Robbie", "full_name": "Robbie Tranter", "mms_teacher_id": "tch_zV9hJ2", "instruments": ["guitar", "bass", "ukulele"]},
    {"short_name": "Scott", "full_name": "Scott Brice", "mms_teacher_id": "tch_zMWrJR", "instruments": ["guitar"]},
    {"short_name": "Stef", "full_name": "Stef McGlinchey", "mms_teacher_id": "tch_z5YmJX", "instruments": ["guitar"]},
    {"short_name": "Tom", "full_name": "Tom Walters", "mms_teacher_id": "tch_mYJJR", "instruments": ["guitar", "bass"]},
]


def validate_tutors(tutors=TUTORS):
    """Fail clearly when a durable tutor identity is incomplete or duplicated."""
    short_names = set()
    teacher_ids = set()

    for index, tutor in enumerate(tutors, start=1):
        short_name = tutor.get("short_name", "").strip()
        full_name = tutor.get("full_name", "").strip()
        teacher_id = tutor.get("mms_teacher_id", "").strip()
        instruments = tutor.get("instruments")

        if not short_name or not full_name:
            raise ValueError(f"Tutor row {index} needs a short_name and full_name")
        if not re.fullmatch(r"tch_[A-Za-z0-9]+", teacher_id):
            raise ValueError(f"Tutor {short_name} has an invalid MMS teacher ID: {teacher_id!r}")
        if not isinstance(instruments, list) or not instruments or not all(instruments):
            raise ValueError(f"Tutor {short_name} needs at least one instrument")
        if short_name.casefold() in short_names:
            raise ValueError(f"Duplicate tutor short name: {short_name}")
        if teacher_id in teacher_ids:
            raise ValueError(f"Duplicate MMS teacher ID: {teacher_id}")

        short_names.add(short_name.casefold())
        teacher_ids.add(teacher_id)

    return tutors


validate_tutors()
