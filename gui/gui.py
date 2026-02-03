import logging
import queue
import threading
import tkinter as tk

from gui.room_map import RoomMap
from obj.objects import Workstation


class AppGui:
    def __init__(self, root: tk.Tk, events: queue.Queue, stop_event: threading.Event, ready_event: threading.Event,
                 version: str):
        self.logger = logging.getLogger("GUI")

        self.root = root
        self.events = events
        self.stop_event = stop_event
        self.ready_event = ready_event

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.title("Workstation Monitor")
        self.root.attributes("-fullscreen", True)
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = tk.PhotoImage(file="gui/images/dem.png")
        self.canvas.create_image(10, 10, image=self.image, anchor="nw")

        self.room_map = RoomMap(self.logger, self.events, self.canvas)

        self.canvas.tag_bind("click", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("click", "<Leave>", lambda e: self.canvas.config(cursor=""))

        self.canvas.create_text(10, screen_height - 10, text="v" + version, font=("Arial", 10),
                                fill="gray", anchor="sw")

    def show_error(self, message):
        draw_center_text(self.canvas, message)

    def show_waiting(self):
        draw_center_text(self.canvas, "Waiting for card...")

    def show_loading(self):
        draw_center_text(self.canvas, "Processing card...")

    def show_student_not_found(self):
        draw_title_subtitle(self.canvas, "Student not found",
                            "Please register your student card via LEMAC's website")

    def show_student_requires_renewal(self):
        draw_title_subtitle(self.canvas, "Renewal Required",
                            "Please renew your student registration via LEMAC's website")

    def show_room_map(self, workstation_data: list[Workstation], student_id: str):
        self.room_map.draw(workstation_data, student_id)

    def show_seat_reserved(self, ws_name: str):
        draw_title_subtitle(self.canvas, f"Seat {ws_name} reserved", "Please scan card on exit")

    def show_entry_closed(self):
        draw_title_subtitle(self.canvas, "Entry Closed", "Thank you for your visit")

    def on_close(self):
        self.stop_event.set()
        self.ready_event.set()
        self.root.destroy()


def draw_center_text(canvas, text):
    canvas.config(cursor="none")
    canvas.delete("temp")
    canvas.create_text(
        canvas.winfo_width() // 2,
        canvas.winfo_height() // 2,
        text=text,
        font=("Arial", 32),
        fill="gray",
        tags=("temp",)
    )

def draw_title_subtitle(canvas, title, subtitle):
    canvas.config(cursor="none")
    canvas.delete("temp")
    canvas.create_text(
            canvas.winfo_width() // 2,
            canvas.winfo_height() // 2,
            text=title,
            font=("Arial", 32),
            fill="gray",
            anchor="s",
            tags=("temp",)
        )
    canvas.create_text(
        canvas.winfo_width() // 2,
        canvas.winfo_height() // 2 + 5,
        text=subtitle,
        font=("Arial", 22),
        fill="gray",
        anchor="n",
        tags=("temp",)
    )