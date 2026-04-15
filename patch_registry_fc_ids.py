"""
Patch students-registry.js with fcStudentId fields.

Reads fc_students.csv to get the mms_student_id → fc_student_id map,
then injects `fcStudentId: 'fc_std_XXXXXXXX',` into each student object
in the registry. The change is purely additive — no existing fields are
touched, and the file remains valid JS.

Run once. Safe to re-run (skips entries already patched).
"""

import csv
import re
import shutil
from pathlib import Path

from config import REGISTRY_PATH as REGISTRY, FC_EXPORTS_DIR
FC_STUDENTS = FC_EXPORTS_DIR / "fc_students.csv"
BACKUP = REGISTRY.with_suffix('.js.bak')

# ── 1. Build lookup: mms_id → fc_student_id ──────────────────────────────────
fc_map: dict[str, str] = {}
with open(FC_STUDENTS) as f:
    for row in csv.DictReader(f):
        if row['in_registry'] == 'TRUE' and row['mms_student_id']:
            fc_map[row['mms_student_id']] = row['fc_student_id']

print(f"FC map loaded: {len(fc_map)} registry students")

# ── 2. Parse and patch the JS file ───────────────────────────────────────────
lines = REGISTRY.read_text(encoding='utf-8').splitlines(keepends=True)

key_pattern   = re.compile(r"^\s+'(sdt_\w+)':\s*\{")
close_pattern = re.compile(r"^(\s+)\},\s*//")  # matches "  }, // Name"

output: list[str] = []
current_mms_id: str | None = None
patched = 0
already_patched = 0
skipped = 0

for line in lines:
    # Detect the start of a student block
    m = key_pattern.match(line)
    if m:
        current_mms_id = m.group(1)
        output.append(line)
        continue

    # Detect the closing of a student block
    m = close_pattern.match(line)
    if m and current_mms_id is not None:
        indent = m.group(1)  # preserve existing indentation (typically 2 spaces)
        fc_id = fc_map.get(current_mms_id)

        if fc_id:
            # Check not already patched (look back a few lines)
            recent = ''.join(output[-5:])
            if 'fcStudentId' in recent:
                already_patched += 1
            else:
                output.append(f"{indent}  fcStudentId: '{fc_id}',\n")
                patched += 1
        else:
            skipped += 1  # registry-only student not in CSV (shouldn't happen)

        current_mms_id = None
        output.append(line)
        continue

    # All other lines pass through unchanged
    output.append(line)

print(f"Patched:         {patched}")
print(f"Already patched: {already_patched}")
print(f"Skipped (no FC): {skipped}")

# ── 3. Write back ─────────────────────────────────────────────────────────────
if patched > 0:
    shutil.copy2(REGISTRY, BACKUP)
    print(f"Backup written:  {BACKUP}")
    REGISTRY.write_text(''.join(output), encoding='utf-8')
    print(f"Registry updated: {REGISTRY}")
else:
    print("Nothing to do — all entries already patched or no matches.")
