import logging
import queue
import sys
import threading
import tkinter as tk

from api_clients.ApiWorker import ApiWorker, ApiJobType, ApiJob
from api_clients.workstations import WorkstationPoller
from config import VERSION
from pi.card_reader import CardScanner
from gui.gui import AppGui
from obj.objects import Workstation, Message, MessageType
import pi.sounds as sounds

class App:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG if "--debug" in sys.argv else logging.INFO,
                            format='%(asctime)s [%(name)s] - %(levelname)s - %(message)s',
                            datefmt="%H:%M:%S",
                            handlers=[
                                logging.StreamHandler()
                            ])
        self.logger = logging.getLogger("LEMAC")
        self.logger.info("Initializing LEMAC Application")

        self.events = queue.Queue()
        self.api_events = queue.Queue()
        self.stop_event = threading.Event()
        self.ready_event = threading.Event()

        self.root = tk.Tk()
        self.gui = AppGui(self.root, self.events, self.stop_event, self.ready_event, VERSION)

        self.api_worker = ApiWorker(self.events, self.api_events, self.stop_event)

        self.workstation_store: list[Workstation] = []
        self.workstation_poller = WorkstationPoller(self.events, self.stop_event, 5)

        self.card_reader = CardScanner(self.events, self.stop_event, self.ready_event)

        self.out_of_service = False

    def start(self):
        self.workstation_poller.start()
        self.api_worker.start()
        self.card_reader.start()

        self.root.after(1000, lambda: self.events.put(Message(MessageType.RESET)))

        self.root.after(0, self.process_events)

        self.logger.info("All systems go. Starting main loop.")
        self.root.mainloop()

    def process_events(self):
        try:
            while True:
                msg: Message = self.events.get_nowait()

                if self.out_of_service and msg.type != MessageType.API_WORKSTATION_UPDATE:
                    continue

                if msg.type == MessageType.RESET or msg.type == MessageType.CANCEL_SEAT_SELECTION: # Reset
                    self.gui.show_waiting()
                    self.ready_event.set()
                elif msg.type == MessageType.CARD_SCANNED: # Card scanned. Payload: card_id
                    self.ready_event.clear()
                    self.gui.show_loading()
                    self.api_events.put(ApiJob(ApiJobType.FETCH_ACTIVE_ENTRY, msg.payload))
                    thread = threading.Thread(target=sounds.beep)
                    thread.start()
                elif msg.type == MessageType.API_STUDENT_NOT_FOUND: # Student not found. Payload: None
                    self.gui.show_student_not_found()
                    thread = threading.Thread(target=sounds.wrong)
                    thread.start()
                    self.root.after(3000, lambda: self.events.put(Message(MessageType.RESET)))
                elif msg.type == MessageType.API_STUDENT_REQUIRES_RENEWAL: # Student not found. Payload: None
                    self.gui.show_student_requires_renewal()
                    thread = threading.Thread(target=sounds.wrong)
                    thread.start()
                    self.root.after(3000, lambda: self.events.put(Message(MessageType.RESET)))
                elif msg.type == MessageType.API_NO_ACTIVE_ENTRY: # Show room map. Payload: student_id
                    self.gui.show_room_map(self.workstation_store, msg.payload)
                elif msg.type == MessageType.API_ACTIVE_ENTRY_FOUND: # Close entry. Payload: entry_id
                    self.api_events.put(ApiJob(ApiJobType.CLOSE_ENTRY, msg.payload))
                    self.gui.show_entry_closed()
                    thread = threading.Thread(target=sounds.pling)
                    thread.start()
                    self.root.after(3000, lambda: self.events.put(Message(MessageType.RESET)))
                elif msg.type == MessageType.API_WORKSTATION_UPDATE: # Workstation data update. Payload: list[Workstation]
                    self.workstation_store = msg.payload
                    if self.workstation_store is None and not self.out_of_service:
                        self.out_of_service = True
                        self.gui.show_error("Out of Service")
                        thread = threading.Thread(target=sounds.wrong)
                        thread.start()
                    elif self.workstation_store is not None and self.out_of_service:
                        self.out_of_service = False
                        self.events.put(Message(MessageType.RESET))
                elif msg.type == MessageType.WORKSTATION_CLICKED: # Reserve seat. Payload = ws_id, ws_name, student_id
                    self.gui.show_loading()
                    self.api_events.put(ApiJob(ApiJobType.ADD_ENTRY, msg.payload))
                    self.gui.show_seat_reserved(msg.payload["ws_name"])
                    thread = threading.Thread(target=sounds.pling)
                    thread.start()
                    self.root.after(3000, lambda: self.events.put(Message(MessageType.RESET)))
                elif msg.type == MessageType.API_ERROR:
                    self.gui.show_error("Unknown Error")
                    thread = threading.Thread(target=sounds.wrong)
                    thread.start()
                    self.root.after(3000, lambda: self.events.put(Message(MessageType.RESET)))



        except queue.Empty:
            pass
        self.root.after(100, self.process_events)

app = App()
app.start()