# Knowledge Base Sources & Methodology

## DS-001 (institutional knowledge) — how it was built

Every record in `database/seed_data/ds001_institution/` was built by
searching for and reading Gateway ICT Polytechnic, Saapade's official
website (new.gaposa.edu.ng) and other public sources (admission notice
aggregators like myschool.ng and admissionform.ng, and a general
institutional directory), on 2026-07-14. Nothing was invented.

Where a fact could be confirmed, it's stated plainly with a `source` field
pointing to where it came from. **Where a fact could not be confirmed —
current HOD name, department office location, exact fees, specific
grading-scale numbers, exact SIWES coordinator contact, and several
others — the record says so explicitly** ("Information Not Available")
rather than presenting a plausible-sounding guess as fact. This was a
deliberate choice per the DS-001 specification's own instruction: *"Do
not invent facts. If information cannot be verified, mark it as
'Information Not Available' rather than guessing."*

### What's confirmed vs. not, at a glance

| Verified | Not verified (marked accordingly in the dataset) |
|---|---|
| Institution name, founding year (2006), Ogun State ownership | Current exact vision/mission wording (sourced from a third-party directory, not the official handbook) |
| Campus address and postal codes | Department office location for Computer Science |
| Current Rector's name | Current Computer Science HOD's name |
| General contact phone/email | Department-specific phone/email |
| HND Computer Science and HND Computer Engineering programmes exist | Whether ND Computer Science is offered on this specific campus |
| General campus facilities (ICT labs, library, hostels, sports complex) | Facility-specific hours, capacity, policies |
| General ND/HND admission requirements | Exact current fees (change per session) |
| NBTE-standard ND/HND programme structure | Gateway-specific grading scale numbers, attendance policy percentage, exam conduct rules |

### Why this matters for COSIB's behavior

The AI's system prompt (`app/services/prompt_engineering.py`) explicitly
instructs it not to hallucinate institutional facts and to say when it's
uncertain. Knowledge base articles marked "Information Not Available"
reinforce this — if a student asks who the HOD is, COSIB's knowledge
retrieval will surface the article saying that isn't confirmed, rather
than the model guessing a plausible-sounding name.

### Keeping this current

This dataset reflects a point-in-time check (2026-07-14). Contact details,
leadership, and admission requirements at any institution change over
time. The department should periodically re-verify these records via the
Admin > Knowledge Base UI (or by re-running
`python -m scripts.seed_knowledge_base` after updating the source JSON
files) — this is exactly the kind of upkeep the admin portal (ES-003) was
built to make possible without a code deploy.

## DS-002 (academic knowledge) — how it was built

General Computer Science curriculum content (programming, algorithms,
databases, networking, operating systems, software engineering, AI,
cybersecurity, discrete mathematics) is well-established, stable knowledge
that doesn't require institution-specific verification — no search was
needed for these topics. Content was written directly, referencing
standard textbooks (cited per-article in each dataset file's `references`
field — e.g. CLRS for algorithms, Silberschatz et al. for OS/databases,
Sommerville for software engineering).

This is a representative, high-quality starting set (27 topics across 9
subject areas, each with explanation, worked example, and quiz questions)
rather than an exhaustive curriculum — extending it is just adding more
JSON records in the same shape to the relevant `ds002_academic/*.json`
file and re-running the seed script.

## DS-003 (dynamic/demo content)

Announcements, events, and feedback in `ds003_dynamic/` are clearly
fictional demo content for presentation purposes (see
`scripts/seed_demo.py`), not claims about real Gateway ICT Polytechnic
activity. Suggested prompts and the AI/analytics configuration reference
files document the *shape* of live, admin-editable data — the actual
values are managed through the database and admin UI, not read from these
JSON files at runtime.
