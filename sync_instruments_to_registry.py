#!/usr/bin/env python3
"""Sync the Google Sheet's Instrument column into the dashboard's students-registry.js.

WHY THIS EXISTS. The Sheet and `music-school-dashboard/lib/config/students-registry.js`
are BOTH canonical in their own domain, and **nothing syncs `instrument` between them**.
In July 2026 that gap left 38 students with no instrument in the registry — Finn had
filled the Sheet in, but the dashboard reads the registry, so every one of them opened
the song shelf to an empty page. It also hid a mislabelled student (Alba: bass, not
guitar) from a scan that only looked at the registry.

So: run this whenever instruments are edited in the Sheet. It is READ-ONLY against the
Sheet and writes only the registry.

    python3 sync_instruments_to_registry.py            # dry run — always look first
    python3 sync_instruments_to_registry.py --apply

Then, in the dashboard: `npm run generate-configs && npm run test:admin`.

SCOPE IS DELIBERATELY NARROW:
  - FILLS entries that have no instrument at all (the Sheet is the only source).
  - NORMALISES casing ('guitar' -> 'Guitar').
  - Genuine disagreements (registry says Voice, Sheet says Piano) are REPORTED and left
    alone. Those are judgement calls about a real child's lessons, not a sync.

Values are written with the same escaping rule as `escapeRegistryValue` in
lib/admin/registry-helpers.mjs — an unescaped apostrophe in a surname (O'Neil) once left
the canonical registry as invalid JavaScript for three months.

NOTE: an instrument the song catalogue does not know (e.g. a brand-new one) means an
EMPTY song shelf for that student. The dashboard test suite enforces this — see
`INSTRUMENTS_WITHOUT_REPERTOIRE` in tests/admin/songs-catalogue.test.mjs.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/Users/finnlemarinel/Desktop/FirstChord/first-chord-brain")
import generate_fc_ids as g  # noqa: E402

REGISTRY = Path("/Users/finnlemarinel/Desktop/FirstChord/music-school-dashboard/lib/config/students-registry.js")

# Values the Sheet uses that the dashboard writes verbatim. Case is normalised to these.
CANON = {
    "guitar": "Guitar", "bass": "Bass", "piano": "Piano", "voice": "Voice",
    "singing": "Singing", "ukulele orchestra": "Ukulele Orchestra",
    "electric guitar": "Electric Guitar", "drums": "Drums",
    "piano / voice": "Piano / Voice", "piano / guitar": "Piano / Guitar",
    "guitar / piano": "Guitar / Piano",
}


def escape(v):
    return str(v).replace("\\", "\\\\").replace("'", "\\'")


def main():
    apply = "--apply" in sys.argv
    sheet = {}
    for row in g.fetch_sheets_students():
        mms = (row.get("mms_id") or "").strip()
        inst = (row.get("Instrument") or "").strip()
        if mms and inst:
            sheet[mms] = CANON.get(inst.lower(), inst)

    src = REGISTRY.read_text()
    filled, cased, skipped_conflict = [], [], []

    def fix_entry(m):
        mms, body = m.group(1), m.group(2)
        s_inst = sheet.get(mms)
        if not s_inst:
            return m.group(0)

        cur = re.search(r"(\n(\s*)instrument:\s*)'((?:[^'\\]|\\.)*)'", body)
        if cur:
            existing = cur.group(3).replace("\\'", "'")
            if existing == s_inst:
                return m.group(0)
            # An empty instrument field is a blank to fill, not a disagreement.
            if not existing.strip():
                filled.append(f"{mms}: (blank) -> {s_inst!r}")
                new_body = body[: cur.start()] + f"{cur.group(1)}'{escape(s_inst)}'" + body[cur.end():]
                return f"  '{mms}': {{{new_body}\n  }},"
            if existing.lower() == s_inst.lower():
                cased.append(f"{mms}: {existing!r} -> {s_inst!r}")
                new_body = body[: cur.start()] + f"{cur.group(1)}'{escape(s_inst)}'" + body[cur.end():]
                return f"  '{mms}': {{{new_body}\n  }},"
            # A real disagreement — leave it alone, report it.
            skipped_conflict.append(f"{mms}: registry={existing!r} sheet={s_inst!r}")
            return m.group(0)

        # No instrument field at all: insert one after `tutor:`, matching the house layout.
        tutor = re.search(r"\n(\s*)tutor:\s*'(?:[^'\\]|\\.)*',", body)
        if not tutor:
            skipped_conflict.append(f"{mms}: no tutor line to anchor instrument after")
            return m.group(0)
        indent = tutor.group(1)
        insert_at = tutor.end()
        new_body = body[:insert_at] + f"\n{indent}instrument: '{escape(s_inst)}'," + body[insert_at:]
        filled.append(f"{mms}: -> {s_inst!r}")
        return f"  '{mms}': {{{new_body}\n  }},"

    out = re.sub(r"  '(sdt_\w+)': \{(.*?)\n  \},", fix_entry, src, flags=re.S)

    print(f"FILLED (had no instrument): {len(filled)}")
    for f in filled:
        print("  ", f)
    print(f"\nCASING NORMALISED: {len(cased)}")
    for c in cased:
        print("  ", c)
    print(f"\nLEFT ALONE — genuine disagreement, needs a decision: {len(skipped_conflict)}")
    for c in skipped_conflict:
        print("  ", c)

    if apply:
        REGISTRY.write_text(out)
        print("\nWROTE registry.")
    else:
        print("\n(dry run — pass --apply to write)")


if __name__ == "__main__":
    main()
