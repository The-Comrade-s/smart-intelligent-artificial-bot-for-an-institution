"""
Demo / Presentation Mode seed script (ES-005).

Populates the database with realistic, clearly-fictional sample data so
COSIB looks fully alive for a demo or academic presentation: sample
students, lecturers, courses, conversations with real message history,
feedback, announcements, events, and backdated analytics events for
14-30 days of chart history.

Everything here is demo data, not verified institutional fact — lecturer
names, course codes, and student records are illustrative, not claims
about real people or Gateway ICT Polytechnic's actual current curriculum.
Real institutional facts live in the DS-001 dataset (see
seed_knowledge_base.py), which is kept separate on purpose.

Run after scripts/seed.py and scripts/seed_knowledge_base.py:
    python -m scripts.seed_demo
"""
import asyncio
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.academics import Course, Department, Lecturer  # noqa: E402
from app.models.chat import Conversation, Message  # noqa: E402
from app.models.content import Announcement, Event  # noqa: E402
from app.models.enums import AccountStatus, AnnouncementPriority, ContentStatus, MessageRole, UserRole  # noqa: E402
from app.models.feedback_analytics import AnalyticsEvent, Feedback  # noqa: E402
from app.models.user import User  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DS003_DIR = REPO_ROOT / "database" / "seed_data" / "ds003_dynamic"


