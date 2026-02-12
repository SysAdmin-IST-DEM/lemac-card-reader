import logging
import queue
import threading
from enum import Enum
from time import sleep
from mfrc522 import SimpleMFRC522

from obj.objects import Message, MessageType

class CardScanned(Enum):
    NOT_SCANNED = 0
    STUDENT_NOT_FOUND = 1
    NO_ACTIVE_ENTRY = 2
    ACTIVE_ENTRY_FOUND = 3
    LOADING = 4

class CardScanner(threading.Thread):
    def __init__(self, events: queue.Queue, stop_event: threading.Event, ready_event: threading.Event):
        super().__init__()
        self.logger = logging.getLogger("CARD_SCANNER")
        self.events = events
        self.stop_event = stop_event
        self.ready_event = ready_event
        self.reader = SimpleMFRC522()
        self.logger.info(f"Starting Card Scanner...")

    def run(self):
        while not self.stop_event.is_set():
            self.ready_event.wait()
            if self.stop_event.is_set():
                break

            try:
                card_id = self.reader.read_id_no_block()

                if card_id:
                    if card_id > 0xFFFFFFFF:
                        card_id = card_id >> 8
                    self.events.put(Message(MessageType.CARD_SCANNED, int(card_id)))
                    self.logger.info(f"Scanned card ID: {card_id}")
                    self.stop_event.wait(0.7)
                else:
                    self.stop_event.wait(0.05)
            except Exception as e:
                self.logger.error(f"Card read failed: {e}")
                self.reader = SimpleMFRC522()
                self.logger.error("Reinitialized card reader after failure.")
        self.logger.info("CardScanner stopped.")