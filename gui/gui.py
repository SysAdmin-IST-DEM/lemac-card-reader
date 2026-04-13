import logging
import queue
import threading
import tkinter as tk

from PIL import Image, ImageTk
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

        # Draw DEM logo
        self.dem = get_resized_image("gui/images/dem.png", 0.13, screen_width, screen_height)
        self.canvas.create_image(10, 10, image=self.dem, anchor="nw")

        self.room_map = RoomMap(self.logger, self.events, self.canvas)

        self.canvas.tag_bind("click", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("click", "<Leave>", lambda e: self.canvas.config(cursor=""))

        self.canvas.create_text(10, screen_height - 10, text="v" + version, font=("Arial", 10),
                                fill="gray", anchor="sw")

        self.qrcode = get_resized_image("gui/images/qrcode.png", 0.1, screen_width, screen_height)
        self.qrcode_img = None

        self.arrow = get_resized_image("gui/images/arrow.png", 0.05, screen_width, screen_height)
        self.arrow_img = None

    def show_error(self, message):
        clear_screen(self.canvas)
        draw_center_text(self.canvas, message)

    def show_waiting(self):
        clear_screen(self.canvas)
        draw_center_text(self.canvas, "Waiting for card...")

        self.canvas.create_text(
            self.canvas.winfo_screenwidth() - 20 - self.qrcode.width() - self.arrow.width(),
            10 + self.qrcode.height() // 2,
            text="Student\nRegistration",
            font=("Arial", 13),
            fill="gray",
            justify="center",
            anchor="e",
            tags=("temp",)
        )

        self.arrow_img = self.canvas.create_image(
            self.canvas.winfo_screenwidth() - 10 - self.qrcode.width(),
            10 + self.qrcode.height() // 2,
            image=self.arrow,
            anchor="e",
            tags=("temp",)
        )
        self.qrcode_img = self.canvas.create_image(
            self.canvas.winfo_screenwidth() - 10,
            10,
            image=self.qrcode,
            anchor="ne",
            tags=("temp",)
        )

    def show_loading(self):
        clear_screen(self.canvas)
        draw_center_text(self.canvas, "Processing card...")

    def show_student_not_found(self):
        clear_screen(self.canvas)
        draw_title_subtitle(self.canvas, "Student not found",
                            "Please register your student card via LEMAC's website")

    def show_student_requires_renewal(self):
        clear_screen(self.canvas)
        draw_title_subtitle(self.canvas, "Renewal Required",
                            "Please renew your student registration via LEMAC's website")

    def show_card_assigning(self):
        clear_screen(self.canvas)
        draw_title_subtitle(self.canvas, "Card Scanned",
                            "After monitor's confirmation you can immediately start using your card")

    def show_room_map(self, workstation_data: list[Workstation], student_id: str):
        self.room_map.draw(workstation_data, student_id)

    def show_seat_reserved(self, ws_name: str):
        clear_screen(self.canvas)
        draw_title_subtitle(self.canvas, f"Seat {ws_name} reserved", "Please scan card on exit")

    def show_entry_closed(self):
        clear_screen(self.canvas)
        draw_title_subtitle(self.canvas, "Entry Closed", "Thank you for your visit")

    def on_close(self):
        self.stop_event.set()
        self.ready_event.set()
        self.root.destroy()


def clear_screen(canvas):
    canvas.config(cursor="none")
    canvas.delete("temp")


def draw_center_text(canvas, text):
    canvas.create_text(
        canvas.winfo_width() // 2,
        canvas.winfo_height() // 2,
        text=text,
        font=("Arial", 32),
        fill="gray",
        tags=("temp",)
    )


def draw_title_subtitle(canvas, title, subtitle):
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


def get_resized_image(path: str, ratio: float, screen_width: int, screen_height: int) -> ImageTk.PhotoImage:
    image = Image.open(path)
    new_width = int(screen_width * ratio)
    w_percent = (new_width / float(image.size[0]))
    new_height = int((float(image.size[1]) * float(w_percent)))
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized_image)