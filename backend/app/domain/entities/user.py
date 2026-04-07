from dataclasses import dataclass


@dataclass
class UserEntity:
    """An application user with a role."""
    user_id: str
    username: str
    role: str = "instructor"

    @classmethod
    def from_dict(cls, d: dict) -> "UserEntity":
        return cls(
            user_id=d.get("user_id") or d.get("id", ""),
            username=d["username"],
            role=d.get("role", "instructor"),
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
        }
