import logging
import queue
import threading

import requests

from config import BASE_API_URL
from obj.objects import Workstation, Message, MessageType


class WorkstationPoller(threading.Thread):
    def __init__(self, events: queue.Queue, stop_event: threading.Event, interval: int):
        super().__init__()
        self.logger = logging.getLogger("WORKSTATION_POLLER")
        self.events = events
        self.stop_event = stop_event
        self.interval = interval
        self.data: list[Workstation] = []
        self.raw_json = []

    def run(self):
        while not self.stop_event.is_set():
            try:
                self.logger.debug("Fetching workstations from API...")
                response = requests.get(BASE_API_URL + "workstations")
                response.raise_for_status()
                json = response.json()
                if self.raw_json != json:
                    self.data = [Workstation.from_poller(ws) for ws in json]
                    self.raw_json = json
                    self.logger.info(f"Updated {len(self.data)} workstations.")
            except Exception as err:
                self.logger.error(f"Failed to fetch workstations from API with error: ${err}")
                self.data = None
                self.raw_json = None

            self.events.put(Message(MessageType.API_WORKSTATION_UPDATE, self.data))
            self.stop_event.wait(self.interval)
        self.logger.info("Workstation poller stopped.")