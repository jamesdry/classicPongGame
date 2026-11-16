import tkinter as tk
import random

APP_TITLE = "Classic Pong Game"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
CANVAS_BG = "black"
CENTER_LINE_COLOR = "white"

FPS = 60
FRAME_DELAY_MS = 1000 // FPS

PADDLE_WIDTH = 12
PADDLE_HEIGHT = 80
PADDLE_MARGIN = 20
PADDLE_SPEED = 7
PADDLE_COLOR = "white"

BALL_SIZE = 14
BALL_SPEED_X = 5
BALL_SPEED_Y = 4
BALL_COLOR = "white"

class Paddle:

    def __init__(self, canvas: tk.Canvas, x: int, up_key: str, down_key: str):
        self.canvas = canvas
        self.x = x
        self.y = (WINDOW_HEIGHT - PADDLE_HEIGHT) // 2
        self.up_key = up_key
        self.down_key = down_key
        self.item = canvas.create_rectangle(
            self.x, self.y,
            self.x + PADDLE_WIDTH, self.y + PADDLE_HEIGHT,
            fill=PADDLE_COLOR, outline=PADDLE_COLOR
        )

    @property
    def bbox(self):
        return (self.x, self.y, self.x + PADDLE_WIDTH, self.y + PADDLE_HEIGHT)

    def update(self, pressed_keys: set):
        dy = 0
        
        if self.up_key in pressed_keys:
            dy -= PADDLE_SPEED
        if self.down_key in pressed_keys:
            dy += PADDLE_SPEED
        if dy == 0:
            return

        self.y = max(0, min(WINDOW_HEIGHT - PADDLE_HEIGHT, self.y + dy))
        self.canvas.coords(self.item, *self.bbox)

class Ball:

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.radius = BALL_SIZE / 2
        self.x = WINDOW_WIDTH / 2
        self.y = WINDOW_HEIGHT / 2
        self.vx = 0.0
        self.vy = 0.0 
        self.item = canvas.create_oval(
            0, 0, 0, 0, fill=BALL_COLOR, outline=BALL_COLOR
        )
        self.reset()

    @property
    def bbox(self):
        r = self.radius
        return (self.x - r, self.y - r, self.x + r, self.y + r)

    def reset(self):
        self.x = WINDOW_WIDTH / 2
        self.y = WINDOW_HEIGHT / 2
        self.vx = BALL_SPEED_X * random.choice((-1, 1))
        self.vy = BALL_SPEED_Y * random.choice((-1, 1))
        self.sync()

    def update(self):
        self.x += self.vx
        self.y += self.vy

        r = self.radius

        if self.y - r <= 0:
            self.y = r
            self.vy = abs(self.vy)
        elif self.y + r >= WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - r
            self.vy = -abs(self.vy)
        self.sync()

    def sync(self):
        self.canvas.coords(self.item, *self.bbox)

class PongGame:
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.pressed_keys = set()
        self._setup_window()
        self._setup_canvas()
        self._create_entities()
        self._bind_events()
        self._game_loop()

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

    def _create_entities(self):
        self.ball = Ball(self.canvas)

        left_x = PADDLE_MARGIN
        right_x = WINDOW_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH

        self.left_paddle = Paddle(self.canvas, left_x, "w", "s")
        self.right_paddle = Paddle(self.canvas, right_x, "up", "down")

    def _bind_events(self):
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.focus_set()

    def _on_key_press(self, event: tk.Event):
        self.pressed_keys.add(event.keysym.lower())

    def _on_key_release(self, event: tk.Event):
        self.pressed_keys.discard(event.keysym.lower())

    def _game_loop(self):
        self._update()
        self.root.after(FRAME_DELAY_MS, self._game_loop)

    def _update(self):
        self.left_paddle.update(self.pressed_keys)
        self.right_paddle.update(self.pressed_keys)
        self.ball.update()
        self._resolve_paddle_collisions()
        self._handle_out_of_bounds()

    def _resolve_paddle_collisions(self):

        if self._boxes_overlap(self.ball.bbox, self.left_paddle.bbox):
            if self.ball.vx < 0:
                self.ball.vx = abs(self.ball.vx)
                self.ball.x = self.left_paddle.bbox[2] + self.ball.radius
                self.ball.sync()

        if self._boxes_overlap(self.ball.bbox, self.right_paddle.bbox):
            if self.ball.vx > 0:
                self.ball.vx = -abs(self.ball.vx)
                self.ball.x = self.right_paddle.bbox[0] - self.ball.radius
                self.ball.sync()

    def _handle_out_of_bounds(self):
        if self.ball.bbox[2] < 0 or self.ball.bbox[0] > WINDOW_WIDTH:
            self.ball.reset()

    @staticmethod
    def _boxes_overlap(a: tuple, b: tuple):
        return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]
    
def main():
    root = tk.Tk()
    PongGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()