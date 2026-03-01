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
        self.logger.info(f"Starting Card Scanneself.reader...")

    def uid_to_formats(self, uid_bytes: bytes):
        return {
            "uid_bytes": " ".join(f"{b:02X}" for b in uid_bytes),
            "uid_hex": uid_bytes.hex(),
            "int_be": int.from_bytes(uid_bytes, "big"),
            "int_le": int.from_bytes(uid_bytes, "little"),
            "int_rev_be": int.from_bytes(uid_bytes[::-1], "big"),
        }

    def run(self):
        while not self.stop_event.is_set():
            self.ready_event.wait()
            if self.stop_event.is_set():
                break

            try:
                (status, tag_type) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
                if status != self.reader.MI_OK:
                    continue

                (status, uid) = self.reader.MFRC522_Anticoll()
                if status != self.reader.MI_OK:
                    continue

                uid4 = uid[:4]
                self.logger.error("UID:", " ".join(f"{b:02X}" for b in uid4))

                # EXEMPLO: autenticar e ler um bloco (tens de saber qual)
                block = 8
                key = [0xFF] * 6  # chave default (muito comum, mas não garantido)

                self.reader.MFRC522_SelectTag(uid)
                status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1A, block, key, uid)
                if status == self.reader.MI_OK:
                    data = self.reader.MFRC522_Read(block)
                    self.logger.error("BLOCK", block, ":", data)
                    self.reader.MFRC522_StopCrypto1()
                else:
                    self.logger.error("Auth failed")

                '''card_id = self.readeself.reader.read_id_no_block()

                if card_id:
                    if card_id > 0xFFFFFFFF:
                        card_id = card_id >> 8
                    self.events.put(Message(MessageType.CARD_SCANNED, card_id))
                    self.logger.info(f"Scanned card ID: {card_id}")
                    self.stop_event.wait(0.7)
                else:
                    self.stop_event.wait(0.05)'''
            except Exception as e:
                self.logger.error(f"Card read failed: {e}")
                self.reader = SimpleMFRC522()
                self.logger.error("Reinitialized card reader after failure.")
        self.logger.info("CardScanner stopped.")