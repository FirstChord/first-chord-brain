# First Chord — Student Field Data Dictionary

**Read this alongside `CONTEXT.md`.** This file documents every field associated with a student across all systems: what it contains, where it is written, where it is read, and what the conflict rule is if sources disagree.

---

## Canonical Stores

There are two canonical stores for student data. All other representations are derived.

| Store | Domain | Write authority |
|---|---|---|
| Google Sheets `Students` tab | Identity, relationships, lesson config, Stripe, contact info | Brain (onboarding) + Payment Pause (Stripe fields only) |
| `music-school-dashboard/lib/config/students-registry.js` | Portal config (Soundslice, Theta, friendlyUrl) | Brain (onboarding) + `add-student` skill |

**Rule:** update the canonical source first. Never patch a derived file to fix a source problem.

---

## Identity Fields
*Write authority: Google Sheets `Students` tab*

| Field | Sheets column | registry.js key | Brain `student_data` key | MMS source | Notes |
|---|---|---|---|---|---|
| Student first name | `Student forename` | `firstName` | `student_forename` | `FirstName` | Written to both Sheets and registry at onboarding |
| Student last name | `Student Surname` | `lastName` | `student_surname` | `LastName` | Written to both Sheets and registry at onboarding |
| MMS student ID | `mms_id` | entry key | `mms_id` | `ID` | Primary external ID. Format: `sdt_XXXXXXX` |
| FC student ID | `FC Student ID` | `fcStudentId` | `fc_student_id` | — | Deterministic: `sha256(forename:surname:email)[:8]`. Format: `fc_std_XXXXXXXX`. Assigned at onboarding; stable before MMS ID exists |
| Parent first name | `Parent forename` | — | `parent_forename` | `Family.Parents[0].FirstName` | Same as student for adults |
| Parent last name | `Parent surname` | — | `parent_surname` | `Family.Parents[0].LastName` | Same as student for adults |
| Parent / contact email | `Email` | — | `parent_email` | `Family.Parents[0].Email.EmailAddress` | Student's own email for adults |
| Contact number | `Contact Number` | — | `contact_number` | `Telephone.TelephoneNumber` | Parent's number for children, student's for adults. Added for future WhatsApp Business API integration. Currently captured from MMS at onboarding |
| Is adult | *(not yet in Sheets)* | — | `is_adult` | inferred (age ≥ 19) | Captured at onboarding, stored in FC identity layer (`FC_Students.is_adult`). **Flag: should be added as a Sheets column** |

---

## Lesson Config Fields
*Write authority: Google Sheets `Students` tab*

| Field | Sheets column | registry.js key | Brain `student_data` key | Notes |
|---|---|---|---|---|
| Tutor | `Tutor` | `tutor` | `tutor` / `tutor_short` | **Inconsistency:** Sheets stores full name (`"Arion Xenos"`), registry stores short name (`"Arion"`). See Known Inconsistencies §1 below |
| Instrument | `Instrument` | `instrument` | `instrument` | Written to both stores at onboarding. Normalised to: Guitar, Piano, Bass, Ukulele, Singing |
| Lesson length | `Lesson length` | — | `lesson_length` | Minutes as string (e.g. `"30"`). Only in Sheets |

---

## Portal Config Fields
*Write authority: `students-registry.js`*

| Field | registry.js key | Sheets column | Brain `student_data` key | Notes |
|---|---|---|---|---|
| Soundslice course URL | `soundsliceUrl` | `Soundslice` | `soundslice_url` | Written to both stores at onboarding. **Registry is authoritative** — Sheets copy is for human reference only |
| Theta username | `thetaUsername` | `Theta Username` / `Theta` | `theta_username` | Written to both stores at onboarding. **Registry is authoritative**. Auto-generated: `firstname + lastname + "fc"`, lowercase, no spaces/hyphens/apostrophes |
| Portal friendly URL | `friendlyUrl` | — | *(generated in _update_dashboard_registry)* | Only in registry. Auto-generated: `firstname`, falling back to `firstname-lastinitial` if collision |

