# COSIB Administrator Manual

For department administrators and super administrators.

## Accessing the admin portal

Log in with an administrator or super administrator account, then go to
`/admin` (or click **Admin** in the chat header — only visible to those
roles). Students and lecturers are redirected to a 403 page if they try
to access it directly.

## Roles at a glance

| Role | Can do |
|---|---|
| Student | Chat, view public content, manage own conversations, submit feedback |
| Lecturer | Everything a student can, plus publish announcements and manage events |
| Administrator | Manage users' status, courses, lecturers, knowledge base, FAQs, announcements, events, feedback, analytics, AI configuration, settings |
| Super Administrator | Everything an administrator can, plus change user roles, delete accounts, view audit logs |

`GET /api/v1/admin/roles` returns this same breakdown from the API if you
need it for onboarding new staff.

## Dashboard

Live counts (students, conversations, today's conversations, KB articles,
courses, announcements) and two charts: conversation volume over the last
14 days, and AI provider usage. Nothing here is simulated — an empty chart
means there's genuinely no data yet.

## Users

Search/filter by role, change a user's **status** (active / suspended /
deactivated / pending verification) as an administrator, change a user's
**role** or delete an account as a super administrator only.

## Knowledge Base & FAQs

Two tabs, same page. Articles are what COSIB searches first when
answering department questions — write them the way you'd want a student
to read them; COSIB injects the matching content directly into its
response. FAQs work the same way for quick Q&A-style content.

## Courses & Lecturers

Standard CRUD. Course creation requires a department (seeded
automatically — Computer Science).

## Announcements & Events

Create, pin (announcements), and delete. Published announcements appear
to all students/lecturers immediately.

## Feedback

Every rating and comment students submit, plus a summary (average
rating, positive/negative split, bug report count). Respond directly to
a submission — the student sees your response the next time they view
that feedback (in a future release; currently responses are stored and
visible to admins, with student-facing display planned).

## AI Configuration

Switch the active provider (mock / Gemini / OpenAI) with one click —
takes effect on the next message sent, no deploy needed. Tune
temperature, max tokens, streaming, and an optional system prompt
override per provider. The mock provider requires no API key and is
always available as a fallback if a real provider's key is missing or
invalid.

## System Settings

Key-value configuration: app name, logo URL, brand colors, support
email, maintenance mode. A subset (`app_name`, `app_logo_url`,
`primary_color`, `secondary_color`, `support_email`,
`maintenance_mode`) is exposed unauthenticated at
`GET /api/v1/settings/public` for frontend branding.

## Audit Logs

Read-only, super-admin only. Every role change, status change, and other
sensitive action is recorded with who, what, when, and from what IP.
Filter by action or user.

## Notifications

Administrators get an in-app notification when new feedback arrives.
(Additional triggers — upload failures, new registrations — use the same
`notify_admins()` service function and can be added without touching the
notification model or API.)
