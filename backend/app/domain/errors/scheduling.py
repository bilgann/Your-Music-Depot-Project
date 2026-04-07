"""
Scheduling domain error codes and default messages.

Covers instructor and room availability conflicts.
"""

INSTRUCTOR_UNAVAILABLE = "INSTRUCTOR_UNAVAILABLE"
ROOM_UNAVAILABLE       = "ROOM_UNAVAILABLE"

MESSAGES: dict[str, str] = {
    INSTRUCTOR_UNAVAILABLE: "The instructor is unavailable during the requested time.",
    ROOM_UNAVAILABLE:       "The room is unavailable during the requested time.",
}
