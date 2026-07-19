"""
Shared enum types used across ORM models.
"""
import enum


class UserRole(str, enum.Enum):
    GUEST = "guest"
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "administrator"
    SUPER_ADMIN = "super_administrator"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    PENDING_VERIFICATION = "pending_verification"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AnnouncementPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIProviderName(str, enum.Enum):
    MOCK = "mock"
    GEMINI = "gemini"
    OPENAI = "openai"


class NotificationType(str, enum.Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