---

## Stripe Fields
*Write authority: Google Sheets `Students` tab — written by Payment Pause only. Brain never touches these.*

| Field | Sheets column | Notes |
|---|---|---|
| Stripe customer ID | `stripe_customer_id` | Set when student subscribes via Payment Pause PWA |
| Stripe subscription ID | `stripe_subscription_id` | Set when student subscribes via Payment Pause PWA |

---

## Operational Fields (Vault Only)
*These fields are collected at onboarding but currently only persisted to vault markdown files (`vault/Onboarding/YYYY-MM-DD-name.md`). They are not in Sheets.*

| Field | Brain `student_data` key | Notes |
|---|---|---|
| Experience level | `experience_level` | One of: `"a complete beginner"`, `"has some experience"`, `"at an intermediate level"` |
| Interests / genres | `interests` | Combined genres + songs string from MMS notes form |
| Lesson day | `day` | e.g. `"Tuesday"` |
| Lesson time | `time` | e.g. `"4pm"` |
| First lesson date | `date` | e.g. `"Dec 17"` |

**Flag:** These fields are potentially useful for admin reporting and personalisation. Consider adding `Instrument`, `Experience`, `Interests` columns to Sheets in a future pass.

---

## FC Identity Layer (Derived — Never Edit Manually)
*Generated by `python3 generate_fc_ids.py`. Writes directly to Google Sheets FC tabs.*

| Tab | Contents | Regenerate with |
|---|---|---|
| `FC_Students` | All students: `fc_std_*` IDs, `is_adult` flag | `generate_fc_ids.py` |
| `FC_People` | All people (students + parents + tutors): `fc_per_*` IDs | `generate_fc_ids.py` |
| `FC_Tutors` | 16 active tutors: `fc_tut_*` IDs, MMS teacher IDs | `generate_fc_ids.py` |
| `FC_Parent_Student_Links` | Parent → student relationships | `generate_fc_ids.py` |
| `FC_External_IDs` | Cross-reference: MMS, Stripe, Soundslice, Theta IDs per FC entity | `generate_fc_ids.py` |

**Rule:** these tabs are outputs, not inputs. If a value here looks wrong, fix the source in Sheets or `students-registry.js` then regenerate.

---

## MMS API — Available Fields

Fields returned by the MMS API that are available at onboarding time. Not all are currently persisted.

| MMS field | Path in API response | Persisted to | Notes |
|---|---|---|---|
| MMS student ID | `ID` | Sheets + registry key | Always persisted |
| First name | `FirstName` | Sheets + registry | Always persisted |
| Last name | `LastName` | Sheets + registry | Always persisted |
| Date added to waiting list | `DateStarted` | — | Used for waiting list display only; not stored |
| Status | `Status` | — | `"Waiting"` or `"Active"`. Not mirrored to Sheets |
| Telephone | `Telephone.TelephoneNumber` | **Sheets `Contact Number`** | Previously discarded. Now persisted as `contact_number` |
| Student email | `Email.EmailAddress` | Sheets `Email` (adult only) | For adult students only |
| Parent first name | `Family.Parents[0].FirstName` | Sheets `Parent forename` | — |
| Parent last name | `Family.Parents[0].LastName` | Sheets `Parent surname` | — |
| Parent email | `Family.Parents[0].Email.EmailAddress` | Sheets `Email` | — |
| Sign-up form: instrument | `Note` (parsed) | Prefills onboarding prompt | Normalised via `_normalise_instrument()` |
| Sign-up form: age | `Note` (parsed) | Prefills onboarding prompt | Used for adult auto-detection (≥19 → adult) |
| Sign-up form: experience | `Note` (parsed) | Prefills experience level prompt | `"Yes"` → some experience, `"No"` → beginner |
| Sign-up form: genres | `Note` (parsed) | Prefills interests prompt | Combined with songs |
| Sign-up form: songs | `Note` (parsed) | Prefills interests prompt | Combined with genres |

