from dataclasses import dataclass
from enum import Enum
from typing import Any


class WorkstationType(Enum):
    LAPTOP = "LAPTOP"
    DESKTOP = "DESKTOP"

@dataclass
class Workstation:
    id: int
    name: str
    type: WorkstationType
    occupied: bool

    @classmethod
    def from_poller(cls, d: dict) -> "Workstation":
        return cls(
            id=d["id"],
            name=d["name"],
            type=WorkstationType.LAPTOP if d["capacity"] == 1 else WorkstationType.DESKTOP,
            occupied=d["occupation"] > 0
        )

class MessageType(Enum):
    RESET = "reset" # payload = None
    CARD_SCANNED = "card_scanned" # payload = card_id: int
    API_STUDENT_NOT_FOUND = "api_student_not_found" # payload = None
    API_STUDENT_REQUIRES_RENEWAL = "api_student_requires_renewal"  # payload = None
    API_NO_ACTIVE_ENTRY = "api_no_active_entry" # payload = student_id: str
    API_ACTIVE_ENTRY_FOUND = "api_active_entry_found" # payload = entry_id: int
    API_WORKSTATION_UPDATE = "api_workstation_update" # payload = list[Workstation]
    WORKSTATION_CLICKED = "workstation_clicked" # payload = ws_id: int, ws_name: str, student_id: str
    CANCEL_SEAT_SELECTION = "cancel_seat_selection" # payload = None
    API_ERROR = "api_error" # payload = None

@dataclass(frozen=True)
class Message:
    type: MessageType
    payload: Any = None