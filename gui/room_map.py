import logging
import queue
from tkinter import Canvas

from obj.objects import Workstation, WorkstationType, Message, MessageType

BOX_SIZE = 60
GRID = [
    [('30', '28'), ('26', '24'), ('22', '20'), ('18', '16'), ('14', '12'), ('10', '7')],
    [('29', '27'), ('25', '23'), ('21', '19'), ('17', '15'), ('13', '11'), ('9', '6')],
    [('0', '0'), ('0', '0'), ('0', '0'), ('0', '0'), ('0', '0'), ('8', '5')],
    [('0', '0'), ('0', '0'), ('0', '0'), ('0', '0'), ('0', '0'), ('0', '0')],
    [('31', '33'), ('35', '37'), ('0', '0'), ('0', '0'), ('0', '0'), ('4', '2')],
    [('32', '34'), ('36', '38'), ('0', '0'), ('0', '0'), ('D', 'D'), ('3', '1')]
]

class RoomMap:
    def __init__(self, logger: logging.Logger, events: queue.Queue, canvas: Canvas):
        self.logger = logger
        self.events = events
        self.canvas = canvas

    def draw(self, workstations: list[Workstation], student_id: str):
        self.canvas.config(cursor="")
        stations = {str(ws.name): ws for ws in workstations}

        self.canvas.delete("temp")

        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            40,
            text="Choose a seat",
            font=("Arial", 28),
            fill="black",
            tags=("temp",)
        )
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            75,
            text="Student: " + student_id,
            font=("Arial", 20),
            fill="gray",
            tags=("temp",)
        )
        self._draw_workstations(stations, student_id)

        cancel = self.canvas.create_text(
            self.canvas.winfo_width() - 20,
            20,
            text="X",
            font=("Arial", 20),
            fill="gray",
            anchor="ne",
            tags=("temp", "click")
        )
        self.canvas.tag_bind(cancel, "<Button>", lambda event: self.events.put(Message(MessageType.CANCEL_SEAT_SELECTION)))

    def _draw_workstations(self, stations: dict[str, Workstation], student_id: str):
        cluster_width = BOX_SIZE + 20 + BOX_SIZE
        total_spacing = 50 * (len(GRID[0]) - 1)
        total_width = cluster_width * len(GRID[0]) + total_spacing
        x_start = (self.canvas.winfo_width() - total_width) / 2

        x = x_start
        y = 150

        for row in GRID:
            for left, right in row:
                if left == 'D':
                    self.canvas.create_line(x, y + BOX_SIZE, x + BOX_SIZE, y + BOX_SIZE, tags=("temp",))
                elif left != '0':
                    ws_left = stations[left]
                    self._draw_workstation(ws_left, x, y, student_id)

                x = x + BOX_SIZE + 20

                if right == 'D':
                    self.canvas.create_line(x, y + BOX_SIZE, x + BOX_SIZE, y + BOX_SIZE, tags=("temp",))
                elif right != '0':
                    ws_right = stations[right]
                    self._draw_workstation(ws_right, x, y, student_id)

                x = x + BOX_SIZE + 50
            x = x_start
            y = y + BOX_SIZE + 50

        self._draw_captions(y)

        return x, y

    def _draw_captions(self, y_start: int):
        # Draw captions
        y_cap = y_start + BOX_SIZE
        x_cap_1 = int(self.canvas.winfo_width() / 2 - BOX_SIZE * 1.5)
        x_cap_2 = int(self.canvas.winfo_width() / 2)
        x_cap_3 = int(self.canvas.winfo_width() / 2 + BOX_SIZE * 1.5)

        # Caption Laptop
        self._draw_workstation(Workstation(-1, "LTI-PC", WorkstationType.DESKTOP, False),
                               x_cap_1, y_cap, None)
        self.canvas.create_text(
            x_cap_1 + BOX_SIZE / 2,
            y_cap + BOX_SIZE + 20,
            text="Laptop",
            font=("Arial", 13),
            anchor="center",
            tags=("temp",)
        )

        # Caption Desktop
        self._draw_workstation(Workstation(-1, "LTI-PC", WorkstationType.LAPTOP, False),
                               x_cap_2, y_cap, None)
        self.canvas.create_text(
            x_cap_2 + BOX_SIZE / 2,
            y_cap + BOX_SIZE + 20,
            text="Desktop",
            font=("Arial", 13),
            anchor="center",
            tags=("temp",)
        )

        # Caption Occupied
        self._draw_workstation(Workstation(-1, "LTI-PC", WorkstationType.DESKTOP, True),
                               x_cap_3, y_cap, None)
        self.canvas.create_text(
            x_cap_3 + BOX_SIZE / 2,
            y_cap + BOX_SIZE + 20,
            text="Occupied",
            font=("Arial", 13),
            anchor="center",
            tags=("temp",)
        )
        return x_cap_1, y_cap

    def _draw_workstation(self, ws: Workstation, x: int, y: int, student_id: str | None):
        x2 = x + BOX_SIZE
        y2 = y + BOX_SIZE

        if ws.occupied:
            fill_color = "#F7825B"
        elif ws.type == WorkstationType.DESKTOP:
            fill_color = "#A0E89C"
        elif ws.type == WorkstationType.LAPTOP:
            fill_color = "#5ABC9D"
        else:
            fill_color = "#D3D3D3"

        tag = f"ws_{ws.name}"
        tag_click = "click" if student_id is not None else ""

        self.canvas.create_rectangle(x, y, x2, y2, fill=fill_color, outline="black", tags=("temp", tag_click, tag,))
        self.canvas.create_text((x + x2) / 2, (y + y2) / 2, text=str(ws.name), font=("Arial", 12), tags=("temp", tag_click, tag,))

        if student_id is not None: self.canvas.tag_bind(tag, "<Button>", lambda event: self._on_ws_click(ws, student_id))

    def _on_ws_click(self, ws: Workstation, student_id: str):
        self.logger.debug("The Workstation " + ws.name + " was clicked.")
        if ws.occupied:
            return

        self.events.put(Message(MessageType.WORKSTATION_CLICKED, {"ws_id": ws.id, "ws_name": ws.name, "student_id": student_id}))
