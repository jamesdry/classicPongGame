import tkinter as tk
import random

APP_TITLE = "Classic Pong Game"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500

CANVAS_BG = "black"
CENTER_LINE_COLOR = "white"
TEXT_COLOR = "white"
HINT_COLOR = "#888888"

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

SCORE_OPTIONS = (10, 20, 30)

TITLE_FONT = ("Helvetica", 64, "bold")
SUBTITLE_FONT = ("Helvetica", 22)
BUTTON_FONT = ("Helvetica", 18, "bold")
SCORE_FONT = ("Helvetica", 40, "bold")
HINT_FONT = ("Helvetica", 11)

BUTTON_BG = "#222222"
BUTTON_FG = "white"
BUTTON_ACTIVE_BG = "#444444"


def make_button(parent, text, command, width=15):
    return tk.Button(
        parent, text=text, font=BUTTON_FONT, width=width,
        bg=BUTTON_BG, fg=BUTTON_FG,
        activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_FG,
        relief="flat", bd=0, cursor="hand2", command=command,
    )

class Paddle:
    def __init__(self, canvas, x, up_key, down_key):
        self.canvas = canvas
        self.x = x
        self.y = (WINDOW_HEIGHT - PADDLE_HEIGHT) // 2
        self.up_key = up_key
        self.down_key = down_key
        self.item = canvas.create_rectangle(
            self.x, self.y,
            self.x + PADDLE_WIDTH, self.y + PADDLE_HEIGHT,
            fill=PADDLE_COLOR, outline=PADDLE_COLOR,
        )

    @property
    def bbox(self):
        return (self.x, self.y, self.x + PADDLE_WIDTH, self.y + PADDLE_HEIGHT)

    def update(self, pressed_keys):
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
    def __init__(self, canvas):
        self.canvas = canvas
        self.radius = BALL_SIZE / 2
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.item = canvas.create_oval(0, 0, 0, 0, fill=BALL_COLOR, outline=BALL_COLOR)
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

class MainMenuFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=CANVAS_BG)
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="PONG", font=TITLE_FONT,
                 fg=TEXT_COLOR, bg=CANVAS_BG).pack(pady=(80, 40))
        make_button(self, "Play", self.app.show_score_select).pack(pady=10)
        make_button(self, "Quit", self.app.root.destroy).pack(pady=10)

class ScoreSelectFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=CANVAS_BG)
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Select Winning Score", font=SUBTITLE_FONT,
                 fg=TEXT_COLOR, bg=CANVAS_BG).pack(pady=(100, 40))

        options = tk.Frame(self, bg=CANVAS_BG)
        options.pack()
        for score in SCORE_OPTIONS:
            make_button(
                options, str(score),
                command=lambda s=score: self.app.start_game(s),
                width=6,
            ).pack(side="left", padx=10)

        make_button(self, "Back", self.app.show_main_menu).pack(pady=40)

