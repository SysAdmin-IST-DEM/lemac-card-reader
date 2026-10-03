import logging
import queue
import threading
from enum import Enum

try:
    from pn532pi import Pn532Spi, PN532
    from pn532pi import pn532
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False

from obj.objects import Message, MessageType

class CardScanned(Enum):
    NOT_SCANNED = 0
    STUDENT_NOT_FOUND = 1
    NO_ACTIVE_ENTRY = 2
    ACTIVE_ENTRY_FOUND = 3
    LOADING = 4

class CardScanner(threading.Thread):
    def __init__(self, events: queue.Queue, stop_event: threading.Event, ready_event: threading.Event):
        global HAS_HARDWARE
        super().__init__()
        self.logger = logging.getLogger("CARD_SCANNER")
        self.logger.info(f"Starting Card Scanner...")
        self.events = events
        self.stop_event = stop_event
        self.ready_event = ready_event

        if HAS_HARDWARE:
            try:
                spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
                self.reader = PN532(spi)
                self.reader.begin()

                versiondata = self.reader.getFirmwareVersion()
                if not versiondata:
                    raise RuntimeError("PN532 chip not found via SPI.")
                self.logger.info("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF,
                                                                                       (versiondata >> 16) & 0xFF,
                                                                                       (versiondata >> 8) & 0xFF))

                self.reader.SAMConfig()
                self.logger.info("PN532 reader initialized successfully over SPI.")
            except Exception as e:
                self.logger.error(f"Failed to initialize PN532 hardware: {e}")
                HAS_HARDWARE = False
        else:
            self.logger.warning("mfrc522 hardware not found. CardScanner will be disabled.")


    def run(self):
        if not HAS_HARDWARE or not self.reader:
            return

        while not self.stop_event.is_set():
            self.ready_event.wait()
            if self.stop_event.is_set():
                break

            try:
                success, uid = self.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS, timeout=50)

                if success and uid:
                    card_id = int.from_bytes(uid, byteorder='big')

                    if card_id > 0xFFFFFFFF:
                        card_id = card_id >> 8

                    self.events.put(Message(MessageType.CARD_SCANNED, card_id))
                    self.logger.info(f"Scanned card ID: {card_id} (UID Hex: {uid.hex().upper()})")
                    self.stop_event.wait(0.7)
                else:
                    self.stop_event.wait(0.05)
            except Exception as e:
                self.logger.error(f"Card read failed: {e}")
                spi = Pn532Spi(Pn532Spi.SS0_GPIO8)
                self.reader = PN532(spi)
                self.reader.begin()
                self.reader.SAMConfig()
                self.logger.info("Reinitialized PN532 card reader after failure.")
        self.logger.info("CardScanner stopped.")