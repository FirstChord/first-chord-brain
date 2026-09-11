"""Tests for FC ID formula and FC student ID resolution.

The failure these guard against: two repos minting "the FC student ID" with two
different formulas, and this job overwriting the stored value every hour.

Run with: python3 -m unittest test_fc_ids -v
"""
import tempfile
import unittest
from pathlib import Path

from fc_ids import (
    FLAG_CONFLICT,
    FLAG_DUPLICATE,
    FLAG_MALFORMED,
    assert_registry_ids_parsed,
    assign_fc_student_ids,
    make_fc_id,
)

TYLER = "sdt_WFQ7Js"
TYLER_DERIVED = "fc_std_fa157fc5"
TYLER_STORED = "fc_std_68c763fb"


class FormulaTests(unittest.TestCase):
    def test_golden_value_matches_the_dashboard(self):
        # Mirrored in music-school-dashboard tests/admin/fc-helpers.test.mjs.
        # If this fails, one repo changed the formula and the other did not.
        self.assertEqual(make_fc_id("std", TYLER), TYLER_DERIVED)


class ResolutionTests(unittest.TestCase):
    def test_stored_registry_id_wins_over_the_formula(self):
        assigned, flags = assign_fc_student_ids({TYLER: (TYLER_STORED, "")})
        self.assertEqual(assigned[TYLER], TYLER_STORED)
        self.assertEqual(flags, {})

    def test_sheet_cell_is_used_when_the_registry_has_none(self):
        assigned, flags = assign_fc_student_ids({TYLER: ("", TYLER_STORED)})
        self.assertEqual(assigned[TYLER], TYLER_STORED)
        self.assertEqual(flags, {})

    def test_formula_is_used_only_when_nothing_is_stored(self):
        assigned, flags = assign_fc_student_ids({TYLER: ("", "")})
        self.assertEqual(assigned[TYLER], TYLER_DERIVED)
        self.assertEqual(flags, {})

    def test_agreeing_registry_and_sheet_raise_nothing(self):
        assigned, flags = assign_fc_student_ids({TYLER: (TYLER_STORED, TYLER_STORED)})
        self.assertEqual(assigned[TYLER], TYLER_STORED)
        self.assertEqual(flags, {})

    def test_registry_wins_a_disagreement_and_it_is_flagged(self):
        other = "fc_std_00000000"
        assigned, flags = assign_fc_student_ids({TYLER: (TYLER_STORED, other)})
        self.assertEqual(assigned[TYLER], TYLER_STORED)
        self.assertEqual([f[0] for f in flags[TYLER]], [FLAG_CONFLICT])

    def test_malformed_stored_value_is_ignored_and_flagged(self):
        assigned, flags = assign_fc_student_ids({TYLER: ("fc_std_NOTHEX!", "")})
        self.assertEqual(assigned[TYLER], TYLER_DERIVED)
        self.assertEqual([f[0] for f in flags[TYLER]], [FLAG_MALFORMED])

    def test_malformed_registry_falls_back_to_a_valid_sheet_cell(self):
        assigned, flags = assign_fc_student_ids({TYLER: ("garbage", TYLER_STORED)})
        self.assertEqual(assigned[TYLER], TYLER_STORED)
        self.assertEqual([f[0] for f in flags[TYLER]], [FLAG_MALFORMED])

    def test_one_stored_id_on_two_students_is_split_and_flagged(self):
        a, b = "sdt_aaaaaa", "sdt_bbbbbb"
        assigned, flags = assign_fc_student_ids({a: (TYLER_STORED, ""), b: (TYLER_STORED, "")})
        self.assertEqual(assigned[a], make_fc_id("std", a))
        self.assertEqual(assigned[b], make_fc_id("std", b))
        self.assertEqual(set(flags), {a, b})
        self.assertTrue(all(f[0] == FLAG_DUPLICATE for fl in flags.values() for f in fl))

    def test_stored_id_equal_to_another_students_derived_id_is_resolved(self):
        a, b = "sdt_aaaaaa", "sdt_bbbbbb"
        assigned, flags = assign_fc_student_ids({
            a: (make_fc_id("std", b), ""),  # a's stored id collides with b's formula
            b: ("", ""),
        })
        self.assertEqual(len(set(assigned.values())), 2)
        self.assertEqual(assigned[b], make_fc_id("std", b))
        self.assertEqual(assigned[a], make_fc_id("std", a))
        self.assertIn(a, flags)

    def test_every_assignment_is_one_to_one(self):
        candidates = {f"sdt_{i:06d}": ("", "") for i in range(300)}
        candidates["sdt_000001"] = (make_fc_id("std", "sdt_000002"), "")
        assigned, _ = assign_fc_student_ids(candidates)
        self.assertEqual(len(set(assigned.values())), len(candidates))


class RegistryParserTests(unittest.TestCase):
    def test_a_registry_that_parses_without_ids_stops_the_run(self):
        # The silent failure: a format change makes every fcStudentId None and
        # the job rekeys all stored IDs to derived ones with no flag.
        with self.assertRaises(RuntimeError):
            assert_registry_ids_parsed({TYLER: {"firstName": "Tyler", "fcStudentId": None}})

    def test_registry_guard_passes_when_ids_are_present_or_registry_is_empty(self):
        self.assertEqual(assert_registry_ids_parsed({TYLER: {"fcStudentId": TYLER_STORED}}), 1)
        self.assertEqual(assert_registry_ids_parsed({}), 0)

    def test_real_registry_parses_with_stored_ids(self):
        import generate_fc_ids
        registry = generate_fc_ids.parse_registry(generate_fc_ids.REGISTRY_PATH)
        self.assertEqual(assert_registry_ids_parsed(registry), len(registry))

    def test_parse_registry_reads_fc_student_id(self):
        import generate_fc_ids

        source = """export const STUDENTS_REGISTRY = {
  'sdt_WFQ7Js': {
    firstName: 'Tyler',
    lastName: 'Beaton',
    friendlyUrl: 'tyler',
    tutor: 'Hamish',
    instrument: 'Guitar',
    soundsliceUrl: 'https://www.soundslice.com/courses/21309/',
    thetaUsername: 'tylerbeatonfc',
    fcStudentId: 'fc_std_68c763fb',
  }, // Tyler Beaton
};
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "students-registry.js"
            path.write_text(source, encoding="utf-8")
            parsed = generate_fc_ids.parse_registry(path)
        self.assertEqual(parsed[TYLER]["fcStudentId"], TYLER_STORED)


if __name__ == "__main__":
    unittest.main()
