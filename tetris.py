import tkinter as tk
import random
import pygame
import numpy as np

pygame.mixer.init()

def play_sound(freq=440, duration=0.1):
    try:
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate))
        buf = np.zeros((n_samples, 2), dtype=np.int16)
        max_amplitude = int(2**(15) - 1)
        t = np.linspace(0, duration, n_samples, False)
        wave = np.sin(2 * np.pi * freq * t) * max_amplitude
        buf[:, 0] = wave
        buf[:, 1] = wave
        sound = pygame.sndarray.make_sound(buf)
        sound.set_volume(0.1)
        sound.play()
    except Exception:
        pass

# Game constants
ROWS, COLS = 20, 10
CELL_SIZE = 30
GAME_WIDTH = COLS * CELL_SIZE
GAME_HEIGHT = ROWS * CELL_SIZE

COLORS = ['black', 'cyan', 'blue', 'orange', 'yellow', 'green', 'purple', 'red']
SHAPES = [
    [],
    [[(0,0),(0,1),(0,2),(0,3)], [(0,1),(1,1),(2,1),(3,1)]],
    [[(0,0),(1,0),(1,1),(1,2)], [(0,1),(0,2),(1,1),(2,1)], [(0,0),(0,1),(0,2),(1,2)], [(0,1),(1,1),(2,1),(2,0)]],
    [[(1,0),(1,1),(1,2),(0,2)], [(0,1),(1,1),(2,1),(2,2)], [(0,0),(0,1),(0,2),(1,0)], [(0,0),(0,1),(1,1),(2,1)]],
    [[(0,0),(0,1),(1,0),(1,1)]],
    [[(1,0),(1,1),(0,1),(0,2)], [(0,1),(1,1),(1,2),(2,2)]],
    [[(1,0),(1,1),(1,2),(0,1)], [(0,1),(1,1),(2,1),(1,2)], [(0,0),(0,1),(0,2),(1,1)], [(0,1),(1,1),(2,1),(1,0)]],
    [[(0,0),(0,1),(1,1),(1,2)], [(0,2),(1,1),(1,2),(2,1)]]
]

class TetrisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Tkinter Tetris")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)
        self.show_dashboard()

    def show_dashboard(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        lbl_title = tk.Label(self.main_frame, text="TETRIS", font=("Arial", 32, "bold"), fg="blue")
        lbl_title.pack(pady=20)
        
        btn_start = tk.Button(self.main_frame, text="Start New Game", font=("Arial", 16), command=self.start_game)
        btn_start.pack(pady=10)
        
        btn_quit = tk.Button(self.main_frame, text="Quit", font=("Arial", 16), command=self.root.quit)
        btn_quit.pack(pady=10)

    def start_game(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.game = TetrisGame(self.main_frame, self.show_dashboard)

class TetrisGame:
    def __init__(self, parent, show_dashboard_cb):
        self.parent = parent
        self.show_dashboard_cb = show_dashboard_cb
        
        self.canvas = tk.Canvas(self.parent, width=GAME_WIDTH, height=GAME_HEIGHT, bg='black')
        self.canvas.pack(side=tk.LEFT)
        
        sidebar = tk.Frame(self.parent)
        sidebar.pack(side=tk.LEFT, padx=20)
        
        self.score_label = tk.Label(sidebar, text="Score: 0", font=("Arial", 16))
        self.score_label.pack(pady=5)
        
        self.level_label = tk.Label(sidebar, text="Level: 1", font=("Arial", 16))
        self.level_label.pack(pady=5)
        
        self.lines_label = tk.Label(sidebar, text="Lines: 0", font=("Arial", 16))
        self.lines_label.pack(pady=5)
        
        self.msg_label = tk.Label(sidebar, text="", font=("Arial", 16), fg="red")
        self.msg_label.pack(pady=10)
        
        tk.Button(sidebar, text="Main Menu", command=self.quit_to_menu).pack(pady=20)
        
        self.grid = [[0] * COLS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines_cleared_total = 0
        self.current_piece = None
        self.game_over = False
        self.drop_speed = 500
        
        self.parent.winfo_toplevel().bind("<Left>", lambda e: self.move(-1, 0))
        self.parent.winfo_toplevel().bind("<Right>", lambda e: self.move(1, 0))
        self.parent.winfo_toplevel().bind("<Down>", lambda e: self.move(0, 1))
        self.parent.winfo_toplevel().bind("<Up>", lambda e: self.rotate())
        
        self.spawn_piece()
        self.update()

    def quit_to_menu(self):
        self.game_over = True
        self.show_dashboard_cb()

    def spawn_piece(self):
        shape_idx = random.randint(1, 7)
        self.current_piece = {'shape': shape_idx, 'rotation': 0, 'x': COLS//2 - 2, 'y': 0}
        if not self.is_valid_pos(self.current_piece['x'], self.current_piece['y'], self.current_piece['rotation']):
            self.game_over = True
            play_sound(150, 0.5)
            self.msg_label.config(text="GAME OVER")

    def is_valid_pos(self, x, y, rotation):
        shape_idx = self.current_piece['shape']
        blocks = SHAPES[shape_idx][rotation % len(SHAPES[shape_idx])]
        for r, c in blocks:
            nx, ny = x + c, y + r
            if nx < 0 or nx >= COLS or ny >= ROWS: return False
            if ny >= 0 and self.grid[ny][nx] != 0: return False
        return True

    def move(self, dx, dy):
        if self.game_over: return False
        nx, ny = self.current_piece['x'] + dx, self.current_piece['y'] + dy
        if self.is_valid_pos(nx, ny, self.current_piece['rotation']):
            self.current_piece['x'] = nx
            self.current_piece['y'] = ny
            self.draw()
            if dx != 0: play_sound(300, 0.05) # move sound
            return True
        elif dy > 0:
            self.lock_piece()
            self.spawn_piece()
        return False

    def rotate(self):
        if self.game_over: return
        new_rot = self.current_piece['rotation'] + 1
        if self.is_valid_pos(self.current_piece['x'], self.current_piece['y'], new_rot):
            self.current_piece['rotation'] = new_rot
            play_sound(400, 0.05)
            self.draw()

    def lock_piece(self):
        play_sound(200, 0.1)
        shape_idx = self.current_piece['shape']
        blocks = SHAPES[shape_idx][self.current_piece['rotation'] % len(SHAPES[shape_idx])]
        for r, c in blocks:
            nx, ny = self.current_piece['x'] + c, self.current_piece['y'] + r
            if ny >= 0: self.grid[ny][nx] = shape_idx
        self.clear_lines()

    def clear_lines(self):
        lines_cleared = 0
        new_grid = []
        for row in self.grid:
            if all(cell != 0 for cell in row):
                lines_cleared += 1
            else:
                new_grid.append(row)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0] * COLS)
        self.grid = new_grid
        if lines_cleared > 0:
            play_sound(600, 0.2)
            self.lines_cleared_total += lines_cleared
            self.score += lines_cleared * 100 * self.level
            # Level up every 5 lines
            new_level = (self.lines_cleared_total // 5) + 1
            if new_level > self.level:
                self.level = new_level
                play_sound(800, 0.4)
                self.drop_speed = max(50, 500 - (self.level - 1) * 30)
            
            self.score_label.config(text=f"Score: {self.score}")
            self.lines_label.config(text=f"Lines: {self.lines_cleared_total}")
            self.level_label.config(text=f"Level: {self.level}")

    def draw(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                val = self.grid[r][c]
                if val != 0:
                    self.draw_block(c, r, COLORS[val])
        if self.current_piece and not self.game_over:
            shape_idx = self.current_piece['shape']
            blocks = SHAPES[shape_idx][self.current_piece['rotation'] % len(SHAPES[shape_idx])]
            for r, c in blocks:
                nx, ny = self.current_piece['x'] + c, self.current_piece['y'] + r
                if ny >= 0:
                    self.draw_block(nx, ny, COLORS[shape_idx])

    def draw_block(self, x, y, color):
        x1, y1 = x * CELL_SIZE, y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="white")

    def update(self):
        if not self.game_over:
            self.move(0, 1)
            self.draw()
            self.parent.winfo_toplevel().after(self.drop_speed, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    app = TetrisApp(root)
    root.mainloop()
