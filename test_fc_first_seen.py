"""Tests for durable first-seen dates.

The bug these guard against is subtle and silent: created_at looked populated
and plausible on every row, it was just always today's date. So the assertions
that matter are the ones about a *second* run — one run alone always looks fine.

Run with: python3 -m unittest test_fc_first_seen -v
"""
import tempfile
import unittest
from pathlib import Path

from fc_first_seen import (
    KEY_SPECS,
    apply_first_seen,
    compose_key,
    load_first_seen,
    merge_first_seen,
    save_first_seen,
)


class MergeTests(unittest.TestCase):
    """The merge lets the live tabs act as a second memory, so the hourly job
    remembers new entities without needing to write back to the repo."""

    def test_earliest_wins(self):
        memo = {"FC_Students:sdt_a": "2026-07-28"}
        changed = merge_first_seen(memo, {"FC_Students:sdt_a": "2026-04-15"})

        self.assertEqual(changed, 1)
        self.assertEqual(memo["FC_Students:sdt_a"], "2026-04-15")

    def test_later_date_from_tabs_is_ignored(self):
        """Tabs still holding the old generation-time stamps must not be able to
        push a correct early date forward."""
        memo = {"FC_Students:sdt_a": "2026-04-15"}
        changed = merge_first_seen(memo, {"FC_Students:sdt_a": "2026-07-28"})

        self.assertEqual(changed, 0)
        self.assertEqual(memo["FC_Students:sdt_a"], "2026-04-15")

    def test_key_absent_from_seed_is_adopted(self):
        memo = {}
        merge_first_seen(memo, {"FC_Students:sdt_new": "2026-09-01"})

        self.assertEqual(memo["FC_Students:sdt_new"], "2026-09-01")

    def test_junk_values_are_rejected(self):
        memo = {"FC_Students:sdt_a": "2026-04-15"}
        merge_first_seen(memo, {
            "FC_Students:sdt_a": "not-a-date",
            "FC_Students:sdt_b": "",
            "": "2026-01-01",
        })

        self.assertEqual(memo, {"FC_Students:sdt_a": "2026-04-15"})

    def test_compose_key_uses_the_shared_spec(self):
        """The sheet reader passes no field names, so it must resolve the same
        key the writer would."""
        row = {"mms_student_id": "sdt_a", "fc_student_id": "fc_std_x"}
        self.assertEqual(compose_key("FC_Students", row), "FC_Students:sdt_a")

    def test_compose_key_falls_back_when_anchor_missing(self):
        row = {"mms_student_id": "", "fc_student_id": "fc_std_x"}
        self.assertEqual(compose_key("FC_Students", row), "FC_Students:fc_std_x")

    def test_every_spec_table_has_a_usable_key(self):
        for table, (primary, _fallback) in KEY_SPECS.items():
            self.assertTrue(primary, f"{table} has no primary key fields")


class FirstSeenTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.base = Path(self._dir.name)

    def tearDown(self):
        self._dir.cleanup()

    def test_missing_seed_file_is_not_an_error(self):
        self.assertEqual(load_first_seen(self.base), {})

    def test_first_run_stamps_today_and_records_it(self):
        rows = [{"fc_student_id": "fc_std_aaa"}, {"fc_student_id": "fc_std_bbb"}]
        memo = {}
        new = apply_first_seen("FC_Students", rows, "fc_student_id", memo, "2026-07-28")

        self.assertEqual(new, 2)
        self.assertEqual([r["created_at"] for r in rows], ["2026-07-28", "2026-07-28"])
        self.assertEqual(memo["FC_Students:fc_std_aaa"], "2026-07-28")

    def test_second_run_on_a_later_day_does_not_move_the_date(self):
        """This is the actual regression. Before the fix, every row's created_at
        advanced with the calendar on every hourly run."""
        rows = [{"fc_student_id": "fc_std_aaa"}]
        memo = {}
        apply_first_seen("FC_Students", rows, "fc_student_id", memo, "2026-07-28")

        later = [{"fc_student_id": "fc_std_aaa"}]
        new = apply_first_seen("FC_Students", later, "fc_student_id", memo, "2026-11-03")

        self.assertEqual(new, 0)
        self.assertEqual(later[0]["created_at"], "2026-07-28")

    def test_new_entity_among_old_ones_gets_todays_date_only_for_itself(self):
        memo = {"FC_Students:fc_std_old": "2026-04-15"}
        rows = [{"fc_student_id": "fc_std_old"}, {"fc_student_id": "fc_std_new"}]
        new = apply_first_seen("FC_Students", rows, "fc_student_id", memo, "2026-07-28")

        self.assertEqual(new, 1)
        self.assertEqual(rows[0]["created_at"], "2026-04-15")
        self.assertEqual(rows[1]["created_at"], "2026-07-28")

    def test_departed_entity_keeps_its_row_in_the_memo(self):
        """A student who leaves vanishes from the regenerated tables. Their
        first-seen row is the only evidence they were ever here."""
        memo = {"FC_Students:fc_std_gone": "2026-04-15"}
        apply_first_seen("FC_Students", [], "fc_student_id", memo, "2026-07-28")

        self.assertIn("FC_Students:fc_std_gone", memo)

    def test_rejoining_does_not_reset_first_seen(self):
        memo = {"FC_Students:fc_std_back": "2026-04-15"}
        rows = [{"fc_student_id": "fc_std_back"}]
        apply_first_seen("FC_Students", rows, "fc_student_id", memo, "2027-01-09")

        self.assertEqual(rows[0]["created_at"], "2026-04-15")

    def test_tables_do_not_collide_on_a_shared_id(self):
        memo = {}
        apply_first_seen("FC_Students", [{"id": "x"}], "id", memo, "2026-04-15")
        apply_first_seen("FC_People", [{"id": "x"}], "id", memo, "2026-07-28")

        self.assertEqual(memo["FC_Students:x"], "2026-04-15")
        self.assertEqual(memo["FC_People:x"], "2026-07-28")

    def test_composite_key_distinguishes_mappings_of_one_entity(self):
        """FC_External_IDs holds many rows per entity — keying on the entity
        alone would collapse them into one date."""
        memo = {}
        rows = [
            {"fc_entity_id": "fc_std_a", "external_system": "stripe", "external_key": "customer"},
            {"fc_entity_id": "fc_std_a", "external_system": "mms", "external_key": "student"},
        ]
        new = apply_first_seen(
            "FC_External_IDs", rows, ["fc_entity_id", "external_system", "external_key"], memo, "2026-07-28"
        )
        self.assertEqual(new, 2)

    def test_row_with_no_identity_falls_back_to_today_without_polluting_memo(self):
        memo = {}
        rows = [{"fc_student_id": ""}]
        new = apply_first_seen("FC_Students", rows, "fc_student_id", memo, "2026-07-28")

        self.assertEqual(new, 0)
        self.assertEqual(rows[0]["created_at"], "2026-07-28")
        self.assertEqual(memo, {})

    def test_seed_file_round_trips(self):
        memo = {"FC_Students:fc_std_aaa": "2026-04-15", "FC_People:fc_per_bbb": "2026-05-01"}
        save_first_seen(self.base, memo)

        self.assertEqual(load_first_seen(self.base), memo)

    def test_saved_seed_survives_a_wiped_sheet(self):
        """The seed file, not the Sheet, is the authority — a cleared tab must
        not be able to reset history."""
        memo = {"FC_Students:fc_std_aaa": "2026-04-15"}
        save_first_seen(self.base, memo)

        reloaded = load_first_seen(self.base)
        rows = [{"fc_student_id": "fc_std_aaa"}]
        apply_first_seen("FC_Students", rows, "fc_student_id", reloaded, "2026-07-28")

        self.assertEqual(rows[0]["created_at"], "2026-04-15")



class PersonalDataTests(unittest.TestCase):
    """The seed file is committed to git, so no key may carry personal data."""

    def test_email_keys_are_digested_not_stored_raw(self):
        key = compose_key("FC_People", {"email": "Parent.Name@example.com"})
        self.assertNotIn("@", key)
        self.assertNotIn("parent.name", key.lower())
        self.assertTrue(key.startswith("FC_People:"))

    def test_email_hashing_is_stable_and_case_insensitive(self):
        # The sheet reader and the writer must land on the same key, and a
        # parent retyping their address in a different case is the same person.
        a = compose_key("FC_People", {"email": "parent@example.com"})
        b = compose_key("FC_People", {"email": "  PARENT@example.com  "})
        self.assertEqual(a, b)

    def test_different_emails_get_different_keys(self):
        a = compose_key("FC_People", {"email": "one@example.com"})
        b = compose_key("FC_People", {"email": "two@example.com"})
        self.assertNotEqual(a, b)

    def test_the_committed_seed_file_contains_no_email_addresses(self):
        from pathlib import Path
        seed = Path(__file__).parent / "fc_first_seen.csv"
        if not seed.exists():
            self.skipTest("no seed file in this checkout")
        self.assertNotIn("@", seed.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
