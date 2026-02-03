import logging
import threading, queue
from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests

from api_clients.students import fetch_active_entry, close_entry, add_entry
from obj.objects import Message, MessageType


class ApiJobType(Enum):
    FETCH_ACTIVE_ENTRY = "fetch_active_entry" # payload: card_id
    ADD_ENTRY = "add_entry" # payload: ws_id, student_id
    CLOSE_ENTRY = "close_entry" # payload: entry_id

@dataclass(frozen=True)
class ApiJob:
    type: ApiJobType
    payload: Any # card_id or entry_id or workstation_id depending on job type

class ApiWorker(threading.Thread):
    def __init__(self, events: queue.Queue, api_events: queue.Queue, stop_event: threading.Event):
        super().__init__()
        self.logger = logging.getLogger("API_WORKER")
        self.events = events
        self.api_events = api_events
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                event = self.api_events.get(timeout=0.2)
                self.handle_event(event)
            except queue.Empty:
                continue
        self.logger.info("ApiWorker stopped.")

    def handle_event(self, event: ApiJob):
        self.logger.debug(f"Handling event: {event.type}")
        try:
            if event.type == ApiJobType.FETCH_ACTIVE_ENTRY:
                response = fetch_active_entry(event.payload)
                response.raise_for_status()
                response = response.json()
                self.logger.debug(f"API Response: {response}")
                self.logger.info("Fetched active entry from API successfully. CODE: " + response["code"])
                if response["code"] == "STUDENT_NOT_FOUND":
                    self.events.put(Message(MessageType.API_STUDENT_NOT_FOUND))
                elif response["code"] == "STUDENT_REQUIRES_RENEWAL":
                    self.events.put(Message(MessageType.API_STUDENT_REQUIRES_RENEWAL))
                elif response["code"] == "NO_ACTIVE_ENTRY":
                    self.events.put(Message(MessageType.API_NO_ACTIVE_ENTRY, response["student"]["istId"]))
                elif response["code"] == "ACTIVE_ENTRY_FOUND":
                    self.events.put(Message(MessageType.API_ACTIVE_ENTRY_FOUND, response["entry"]["id"]))
            elif event.type == ApiJobType.ADD_ENTRY:
                response = add_entry(event.payload["student_id"], event.payload["ws_id"])
                response.raise_for_status()
                self.logger.info("Added entry to API successfully.")
            elif event.type == ApiJobType.CLOSE_ENTRY:
                response = close_entry(event.payload)
                response.raise_for_status()
                self.logger.info("Closed entry from API successfully.")
        except Exception as err:
            self.logger.error(f"Failed to execute API job with error: {err}")
            self.events.put(Message(MessageType.API_ERROR))