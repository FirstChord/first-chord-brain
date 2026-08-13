"""Regression coverage for the shared durable tutor roster."""

import unittest

import generate_fc_ids
from src.mms_client import MMSClient
from tutors import TUTORS, validate_tutors


class TutorRosterTests(unittest.TestCase):
    def test_canonical_roster_is_valid_and_contains_hamish(self):
        self.assertIs(validate_tutors(), TUTORS)
        hamish = next(tutor for tutor in TUTORS if tutor["short_name"] == "Hamish")
        self.assertEqual(hamish["mms_teacher_id"], "tch_zLnnJw")
        self.assertEqual(hamish["instruments"], ["guitar"])

    def test_mms_client_derives_its_teacher_database_from_the_canonical_roster(self):
        client = MMSClient()
        expected = {
            tutor["short_name"]: {
                "full_name": tutor["full_name"],
                "teacher_id": tutor["mms_teacher_id"],
                "instruments": tutor["instruments"],
            }
            for tutor in TUTORS
        }

        actual = {
            short_name: {
                "full_name": details["full_name"],
                "teacher_id": details["teacher_id"],
                "instruments": details["instruments"],
            }
            for short_name, details in client.teachers.items()
        }
        self.assertEqual(actual, expected)

    def test_identity_generation_uses_the_same_canonical_roster(self):
        self.assertIs(generate_fc_ids.TUTORS, TUTORS)

    def test_validation_rejects_duplicate_teacher_ids(self):
        duplicate = [dict(TUTORS[0]), dict(TUTORS[1])]
        duplicate[1]["mms_teacher_id"] = duplicate[0]["mms_teacher_id"]

        with self.assertRaisesRegex(ValueError, "Duplicate MMS teacher ID"):
            validate_tutors(duplicate)


if __name__ == "__main__":
    unittest.main()
