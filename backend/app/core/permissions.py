"""
Permission layer sitting on top of the enum-based role system.

Today, "permissions" are just a documentation/introspection mapping over
UserRole — actual enforcement still happens via `require_roles` in
app.core.deps, checked directly against `User.role`. That's intentional:
role checks in route signatures are explicit and easy to audit.

This module exists so that if a future version needs granular, per-user
permission overrides, the migration path is:
  1. Add a Permission / UserPermission table (or a permissions JSON column on User).
  2. Change `get_role_permissions()` below to query it instead of returning
     the static ROLE_PERMISSIONS dict (falling back to it for roles with no
     override).
  3. Optionally add a `require_permission("resource.action")` dependency
     that calls `get_role_permissions()` instead of comparing roles directly.
No route files need to change for step 1-2; only this module does.
"""
from app.models.enums import UserRole

# Permission strings follow "resource.action" convention so a future
# granular system can check them individually rather than by role.
ROLE_PERMISSIONS: dict[str, list[str]] = {
    UserRole.GUEST.value: [
        "landing.view",
        "auth.login",
        "auth.register",
    ],
    UserRole.STUDENT.value: [
        "chat.use",
        "announcements.view",
        "courses.view",
        "lecturers.view",
        "events.view",
        "profile.manage_own",
        "conversations.manage_own",
        "feedback.submit",
        "documents.analyze",
    ],
    UserRole.LECTURER.value: [
        "announcements.publish",
        "events.manage",
    ],
    UserRole.ADMIN.value: [
        "users.manage_status",
        "courses.manage",
        "lecturers.manage",
        "knowledge_base.manage",
        "faqs.manage",
        "announcements.manage",
        "events.manage",
        "analytics.view",
        "feedback.manage",
        "ai_config.manage",
        "settings.manage",
    ],
    UserRole.SUPER_ADMIN.value: [
        "users.manage_role",
        "users.delete",
        "audit_logs.view",
    ],
}

# Higher roles inherit everything granted to the roles below them.
ROLE_HIERARCHY: list[str] = [
    UserRole.GUEST.value,
    UserRole.STUDENT.value,
    UserRole.LECTURER.value,
    UserRole.ADMIN.value,
    UserRole.SUPER_ADMIN.value,
]


def get_role_permissions(role: str) -> list[str]:
    """
    Returns every permission a role has, including inherited ones from
    lower roles in the hierarchy.

    This is the one function to change if permissions ever move to a
    database table — everything else (require_roles-based route guards,
    the /admin/roles endpoint) can keep calling this function unchanged.
    """
    if role not in ROLE_HIERARCHY:
        return []
    granted: list[str] = []
    for r in ROLE_HIERARCHY[: ROLE_HIERARCHY.index(role) + 1]:
        granted.extend(ROLE_PERMISSIONS.get(r, []))
    return granted


def role_has_permission(role: str, permission: str) -> bool:
    return permission in get_role_permissions(role)