---

## Known Inconsistencies

### 1. Tutor name format difference (intentional, handled)
- **Sheets** stores full tutor name: `"Arion Xenos"`
- **registry.js** stores short name: `"Arion"`
- **This is intentional.** Sheets full name is for human readability; registry short name is a lookup key against `mms_client.py` `teachers` dict
- **Comparison logic in `generate_fc_ids.py` handles this correctly:** it takes `tutor_full.split()[0].lower()` (first word of Sheets name) and compares it to the registry short name. No false positives
- **The 6 `TUTOR CONFLICT` flags are genuine assignment mismatches** (e.g. registry says `"Eléna"` but Sheets says `"Ines Alban Zapata Peréz"`) — not format noise
- **No code change needed.** The two-format system works as designed

### 2. Soundslice URL and Theta username written to both stores
- Both are written to Sheets and registry.js at onboarding
- **registry.js is authoritative** for the portal. Sheets copy exists for human visibility
- If they ever diverge, registry.js wins for portal behaviour; Sheets wins for identity/contact lookups
- This dual-write is acceptable and intentional

### 3. `is_adult` not in Sheets `Students` tab
- Captured at onboarding, stored in `FC_Students` tab (derived)
- The `Students` tab has no `is_adult` column
- **Impact:** Payment Pause and any admin surface reading Sheets cannot distinguish adult vs child students without cross-referencing `FC_Students`
- **Future:** add `is_adult` boolean column to `Students` tab, written at onboarding

### 4. `experience_level` and `interests` not persisted to Sheets
- Collected at onboarding, used to generate welcome message, saved to vault markdown only
- Not accessible to any downstream system
- **Future:** consider adding `Experience` and `Interests` columns to `Students` tab for admin dashboard display

### 5. `fcStudentId` in registry but not passed through `generate-configs`
- `fcStudentId` is present in `students-registry.js` for all 200 students
- `npm run generate-configs` does not yet propagate it to the generated config files
- **Impact:** portal pages do not have access to the FC ID at render time
- Tracked in `CONTEXT.md` → What's NOT Yet Done

---

## Field Conflict Resolution Rules

When sources disagree, apply these rules in order:

| Scenario | Rule |
|---|---|
| Sheets `Students` tab vs registry.js for tutor assignment | Check MMS live API — it is the true operational source for tutor assignments |
| Sheets vs registry.js for Soundslice URL | Registry wins for portal behaviour; investigate and correct Sheets if they differ |
| Sheets vs registry.js for Theta username | Registry wins for portal behaviour; investigate and correct Sheets if they differ |
| FC identity layer tabs vs `Students` tab | Regenerate FC layer (`python3 generate_fc_ids.py`) — it reads from `Students` tab, so divergence means layer is stale |
| Brain `student_data` vs any persisted store | `student_data` is transient (per-onboarding-session). Persisted stores win after onboarding completes |
| Registry.js student name vs Sheets student name | Manual review required — check MMS as tiebreaker |

---

## Onboarding Write Sequence

At the end of a successful onboarding run, fields are written in this order:

1. **Google Sheets `Students` tab** (`_step_2_google_sheets`) — identity + lesson config + contact
2. **Vault markdown** (`_save_to_vault`) — full onboarding record including operational fields
3. **FC identity layer** (`_regenerate_fc_layer`) — all FC tabs regenerated from fresh Sheets data
4. **`students-registry.js`** (`_update_dashboard_registry`) — portal config entry added
5. **Derived dashboard configs** (`npm run generate-configs`) — all other config files regenerated
6. **Railway deploy** (`git push`) — auto-deploys in ~2 minutes

If any step fails, the vault record and the step log in the console are the source of truth for what was and was not completed.