def _load_json(filename: str):
    with open(DS003_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


DEMO_STUDENTS = [
    {"full_name": "Chidinma Okafor", "username": "chidinma.okafor", "email": "chidinma.okafor@demo.cosib.local", "matric_number": "GAPOSA/CS/ND2/001"},
    {"full_name": "Tunde Bakare", "username": "tunde.bakare", "email": "tunde.bakare@demo.cosib.local", "matric_number": "GAPOSA/CS/ND2/002"},
    {"full_name": "Amaka Nwosu", "username": "amaka.nwosu", "email": "amaka.nwosu@demo.cosib.local", "matric_number": "GAPOSA/CS/HND1/003"},
    {"full_name": "Segun Ade", "username": "segun.ade", "email": "segun.ade@demo.cosib.local", "matric_number": "GAPOSA/CS/HND1/004"},
    {"full_name": "Blessing Eze", "username": "blessing.eze", "email": "blessing.eze@demo.cosib.local", "matric_number": "GAPOSA/CS/HND2/005"},
    {"full_name": "Kelechi Obi", "username": "kelechi.obi", "email": "kelechi.obi@demo.cosib.local", "matric_number": "GAPOSA/CS/ND1/006"},
]

DEMO_LECTURERS = [
    {"full_name": "Adeyemi Fashola", "title": "Mr.", "email": "a.fashola@demo.cosib.local", "office": "CS Block, Room 12", "office_hours": "Mon & Wed, 10am-12pm", "biography": "Teaches introductory programming and data structures.", "courses_taught": ["Introduction to Programming", "Data Structures"]},
    {"full_name": "Funmilayo Adebayo", "title": "Dr.", "email": "f.adebayo@demo.cosib.local", "office": "CS Block, Room 14", "office_hours": "Tue & Thu, 1pm-3pm", "biography": "Specializes in database systems and software engineering.", "courses_taught": ["Database Management Systems", "Software Engineering"]},
    {"full_name": "Ibrahim Musa", "title": "Mr.", "email": "i.musa@demo.cosib.local", "office": "CS Block, Room 9", "office_hours": "Mon & Fri, 9am-11am", "biography": "Teaches networking and operating systems.", "courses_taught": ["Computer Networks", "Operating Systems"]},
]

DEMO_COURSES = [
    {"code": "COM111", "title": "Introduction to Programming", "level": "ND I", "semester": "First", "units": 3, "description": "Fundamentals of programming using Python: variables, control flow, functions, and basic problem solving."},
    {"code": "COM121", "title": "Introduction to Computer Systems", "level": "ND I", "semester": "Second", "units": 2, "description": "Computer hardware, number systems, and basic computer architecture."},
    {"code": "COM211", "title": "Data Structures", "level": "ND II", "semester": "First", "units": 3, "description": "Arrays, linked lists, stacks, queues, trees, and algorithm complexity."},
    {"code": "COM221", "title": "Database Management Systems", "level": "ND II", "semester": "Second", "units": 3, "description": "Relational database design, normalization, and SQL."},
    {"code": "COM311", "title": "Software Engineering", "level": "HND I", "semester": "First", "units": 3, "description": "SDLC models, requirements engineering, testing, and version control."},
    {"code": "COM321", "title": "Computer Networks", "level": "HND I", "semester": "Second", "units": 3, "description": "OSI model, TCP/IP, routing, and network security fundamentals."},
    {"code": "COM411", "title": "Operating Systems", "level": "HND II", "semester": "First", "units": 3, "description": "Processes, threads, scheduling, memory management, and file systems."},
    {"code": "COM421", "title": "Artificial Intelligence", "level": "HND II", "semester": "Second", "units": 3, "description": "Introduction to machine learning, neural networks, and AI applications."},
]

DEMO_CONVERSATIONS = [
    {
        "title": "Explaining recursion",
        "messages": [
            ("user", "Can you explain recursion with a simple example?"),
            ("assistant", "Recursion is when a function calls itself to solve a smaller version of the same problem, until it hits a base case that stops it. Classic example: factorial.\n\n```python\ndef factorial(n):\n    if n == 0:      # base case\n        return 1\n    return n * factorial(n - 1)  # recursive case\n```\n\n`factorial(4)` calls `factorial(3)`, which calls `factorial(2)`, and so on down to `factorial(0)`, which returns 1 — then the results multiply back up: 1, 1×1=1, 2×1=2, 3×2=6, 4×6=24."),
        ],
    },
    {
        "title": "CSC course registration help",
        "messages": [
            ("user", "How do I register my courses this semester?"),
            ("assistant", "Course registration is done through the student portal at studentportal.gaposa.edu.ng. Log in, select your current level, and pick your courses for the semester before the registration deadline — check your department notice board for the exact date this session, since it varies. If the portal gives an error, contact the Registry."),
        ],
    },
    {
        "title": "Database normalization quiz",
        "messages": [
            ("user", "Generate a quiz on database normalization"),
            ("assistant", "Here's a 3-question quiz on Database Normalization:\n\n1. What does 1NF require of a table's columns?\n2. What problem does normalization primarily solve?\n3. True or False: Most well-designed application databases aim for 3NF.\n\n**Answer key:** 1) Atomic (indivisible) values, with unique rows. 2) Data redundancy and update anomalies. 3) True."),
        ],
    },
    {
        "title": "SIWES questions",
        "messages": [
            ("user", "What is SIWES and when do I do it?"),
            ("assistant", "SIWES (Student Industrial Work Experience Scheme) is a mandatory industrial attachment for relevant programmes, typically completed between ND II and HND I and lasting about a year. I don't have the Computer Science department's specific SIWES coordinator contact confirmed — ask the department office directly for placement procedures."),
        ],
    },
    {
        "title": "Big O explanation",
        "messages": [
            ("user", "What's the difference between O(n) and O(log n)?"),
            ("assistant", "O(n) means the runtime grows linearly with input size — double the input, roughly double the time (like scanning a list once). O(log n) means the runtime grows much more slowly — the algorithm cuts the problem in half each step (like binary search on a sorted array). For 1,000,000 items, O(n) might mean 1,000,000 steps, while O(log n) means only about 20 steps."),
        ],
    },
    {
        "title": "Hostel accommodation question",
        "messages": [
            ("user", "Is there hostel accommodation available?"),
            ("assistant", "On-campus hostels are listed among the Polytechnic's facilities, but I don't have confirmed details on the allocation process or cost. Check the current session's admission/registration information or ask Student Affairs directly."),
        ],
    },
]


async def get_or_create_user(db, data: dict, role: UserRole, department_id) -> User:
    result = await db.execute(select(User).where(User.email == data["email"]))
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(
        email=data["email"],
        username=data["username"],
        hashed_password=hash_password("DemoPass123!"),
        full_name=data["full_name"],
        role=role,
        status=AccountStatus.ACTIVE,
        is_email_verified=True,
        matric_number=data.get("matric_number"),
        department_id=department_id,
    )
    db.add(user)
    await db.flush()
    return user


async def seed_demo() -> None:
    async with AsyncSessionLocal() as db:
        dept_result = await db.execute(select(Department).where(Department.name == "Computer Science"))
        department = dept_result.scalar_one_or_none()
        if not department:
            print("No Computer Science department found — run scripts/seed.py first.")
            return

        # --- Courses ---
        existing_codes = {row[0] for row in (await db.execute(select(Course.code))).all()}
        for c in DEMO_COURSES:
            if c["code"] in existing_codes:
                continue
            db.add(Course(department_id=department.id, **c))
        await db.flush()

        # --- Lecturers ---
        existing_lecturer_names = {row[0] for row in (await db.execute(select(Lecturer.full_name))).all()}
        for lect in DEMO_LECTURERS:
            if lect["full_name"] in existing_lecturer_names:
                continue
            db.add(Lecturer(department_id=department.id, **lect))
        await db.flush()

        # --- Students ---
        students = [await get_or_create_user(db, s, UserRole.STUDENT, department.id) for s in DEMO_STUDENTS]
        await db.flush()

        # --- Announcements (from DS-003) ---
        existing_titles = {row[0] for row in (await db.execute(select(Announcement.title))).all()}
        for a in _load_json("announcements.json"):
            if a["title"] in existing_titles:
                continue
            db.add(
                Announcement(
                    title=a["title"],
                    content=a["content"],
                    audience=a["audience"],
                    priority=AnnouncementPriority(a["priority"]),
                    status=ContentStatus(a["status"]),
                    is_pinned=a["is_pinned"],
                )
            )

        # --- Events (from DS-003) ---
        existing_event_titles = {row[0] for row in (await db.execute(select(Event.title))).all()}
        now = datetime.now(timezone.utc)
        for e in _load_json("events.json"):
            if e["title"] in existing_event_titles:
                continue
            db.add(
                Event(
                    title=e["title"],
                    description=e["description"],
                    venue=e["venue"],
                    organizer=e["organizer"],
                    start_time=now + timedelta(days=e["days_from_now"]),
                )
            )
        await db.flush()

        # --- Conversations with realistic, backdated messages ---
        existing_conv_titles = {row[0] for row in (await db.execute(select(Conversation.title))).all()}
        providers = ["mock", "mock", "mock"]  # demo data assumes the default mock provider
        for i, convo_data in enumerate(DEMO_CONVERSATIONS):
            if convo_data["title"] in existing_conv_titles:
                continue
            student = random.choice(students)
            days_ago = random.randint(0, 13)
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            conversation = Conversation(
                user_id=student.id,
                title=convo_data["title"],
                ai_provider_used=random.choice(providers),
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(conversation)
            await db.flush()

            for role, content in convo_data["messages"]:
                db.add(
                    Message(
                        conversation_id=conversation.id,
                        role=MessageRole(role),
                        content=content,
                        response_time_ms=random.randint(120, 450) if role == "assistant" else None,
                        created_at=created_at,
                    )
                )
            db.add(
                AnalyticsEvent(
                    event_type="message_sent",
                    user_id=student.id,
                    metadata_json={"provider": conversation.ai_provider_used},
                    created_at=created_at,
                )
            )

        await db.flush()

        # --- Feedback (from DS-003) ---
        existing_feedback_count = (await db.execute(select(Feedback.id))).all()
        if len(existing_feedback_count) == 0:
            for fb in _load_json("feedback.json"):
                db.add(
                    Feedback(
                        user_id=random.choice(students).id,
                        rating=fb["rating"],
                        category=fb["category"],
                        comment=fb["comment"],
                        created_at=now - timedelta(days=random.randint(0, 20)),
                    )
                )

        await db.commit()
        print("Demo mode seed complete:")
        print(f"  - {len(DEMO_STUDENTS)} demo students (password: DemoPass123!)")
        print(f"  - {len(DEMO_LECTURERS)} demo lecturers")
        print(f"  - {len(DEMO_COURSES)} demo courses")
        print(f"  - {len(DEMO_CONVERSATIONS)} demo conversations with message history")
        print("  - Announcements, events, and feedback seeded from DS-003")


if __name__ == "__main__":
    asyncio.run(seed_demo())
