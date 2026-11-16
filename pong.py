import tkinter as tk

APP_TITLE = "Classic Pong Game"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
CANVAS_BG = "black"
CENTER_LINE_COLOR = "white"

class PongGame:
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        self._setup_canvas()

    def _setup_window(self):
        self.root.title(APP_TITLE)
        self.root.resizable(width=False, height=False)
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WINDOW_WIDTH) // 2
        y = (screen_h - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _setup_canvas(self):
        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=CANVAS_BG,
            highlightthickness=0
        )
        self.canvas.pack()
        self._draw_center_line()

    def _draw_center_line(self):
        mid_x = WINDOW_WIDTH // 2
        self.canvas.create_line(
            mid_x, 0,
            mid_x, WINDOW_HEIGHT,
            fill=CENTER_LINE_COLOR,
            dash=(10, 10),
            width=2
        )
    
def main():
    root = tk.Tk()
    PongGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()