class GameFrame(tk.Frame):
    def __init__(self, parent, app, target_score):
        super().__init__(parent, bg=CANVAS_BG)
        self.app = app
        self.target_score = target_score
        self.left_score = 0
        self.right_score = 0
        self.pressed_keys = set()
        self._after_id = None
        self._press_bind = None
        self._release_bind = None
        self._game_over = False
        self._winner = None

        self._build_canvas()
        self._create_entities()
        self._bind_events()
        self._start_loop()

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
            bg=CANVAS_BG, highlightthickness=0,
        )
        self.canvas.pack()

        mid_x = WINDOW_WIDTH // 2
        self.canvas.create_line(mid_x, 0, mid_x, WINDOW_HEIGHT,
                                fill=CENTER_LINE_COLOR, dash=(10, 10), width=2)

        self.left_score_text = self.canvas.create_text(
            mid_x - 80, 50, text="0", fill=TEXT_COLOR, font=SCORE_FONT)
        self.right_score_text = self.canvas.create_text(
            mid_x + 80, 50, text="0", fill=TEXT_COLOR, font=SCORE_FONT)

        self.canvas.create_text(
            mid_x, WINDOW_HEIGHT - 20,
            text=f"Left: W/S   |   Right: Up/Down   |   First to {self.target_score} wins",
            fill=HINT_COLOR, font=HINT_FONT,
        )

    def _create_entities(self):
        self.ball = Ball(self.canvas)
        left_x = PADDLE_MARGIN
        right_x = WINDOW_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH
        self.left_paddle = Paddle(self.canvas, left_x, "w", "s")
        self.right_paddle = Paddle(self.canvas, right_x, "up", "down")

    def _bind_events(self):
        self._press_bind = self.app.root.bind("<KeyPress>", self._on_key_press, add="+")
        self._release_bind = self.app.root.bind("<KeyRelease>", self._on_key_release, add="+")

    def _on_key_press(self, event):
        self.pressed_keys.add(event.keysym.lower())

    def _on_key_release(self, event):
        self.pressed_keys.discard(event.keysym.lower())

    def _start_loop(self):
        self._after_id = self.after(FRAME_DELAY_MS, self._tick)

    def _tick(self):
        self._after_id = None
        self._update()
        if self._game_over:
            self.app.show_game_over(
                self._winner, self.left_score, self.right_score, self.target_score
            )
            return
        self._after_id = self.after(FRAME_DELAY_MS, self._tick)

    def _update(self):
        self.left_paddle.update(self.pressed_keys)
        self.right_paddle.update(self.pressed_keys)
        self.ball.update()
        self._resolve_paddle_collisions()
        self._handle_out_of_bounds()

    def _resolve_paddle_collisions(self):
        if (self._boxes_overlap(self.ball.bbox, self.left_paddle.bbox)
                and self.ball.vx < 0):
            self.ball.vx = abs(self.ball.vx)
            self.ball.x = self.left_paddle.bbox[2] + self.ball.radius
            self.ball.sync()

        if (self._boxes_overlap(self.ball.bbox, self.right_paddle.bbox)
                and self.ball.vx > 0):
            self.ball.vx = -abs(self.ball.vx)
            self.ball.x = self.right_paddle.bbox[0] - self.ball.radius
            self.ball.sync()

    def _handle_out_of_bounds(self):
        if self.ball.bbox[2] < 0:
            self.right_score += 1
        elif self.ball.bbox[0] > WINDOW_WIDTH:
            self.left_score += 1
        else:
            return

        self._update_score_display()
        self._check_game_over()
        if not self._game_over:
            self.ball.reset()

    def _update_score_display(self):
        self.canvas.itemconfigure(self.left_score_text, text=str(self.left_score))
        self.canvas.itemconfigure(self.right_score_text, text=str(self.right_score))

    def _check_game_over(self):
        if self.left_score >= self.target_score:
            self._game_over = True
            self._winner = "Left Player"
        elif self.right_score >= self.target_score:
            self._game_over = True
            self._winner = "Right Player"

    def destroy(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        if self._press_bind:
            self.app.root.unbind("<KeyPress>", self._press_bind)
            self._press_bind = None
        if self._release_bind:
            self.app.root.unbind("<KeyRelease>", self._release_bind)
            self._release_bind = None
        super().destroy()

    @staticmethod
    def _boxes_overlap(a, b):
        return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]

class GameOverFrame(tk.Frame):
    def __init__(self, parent, app, winner, left_score, right_score, target_score):
        super().__init__(parent, bg=CANVAS_BG)
        self.app = app
        self.winner = winner
        self.left_score = left_score
        self.right_score = right_score
        self.target_score = target_score
        self._build()

    def _build(self):
        tk.Label(self, text="GAME OVER", font=TITLE_FONT,
                 fg=TEXT_COLOR, bg=CANVAS_BG).pack(pady=(70, 10))
        tk.Label(self, text=f"{self.winner} Wins!",
                 font=SUBTITLE_FONT, fg=TEXT_COLOR, bg=CANVAS_BG).pack(pady=10)
        tk.Label(self, text=f"{self.left_score}  -  {self.right_score}",
                 font=SCORE_FONT, fg=TEXT_COLOR, bg=CANVAS_BG).pack(pady=20)

        buttons = tk.Frame(self, bg=CANVAS_BG)
        buttons.pack(pady=30)
        make_button(
            buttons, "Play Again",
            command=lambda: self.app.start_game(self.target_score),
            width=12,
        ).pack(side="left", padx=10)
        make_button(
            buttons, "Main Menu",
            command=self.app.show_main_menu,
            width=12,
        ).pack(side="left", padx=10)

class PongApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.resizable(width=False, height=False)
        self.root.configure(bg=CANVAS_BG)
        self._center_window()

        self.container = tk.Frame(root, bg=CANVAS_BG)
        self.container.pack(fill="both", expand=True)

        self._current_screen = None
        self.show_main_menu()

    def _center_window(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WINDOW_WIDTH) // 2
        y = (screen_h - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _switch_screen(self, screen):
        if self._current_screen is not None:
            self._current_screen.destroy()
        self._current_screen = screen
        screen.pack(fill="both", expand=True)

    def show_main_menu(self):
        self._switch_screen(MainMenuFrame(self.container, self))

    def show_score_select(self):
        self._switch_screen(ScoreSelectFrame(self.container, self))

    def start_game(self, target_score):
        self._switch_screen(GameFrame(self.container, self, target_score))

    def show_game_over(self, winner, left_score, right_score, target_score):
        self._switch_screen(GameOverFrame(
            self.container, self, winner, left_score, right_score, target_score
        ))

def main():
    root = tk.Tk()
    PongApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()