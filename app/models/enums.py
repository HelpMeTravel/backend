import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class RuleStatus(str, enum.Enum):
    DRAFT = "draft"
    NOT_PUBLISHED = "notPublished"
    PUBLISHED = "published"
    REJECTED = "rejected"