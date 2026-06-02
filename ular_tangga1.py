"""
╔══════════════════════════════════════════════════════════════════╗
║          🎲 GAME ULAR TANGGA - PYTHON PYGAME EDITION 🎲         ║
║                                                                  ║
║  ALGORITMA YANG DIGUNAKAN:                                       ║
║  1. BFS (Breadth-First Search) → AI cari jalur terpendek        ║
║  2. Priority Queue / Min-Heap  → Sistem skor & ranking          ║
║  3. Fisher-Yates Shuffle       → Pengacakan posisi ular/tangga  ║
║                                                                  ║
║  Level: MUDAH | SEDANG | SUSAH | LEGENDARIS                     ║
╚══════════════════════════════════════════════════════════════════╝

Instalasi:
    pip install pygame

Jalankan:
    python ular_tangga.py
"""

import pygame
import sys
import random
import heapq
import math
import time
from collections import deque

# ─── INISIALISASI ───────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ─── KONSTANTA LAYAR ────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 750
BOARD_SIZE = 650
BOARD_X, BOARD_Y = 20, 50
CELL = BOARD_SIZE // 10
PANEL_X = BOARD_X + BOARD_SIZE + 20
PANEL_W = SCREEN_W - PANEL_X - 10

FPS = 60

# ─── PALET WARNA ────────────────────────────────────────────────────────────────
C = {
    "bg":        (10,  12,  30),
    "board_a":   (241, 250, 238),
    "board_b":   (168, 218, 220),
    "border":    (29,  53,  87),
    "snake_h":   (230, 57,  70),
    "snake_b":   (180, 30,  40),
    "ladder_h":  (42,  157, 143),
    "ladder_b":  (30,  120, 110),
    "p1":        (255, 183, 3),
    "p2":        (58,  134, 255),
    "p3":        (131, 56,  236),
    "ai":        (255, 80,  80),
    "text":      (255, 255, 255),
    "subtext":   (180, 200, 220),
    "gold":      (255, 215, 0),
    "silver":    (192, 192, 192),
    "bronze":    (205, 127, 50),
    "panel":     (20,  25,  60),
    "panel2":    (30,  38,  80),
    "accent":    (100, 200, 255),
    "green":     (57,  255, 20),
    "red":       (255, 60,  60),
    "dice_bg":   (255, 250, 230),
    "dice_dot":  (30,  30,  30),
    "star":      (255, 220, 50),
    "finish":    (255, 100, 100),
}

# ─── LEVEL KONFIGURASI ──────────────────────────────────────────────────────────
LEVELS = {
    1: {
        "name": "MUDAH",
        "emoji": "🌱",
        "color": (80, 200, 80),
        "snakes": {17: 7, 54: 34, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78},
        "ladders": {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91},
        "ai_count": 1,
        "description": "Ular & tangga seimbang. Cocok untuk pemula!",
    },
    2: {
        "name": "SEDANG",
        "emoji": "🔥",
        "color": (255, 180, 0),
        "snakes": {17: 7, 32: 10, 54: 34, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78, 45: 5},
        "ladders": {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81},
        "ai_count": 1,
        "description": "Lebih banyak ular! Hati-hati langkahmu.",
    },
    3: {
        "name": "SUSAH",
        "emoji": "💀",
        "color": (220, 80, 80),
        "snakes": {12: 2, 25: 4, 32: 10, 48: 6, 54: 34, 62: 19, 64: 60, 72: 51, 87: 24, 93: 73, 95: 75, 99: 78},
        "ladders": {4: 14, 9: 31, 28: 84, 40: 59, 63: 81},
        "ai_count": 2,
        "description": "Banyak ular, sedikit tangga. Sangat menantang!",
    },
    4: {
        "name": "LEGENDARIS",
        "emoji": "⚡",
        "color": (180, 50, 255),
        "snakes": None,   # akan digenerate dengan Fisher-Yates
        "ladders": None,
        "ai_count": 2,
        "description": "Posisi ular & tangga DIACAK setiap game! 🎲",
    },
}

# ════════════════════════════════════════════════════════════════════════════════
#  ALGORITMA 1: FISHER-YATES SHUFFLE
#  Fungsi: Mengacak posisi ular dan tangga secara merata dan tidak bias.
#  Kompleksitas: O(n) — setiap elemen pasti diproses tepat sekali.
# ════════════════════════════════════════════════════════════════════════════════
def fisher_yates_shuffle(arr):
    """
    Fisher-Yates (Knuth) Shuffle Algorithm
    Menghasilkan permutasi acak yang benar-benar merata (unbiased).
    
    Cara kerja:
      - Iterasi dari elemen terakhir ke elemen pertama.
      - Untuk setiap posisi i, pilih indeks acak j dari [0..i].
      - Tukar arr[i] dengan arr[j].
    """
    n = len(arr)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def generate_random_board():
    """
    Menggunakan Fisher-Yates untuk generate papan level Legendaris.
    Menghasilkan 10 ular dan 8 tangga secara acak tanpa konflik.
    """
    cells = list(range(3, 99))   # kotak 3-98 (tidak termasuk 1,2,99,100)
    fisher_yates_shuffle(cells)  # acak dengan Fisher-Yates

    snake_heads = cells[:12]
    remaining = [c for c in cells if c not in snake_heads]
    fisher_yates_shuffle(remaining)
    ladder_bottoms = remaining[:8]

    snakes, ladders = {}, {}

    for head in snake_heads:
        # ekor harus lebih rendah dari kepala
        possible = [c for c in range(2, head) if c not in snake_heads and c not in [v for v in snakes.values()]]
        if possible:
            tail = random.choice(possible)
            snakes[head] = tail

    used_tops = set()
    for bottom in ladder_bottoms:
        # puncak harus lebih tinggi dari bawah
        possible = [c for c in range(bottom + 5, 100)
                    if c not in ladders and c not in snakes and c not in used_tops and c < 100]
        if possible:
            top = random.choice(possible)
            ladders[bottom] = top
            used_tops.add(top)

    return snakes, ladders


# ════════════════════════════════════════════════════════════════════════════════
#  ALGORITMA 2: BFS (Breadth-First Search) untuk AI
#  Fungsi: Mencari jalur terpendek dari posisi AI ke kotak 100.
#  Digunakan untuk menentukan strategi gerak AI (simulasi "terbaik").
#  Kompleksitas: O(V + E) dengan V=kotak, E=kemungkinan lemparan dadu.
# ════════════════════════════════════════════════════════════════════════════════
def bfs_shortest_path(start, snakes, ladders):
    """
    BFS dari posisi 'start' ke kotak 100.
    
    Graph model:
      - Dari kotak i, bisa melangkah ke i+1 s/d i+6 (dadu 1-6).
      - Jika mendarat di kepala ular → turun ke ekor ular.
      - Jika mendarat di bawah tangga → naik ke puncak tangga.
    
    Returns:
      (jarak, path) → jumlah lemparan dadu minimum dan rutenya.
    """
    if start == 100:
        return 0, [100]
    
    queue = deque()
    queue.append((start, [start], 0))
    visited = {start}

    while queue:
        pos, path, dist = queue.popleft()
        
        for dice in range(1, 7):
            next_pos = pos + dice
            if next_pos > 100:
                continue
            
            # Cek ular / tangga
            actual = snakes.get(next_pos, ladders.get(next_pos, next_pos))
            
            if actual == 100:
                return dist + 1, path + [next_pos, actual] if actual != next_pos else path + [next_pos]
            
            if actual not in visited:
                visited.add(actual)
                queue.append((actual, path + [next_pos], dist + 1))
    
    return -1, []   # tidak terjangkau


# ════════════════════════════════════════════════════════════════════════════════
#  ALGORITMA 3: PRIORITY QUEUE / MIN-HEAP untuk Sistem Skor
#  Fungsi: Mengelola leaderboard secara efisien — insert & ambil terbaik O(log n).
#  Kompleksitas: Insert O(log n), Extract-min O(log n), Peek O(1).
# ════════════════════════════════════════════════════════════════════════════════
class ScoreBoard:
    """
    Min-Heap berbasis heapq Python.
    Skor = jumlah lemparan dadu (lebih sedikit = lebih baik).
    
    Cara kerja:
      - heapq.heappush() → O(log n): masukkan skor baru, heap otomatis rebalance.
      - heapq.heappop()  → O(log n): ambil elemen terkecil (skor terbaik).
      - Properti heap: parent ≤ children, sehingga root = minimum.
    """
    def __init__(self):
        self._heap = []   # list internal heap
        self._counter = 0  # tie-breaker untuk skor sama

    def push(self, name, rolls, level, duration):
        """Masukkan skor. Heap diurutkan berdasarkan rolls (ascending)."""
        # heapq = min-heap: (rolls, counter, name, level, duration)
        heapq.heappush(self._heap, (rolls, self._counter, name, level, duration))
        self._counter += 1

    def get_top(self, n=10):
        """Ambil n skor terbaik tanpa merusak heap (dengan copy)."""
        temp = self._heap[:]
        result = []
        for _ in range(min(n, len(temp))):
            entry = heapq.heappop(temp)
            result.append({
                "rolls": entry[0],
                "name": entry[2],
                "level": entry[3],
                "duration": entry[4],
            })
        return result

    def size(self):
        return len(self._heap)


# ─── KELAS PEMAIN ───────────────────────────────────────────────────────────────
class Player:
    def __init__(self, name, color, is_ai=False):
        self.name = name
        self.color = color
        self.pos = 0          # 0 = belum mulai
        self.rolls = 0
        self.is_ai = is_ai
        self.history = []     # riwayat posisi

        # ANIMASI
        self.visual_x = 0
        self.visual_y = 0
        self.target_pos = 0
        self.move_queue = []
        self.move_progress = 0

        self.anim_pos = None  # posisi animasi saat ini
        self.moving = False
        self.bounce = 0       # efek bounce

    def reset(self):
        self.pos = 0
        self.rolls = 0
        self.history = []
        self.visual_x, self.visual_y = cell_to_xy(1)

        # reset animasi
        self.visual_x = 0
        self.visual_y = 0
        self.target_pos = 0
        self.move_queue = []
        self.move_progress = 0

        self.anim_pos = None
        self.moving = False
        self.bounce = 0


# ─── FUNGSI BANTU PAPAN ─────────────────────────────────────────────────────────
def cell_to_xy(cell):
    """Konversi nomor kotak (1-100) → koordinat piksel (tengah kotak)."""
    cell -= 1
    row = cell // 10          # baris dari bawah
    col = cell % 10
    if row % 2 == 0:          # baris genap: kiri ke kanan
        cx = col
    else:                     # baris ganjil: kanan ke kiri
        cx = 9 - col
    cy = 9 - row
    px = BOARD_X + cx * CELL + CELL // 2
    py = BOARD_Y + cy * CELL + CELL // 2
    return (px, py)


def draw_rounded_rect(surf, color, rect, radius=10, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def lerp(a, b, t):
    return a + (b - a) * t


# ─── KELAS GAME UTAMA ───────────────────────────────────────────────────────────
class UlarTangga:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🎲 ULAR TANGGA — Python Edition")
        self.clock = pygame.time.Clock()
        self.scoreboard = ScoreBoard()
        self.state = "menu"   # menu | setup | game | result | leaderboard | algo_info
        self.level = 1
        self.players = []
        self.current_player = 0
        self.dice_val = 0
        self.dice_rolling = False
        self.dice_anim_frame = 0
        self.dice_display = 1
        self.message = ""
        self.message_timer = 0
        self.snakes = {}
        self.ladders = {}
        self.winner = None
        self.game_start_time = 0
        self.particles = []
        self.ai_think_timer = 0
        self.bfs_hint = None  # jalur BFS hint untuk pemain manusia
        self.frame = 0
        self.selected_level = 1
        self.hover_btn = None
        self.setup_fonts()

    def animate_player_move(self, player, target):
        player.move_queue = []
        current = player.pos
        while current < target:
            current += 1
            player.move_queue.append(current)
        player.moving = True

    def setup_fonts(self):
        self.font_big   = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_sm    = pygame.font.SysFont("Arial", 18)
        self.font_xs    = pygame.font.SysFont("Arial", 14)
        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_icon  = pygame.font.SysFont("Segoe UI Emoji", 28)
        self.font_emoji_big = pygame.font.SysFont("Segoe UI Emoji", 50)

    # ── SPAWN PARTIKEL ──────────────────────────────────────────────────────────
    def spawn_particles(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(30, 60),
                "color": color,
                "size": random.randint(3, 8),
            })

    def update_particles(self):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15
            p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

    def draw_particles(self):
        for p in self.particles:
            alpha = int(255 * p["life"] / 60)
            r = max(0, min(255, p["color"][0]))
            g = max(0, min(255, p["color"][1]))
            b = max(0, min(255, p["color"][2]))
            pygame.draw.circle(self.screen, (r, g, b),
                               (int(p["x"]), int(p["y"])), p["size"])

    # ── INISIALISASI GAME ───────────────────────────────────────────────────────
    def init_game(self):
        lvl = LEVELS[self.level]
        if lvl["snakes"] is None:
            # LEVEL LEGENDARIS → Fisher-Yates generate random board
            self.snakes, self.ladders = generate_random_board()
        else:
            self.snakes  = dict(lvl["snakes"])
            self.ladders = dict(lvl["ladders"])

        # Setup pemain: 1 manusia + AI sesuai level
        colors = [C["p1"], C["p2"], C["p3"], C["ai"]]
        names  = ["KAMU", "AI-Alpha", "AI-Beta"]
        self.players = [Player("KAMU", C["p1"], is_ai=False)]
        for i in range(lvl["ai_count"]):
            self.players.append(Player(f"AI-{i+1}", colors[i+2], is_ai=True))

        for p in self.players:
            p.reset()

        self.current_player = 0
        self.dice_val = 0
        self.winner = None
        self.message = ""
        self.particles = []
        self.game_start_time = time.time()
        self.bfs_hint = None
        self.state = "game"

    # ── LEMPAR DADU ─────────────────────────────────────────────────────────────
    def roll_dice(self):
        if self.dice_rolling:
            return
        self.dice_rolling = True
        self.dice_anim_frame = 0
        self.dice_val = random.randint(1, 6)

    def update_dice(self):
        if not self.dice_rolling:
            return
        self.dice_anim_frame += 1
        self.dice_display = random.randint(1, 6)
        if self.dice_anim_frame >= 120:
            self.dice_rolling = False
            self.dice_display = self.dice_val
            self.process_move()

    # ── PROSES GERAK ────────────────────────────────────────────────────────────
    def process_move(self):
        p = self.players[self.current_player]
        p.rolls += 1
        new_pos = p.pos + self.dice_val

        if new_pos > 100:
            self.message = f"{p.name}: Butuh tepat {100 - p.pos}! Lemparan terbuang."
            self.message_timer = 120
            self.next_turn()
            return

        # Simpan posisi sebelum efek
        raw_pos = new_pos

        # Cek ular
        if new_pos in self.snakes:
            tail = self.snakes[new_pos]
            self.message = f"🐍 {p.name} kena ULAR! {new_pos} → {tail}"
            self.message_timer = 150
            new_pos = tail
            self.spawn_particles(*cell_to_xy(raw_pos), C["snake_h"], 25)

        # Cek tangga
        elif new_pos in self.ladders:
            top = self.ladders[new_pos]
            self.message = f"🪜 {p.name} dapat TANGGA! {raw_pos} → {top}"
            self.message_timer = 150
            new_pos = top
            self.spawn_particles(*cell_to_xy(raw_pos), C["ladder_h"], 25)

        p.history.append(p.pos)
        self.animate_player_move(p, new_pos)
        p.bounce = 15

        # Hitung BFS hint untuk pemain manusia
        if not p.is_ai:
            dist, path = bfs_shortest_path(new_pos, self.snakes, self.ladders)
            self.bfs_hint = {"dist": dist, "path": path}

        # Cek menang
        if new_pos == 100:
            self.winner = p
            duration = time.time() - self.game_start_time
            self.scoreboard.push(p.name, p.rolls, self.level, duration)
            self.spawn_particles(SCREEN_W // 2, SCREEN_H // 2, C["gold"], 80)
            self.state = "result"
            return

        self.next_turn()

    def next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        self.ai_think_timer = 45  # AI "berpikir" 45 frame sebelum lempar

    # ── UPDATE ──────────────────────────────────────────────────────────────────
    def update(self):
        for p in self.players:
            if p.moving and p.move_queue:
                p.move_progress += 1
                # kecepatan langkah
                if p.move_progress >= 10:
                    next_step = p.move_queue.pop(0)
                    p.anim_pos = next_step
                    p.move_progress = 0
                    p.bounce = 10
                if not p.move_queue:
                    p.moving = False
                    p.pos = p.anim_pos

        self.frame += 1
        self.update_dice()
        self.update_particles()

        if self.message_timer > 0:
            self.message_timer -= 1

        for p in self.players:
            if p.bounce > 0:
                p.bounce -= 1

      # AI turn
        if self.state == "game" and not self.dice_rolling:
            p = self.players[self.current_player]

            # hanya jika pemain AI
            if p.is_ai:
                self.ai_think_timer -= 1

                if self.ai_think_timer <= 0:

                    best_dice = None
                    best_dist = 999
                    best_path = []

                    # coba semua kemungkinan dadu 1-6
                    for dice in range(1, 7):

                        nxt = p.pos + dice

                        # tidak boleh lewat 100
                        if nxt > 100:
                            continue

                        # cek ular / tangga
                        nxt = self.snakes.get(
                            nxt,
                            self.ladders.get(nxt, nxt)
                        )

                        # BFS cari jarak tercepat
                        dist, path = bfs_shortest_path(
                            nxt,
                            self.snakes,
                            self.ladders
                        )

                        # pilih langkah terbaik
                        if dist != -1 and dist < best_dist:
                            best_dist = dist
                            best_dice = dice
                            best_path = path

                    # fallback jika tidak ada
                    if best_dice is None:
                        best_dice = random.randint(1, 6)

                    # tampilkan analisis BFS
                    print("\n===== AI BFS ANALYSIS =====")
                    print("AI :", p.name)
                    print("Posisi awal :", p.pos)
                    print("Dadu terbaik :", best_dice)
                    print("Minimal langkah ke 100 :", best_dist)
                    print("Path BFS :", best_path)
                    print("===========================\n")

                    # gunakan hasil terbaik
                    self.dice_val = best_dice
                    self.dice_display = best_dice

                    # jalankan gerakan
                    self.process_move()

    # ════════════════════════════════════════════════════════════════════════════
    #  RENDER FUNCTIONS
    # ════════════════════════════════════════════════════════════════════════════
    def draw_bg(self):
        self.screen.fill(C["bg"])
        # Grid bintang background
        for i in range(0, SCREEN_W, 60):
            for j in range(0, SCREEN_H, 60):
                offset = math.sin(self.frame * 0.02 + i * 0.1) * 2
                alpha = int(30 + 20 * math.sin(self.frame * 0.03 + j * 0.1))
                pygame.draw.circle(self.screen, (alpha, alpha, alpha + 20),
                                   (i, int(j + offset)), 1)

    def draw_board(self):
        # Shadow
        shadow = pygame.Surface((BOARD_SIZE + 10, BOARD_SIZE + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        self.screen.blit(shadow, (BOARD_X + 5, BOARD_Y + 5))

        # Sel papan
        for row in range(10):
            for col in range(10):
                x = BOARD_X + col * CELL
                y = BOARD_Y + row * CELL
                color = C["board_a"] if (row + col) % 2 == 0 else C["board_b"]
                pygame.draw.rect(self.screen, color, (x, y, CELL, CELL))

                # Nomor kotak
                display_row = 9 - row
                if display_row % 2 == 0:
                    num = display_row * 10 + col + 1
                else:
                    num = display_row * 10 + (9 - col) + 1

                num_surf = self.font_xs.render(str(num), True, (80, 80, 80))
                self.screen.blit(num_surf, (x + 3, y + 3))

        # Grid lines
        for i in range(11):
            x = BOARD_X + i * CELL
            y = BOARD_Y + i * CELL
            pygame.draw.line(self.screen, C["border"], (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), 1)
            pygame.draw.line(self.screen, C["border"], (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), 1)

        # Border papan
        pygame.draw.rect(self.screen, C["border"],
                         (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), 3)

        # Kotak 100 khusus
        fx, fy = cell_to_xy(100)
        glow = int(30 + 20 * math.sin(self.frame * 0.1))
        pygame.draw.circle(self.screen, (255, glow * 3, 50), (fx, fy), CELL // 2 - 2)
        label = self.font_sm.render("🏆", True, C["gold"])
        self.screen.blit(label, (fx - label.get_width() // 2, fy - label.get_height() // 2))

        self.draw_snakes()
        self.draw_ladders()
        self.draw_players()

    def draw_snakes(self):
        for head, tail in self.snakes.items():
            hx, hy = cell_to_xy(head)
            tx, ty = cell_to_xy(tail)
            # Tubuh ular — kurva bezier sederhana
            mid_x = (hx + tx) // 2 + random.randint(-20, 20) * 0
            mid_y = (hy + ty) // 2
            # Garis tebal bayangan
            pygame.draw.line(self.screen, C["snake_b"], (hx, hy), (tx, ty), 8)
            pygame.draw.line(self.screen, C["snake_h"], (hx, hy), (tx, ty), 5)
            # Kepala ular
            pygame.draw.circle(self.screen, C["snake_h"], (hx, hy), 10)
            pygame.draw.circle(self.screen, (255, 255, 255), (hx, hy), 10, 2)
            s_label = self.font_xs.render("🐍", True, C["text"])
            self.screen.blit(s_label, (hx - 10, hy - 14))

    def draw_ladders(self):
        for bottom, top in self.ladders.items():
            bx, by = cell_to_xy(bottom)
            tx, ty = cell_to_xy(top)
            # Rail kiri & kanan tangga
            offset = 5
            pygame.draw.line(self.screen, C["ladder_b"], (bx - offset, by), (tx - offset, ty), 6)
            pygame.draw.line(self.screen, C["ladder_b"], (bx + offset, by), (tx + offset, ty), 6)
            pygame.draw.line(self.screen, C["ladder_h"], (bx - offset, by), (tx - offset, ty), 3)
            pygame.draw.line(self.screen, C["ladder_h"], (bx + offset, by), (tx + offset, ty), 3)
            # Anak tangga
            steps = 5
            for i in range(steps + 1):
                t = i / steps
                rx = int(lerp(bx, tx, t))
                ry = int(lerp(by, ty, t))
                pygame.draw.line(self.screen, C["ladder_h"],
                                 (rx - offset, ry), (rx + offset, ry), 3)
            # Label bawah tangga
            lbl = self.font_xs.render("🪜", True, C["text"])
            self.screen.blit(lbl, (bx - 10, by - 14))

    def draw_players(self):
        offsets = [(-12, 0), (12, 0), (0, -12), (0, 12)]
        for i, p in enumerate(self.players):
            if p.pos == 0:
                continue
            
            # TARGET posisi asli kotak
            draw_pos = p.anim_pos if p.moving and p.anim_pos else p.pos 
            target_x, target_y = cell_to_xy(draw_pos)

            # INTERPOLASI HALUS
            p.visual_x += (target_x - p.visual_x) * 0.15
            p.visual_y += (target_y - p.visual_y) * 0.15

            # gunakan posisi visual
            cx = int(p.visual_x)
            cy = int(p.visual_y)

            ox, oy = offsets[i % len(offsets)]

            px = cx + ox
            py = cy + oy

            # Bounce efek
            bounce_y = -abs(math.sin(p.bounce * 0.3)) * 6 if p.bounce > 0 else 0
            py += int(bounce_y)

            # Shadow
            pygame.draw.circle(self.screen, (0, 0, 0, 80), (px + 2, cy + oy + 2), 12)
            # Body
            pygame.draw.circle(self.screen, p.color, (px, py), 13)
            pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 13, 2)
            # Label inisial
            initial = p.name[0]
            lbl = self.font_xs.render(initial, True, (0, 0, 0))
            self.screen.blit(lbl, (px - lbl.get_width() // 2, py - lbl.get_height() // 2))

            # Indikator giliran
            if i == self.current_player and self.state == "game":
                pulse = int(4 + 3 * math.sin(self.frame * 0.15))
                pygame.draw.circle(self.screen, C["gold"], (px, py), 13 + pulse, 2)

    def draw_dice(self, x, y, value, rolling=False):
        """Gambar dadu dengan titik-titik."""
        size = 70
        draw_rounded_rect(self.screen, C["dice_bg"], (x, y, size, size), 12,
                          3, C["border"])
        # Pola titik dadu
        dot_map = {
            1: [(35, 35)],
            2: [(20, 20), (50, 50)],
            3: [(20, 20), (35, 35), (50, 50)],
            4: [(20, 20), (50, 20), (20, 50), (50, 50)],
            5: [(20, 20), (50, 20), (35, 35), (20, 50), (50, 50)],
            6: [(20, 17), (50, 17), (20, 35), (50, 35), (20, 53), (50, 53)],
        }
        v = value if value in dot_map else 1
        for dx, dy in dot_map[v]:
            r = 6 if rolling else 7
            pygame.draw.circle(self.screen, C["dice_dot"], (x + dx, y + dy), r)

    def draw_panel(self):
        """Panel kanan: info game, dadu, skor pemain."""
        # Background panel
        draw_rounded_rect(self.screen, C["panel"],
                          (PANEL_X - 5, 10, PANEL_W + 5, SCREEN_H - 20), 15)

        y = 20

        # Judul & level
        lvl = LEVELS[self.level]
        title = self.font_med.render("🎲 ULAR TANGGA", True, C["gold"])
        self.screen.blit(title, (PANEL_X + (PANEL_W - title.get_width()) // 2, y))
        y += 35

        lvl_col = lvl["color"]
        lvl_surf = self.font_med.render(f"{lvl['emoji']} {lvl['name']}", True, lvl_col)
        self.screen.blit(lvl_surf, (PANEL_X + (PANEL_W - lvl_surf.get_width()) // 2, y))
        y += 35

        pygame.draw.line(self.screen, C["accent"], (PANEL_X, y), (PANEL_X + PANEL_W, y), 1)
        y += 10

        # Dadu
        dice_x = PANEL_X + (PANEL_W - 70) // 2
        self.draw_dice(dice_x, y, self.dice_display, self.dice_rolling)
        if self.dice_val > 0 and not self.dice_rolling:
            dv = self.font_med.render(f"Dadu: {self.dice_val}", True, C["text"])
            self.screen.blit(dv, (PANEL_X + (PANEL_W - dv.get_width()) // 2, y + 75))
        y += 110

        # Tombol Roll (hanya giliran manusia)
        current = self.players[self.current_player]
        if not current.is_ai and not self.dice_rolling and self.state == "game":
            btn_w, btn_h = 140, 45
            btn_x = PANEL_X + (PANEL_W - btn_w) // 2
            pulse = int(5 * math.sin(self.frame * 0.1))
            draw_rounded_rect(self.screen, (50, 180, 80),
                              (btn_x - pulse, y - pulse, btn_w + pulse * 2, btn_h + pulse * 2), 10)
            draw_rounded_rect(self.screen, (80, 220, 100),
                              (btn_x, y, btn_w, btn_h), 10)
            btn_lbl = self.font_med.render("🎲 LEMPAR", True, (0, 0, 0))
            self.screen.blit(btn_lbl, (btn_x + (btn_w - btn_lbl.get_width()) // 2,
                                        y + (btn_h - btn_lbl.get_height()) // 2))
            self._roll_btn_rect = pygame.Rect(btn_x, y, btn_w, btn_h)
        else:
            self._roll_btn_rect = None

        y += 60

        pygame.draw.line(self.screen, C["accent"], (PANEL_X, y), (PANEL_X + PANEL_W, y), 1)
        y += 10

        # Info pemain
        turn_lbl = self.font_sm.render("📋 STATUS PEMAIN", True, C["accent"])
        self.screen.blit(turn_lbl, (PANEL_X + 5, y))
        y += 30

        for i, p in enumerate(self.players):
            is_cur = (i == self.current_player)
            bg_col = C["panel2"] if is_cur else C["panel"]
            draw_rounded_rect(self.screen, bg_col, (PANEL_X, y, PANEL_W, 52), 8)
            if is_cur:
                pygame.draw.rect(self.screen, p.color, (PANEL_X, y, 4, 52), border_radius=4)

            # Avatar
            pygame.draw.circle(self.screen, p.color, (PANEL_X + 22, y + 26), 16)
            pygame.draw.circle(self.screen, (255, 255, 255), (PANEL_X + 22, y + 26), 16, 2)
            init_lbl = self.font_sm.render(p.name[0], True, (0, 0, 0))
            self.screen.blit(init_lbl, (PANEL_X + 22 - init_lbl.get_width() // 2,
                                         y + 26 - init_lbl.get_height() // 2))

            # Nama & info
            n_col = C["gold"] if is_cur else C["text"]
            name_s = self.font_sm.render(p.name + (" ← GILIRAN" if is_cur else ""),
                                          True, n_col)
            self.screen.blit(name_s, (PANEL_X + 46, y + 6))

            pos_txt = f"Kotak: {p.pos if p.pos > 0 else 'START'}  |  Lempar: {p.rolls}"
            if p.is_ai:
                pos_txt += "  🤖"
            pos_s = self.font_xs.render(pos_txt, True, C["subtext"])
            self.screen.blit(pos_s, (PANEL_X + 46, y + 28))

            # Progress bar
            progress = p.pos / 100
            bar_w = PANEL_W - 55
            pygame.draw.rect(self.screen, (50, 50, 80), (PANEL_X + 46, y + 43, bar_w, 6), border_radius=3)
            pygame.draw.rect(self.screen, p.color,
                             (PANEL_X + 46, y + 43, int(bar_w * progress), 6), border_radius=3)

            y += 58

        pygame.draw.line(self.screen, C["accent"], (PANEL_X, y), (PANEL_X + PANEL_W, y), 1)
        y += 8

        # BFS Hint untuk pemain manusia
        if self.bfs_hint and self.state == "game":
            hint_lbl = self.font_sm.render("🔍 BFS HINT", True, C["accent"])
            self.screen.blit(hint_lbl, (PANEL_X + 5, y))
            y += 22
            dist_txt = f"Min. lemparan ke 100: {self.bfs_hint['dist']}"
            dist_s = self.font_xs.render(dist_txt, True, C["green"])
            self.screen.blit(dist_s, (PANEL_X + 5, y))
            y += 18

        # Pesan
        if self.message_timer > 0 and self.message:
            msg_col = C["snake_h"] if "ULAR" in self.message or "kena" in self.message else C["ladder_h"]
            msg_col = C["gold"] if "MENANG" in self.message else msg_col
            # Word wrap sederhana
            words = self.message.split()
            line, lines = "", []
            for w in words:
                test = (line + " " + w).strip()
                if self.font_xs.size(test)[0] < PANEL_W - 10:
                    line = test
                else:
                    lines.append(line)
                    line = w
            if line:
                lines.append(line)

            msg_y = SCREEN_H - 130
            for ln in lines[-3:]:
                ms = self.font_xs.render(ln, True, msg_col)
                self.screen.blit(ms, (PANEL_X + 5, msg_y))
                msg_y += 18

        # Tombol navigasi bawah
        btn_y = SCREEN_H - 85
        self.draw_small_btn("🏠 MENU", PANEL_X, btn_y, 90, 35, (80, 30, 30))
        self.draw_small_btn("🏆 SKOR", PANEL_X + 95, btn_y, 90, 35, (30, 60, 80))
        self.draw_small_btn("📘 ALGO", PANEL_X + 190, btn_y, 90, 35, (50, 30, 80))

        # Ular & tangga count
        info_y = SCREEN_H - 40
        info_s = self.font_xs.render(f"🐍 {len(self.snakes)} ular  🪜 {len(self.ladders)} tangga", True, C["subtext"])
        self.screen.blit(info_s, (PANEL_X + 5, info_y))

    def draw_small_btn(self, text, x, y, w, h, color):
        draw_rounded_rect(self.screen, color, (x, y, w, h), 8)
        lbl = self.font_xs.render(text, True, C["text"])
        self.screen.blit(lbl, (x + (w - lbl.get_width()) // 2, y + (h - lbl.get_height()) // 2))

    # ── SCREEN: MENU ────────────────────────────────────────────────────────────
    def draw_menu(self):
        self.draw_bg()
        cx = SCREEN_W // 2

        # Judul animasi
        t = self.frame * 0.05
        title_y = 80 + int(8 * math.sin(t))
        title = self.font_title.render("🎲 ULAR TANGGA 🎲", True, C["gold"])
        self.screen.blit(title, (cx - title.get_width() // 2, title_y))

        sub = self.font_med.render("Python Edition — 3 Algoritma Canggih", True, C["accent"])
        self.screen.blit(sub, (cx - sub.get_width() // 2, title_y + 65))

        # Pilih level
        lev_lbl = self.font_med.render("PILIH LEVEL:", True, C["text"])
        self.screen.blit(lev_lbl, (cx - lev_lbl.get_width() // 2, 210))

        self._level_btns = []
        for lv, data in LEVELS.items():
            bx = cx - 340 + (lv - 1) * 175
            by = 255
            bw, bh = 160, 120
            selected = (self.selected_level == lv)
            bg = data["color"] if selected else (40, 40, 70)
            draw_rounded_rect(self.screen, bg, (bx, by, bw, bh), 12,
                              3, data["color"] if selected else (80, 80, 100))
            em = self.font_icon.render(data["emoji"], True, C["text"])
            self.screen.blit(em, (bx + bw // 2 - em.get_width() // 2, by + 10))
            nm = self.font_med.render(data["name"], True, C["text"])
            self.screen.blit(nm, (bx + bw // 2 - nm.get_width() // 2, by + 52))
            ai_t = self.font_xs.render(f"{data['ai_count']} AI", True, (200, 200, 200))
            self.screen.blit(ai_t, (bx + bw // 2 - ai_t.get_width() // 2, by + 78))
            desc_short = data["description"][:25] + "…" if len(data["description"]) > 25 else data["description"]
            ds = self.font_xs.render(desc_short, True, (200, 200, 200))
            self.screen.blit(ds, (bx + bw // 2 - ds.get_width() // 2, by + 96))
            self._level_btns.append((lv, pygame.Rect(bx, by, bw, bh)))

        # Deskripsi level terpilih
        desc = LEVELS[self.selected_level]["description"]
        desc_s = self.font_sm.render(desc, True, C["subtext"])
        self.screen.blit(desc_s, (cx - desc_s.get_width() // 2, 395))

        # Tombol MAIN
        main_bx = cx - 120
        main_bw, main_bh = 240, 60
        pulse = int(6 * math.sin(self.frame * 0.08))
        draw_rounded_rect(self.screen, (30, 140, 60),
                          (main_bx - pulse, 430 - pulse, main_bw + pulse * 2, main_bh + pulse * 2), 15)
        draw_rounded_rect(self.screen, (50, 200, 90), (main_bx, 430, main_bw, main_bh), 15)
        ml = self.font_big.render("▶  MULAI GAME", True, (255, 255, 255))
        self.screen.blit(ml, (main_bx + (main_bw - ml.get_width()) // 2, 430 + (main_bh - ml.get_height()) // 2))
        self._main_btn = pygame.Rect(main_bx, 430, main_bw, main_bh)

        # Nav bawah
        self.draw_small_btn("🏆 LEADERBOARD", cx - 160, 520, 150, 40, (30, 60, 80))
        self.draw_small_btn("📘 INFO ALGORITMA", cx + 10, 520, 170, 40, (50, 30, 80))
        self._lb_btn_menu = pygame.Rect(cx - 160, 520, 150, 40)
        self._algo_btn_menu = pygame.Rect(cx + 10, 520, 170, 40)

        # Footer algoritma
        algos = [
            "🔀 Fisher-Yates Shuffle  →  Acak papan level Legendaris",
            "🔍 BFS (Breadth-First)    →  AI & Hint jalur terpendek",
            "📊 Min-Heap Priority Q    →  Sistem Leaderboard",
        ]
        for i, a in enumerate(algos):
            s = self.font_xs.render(a, True, C["subtext"])
            self.screen.blit(s, (cx - s.get_width() // 2, 590 + i * 20))

    # ── SCREEN: RESULT ──────────────────────────────────────────────────────────
    def draw_result(self):
        self.draw_bg()
        self.draw_particles()
        cx, cy = SCREEN_W // 2, SCREEN_H // 2

        # Panel
        pw, ph = 600, 400
        draw_rounded_rect(self.screen, C["panel"], (cx - pw // 2, cy - ph // 2, pw, ph), 20,
                          3, C["gold"])

        y = cy - ph // 2 + 30
        trophy = self.font_icon.render("🏆", True, C["gold"])
        self.screen.blit(trophy, (cx - trophy.get_width() // 2, y))
        y += 50

        win_txt = self.font_big.render(f"{self.winner.name} MENANG!", True, C["gold"])
        self.screen.blit(win_txt, (cx - win_txt.get_width() // 2, y))
        y += 50

        lvl_txt = self.font_med.render(f"Level: {LEVELS[self.level]['emoji']} {LEVELS[self.level]['name']}", True, C["accent"])
        self.screen.blit(lvl_txt, (cx - lvl_txt.get_width() // 2, y))
        y += 35

        stats = [
            f"🎲 Total Lemparan Dadu: {self.winner.rolls}",
            f"⏱️  Durasi: {int(time.time() - self.game_start_time)} detik",
        ]
        for s in stats:
            ss = self.font_sm.render(s, True, C["text"])
            self.screen.blit(ss, (cx - ss.get_width() // 2, y))
            y += 30

        # Semua pemain
        y += 10
        for i, p in enumerate(sorted(self.players, key=lambda x: (-x.pos, x.rolls))):
            medal = ["🥇", "🥈", "🥉", "4️⃣"][i]
            s = self.font_sm.render(f"{medal} {p.name}  —  Kotak {p.pos}  |  {p.rolls} lemparan", True, C["text"])
            self.screen.blit(s, (cx - s.get_width() // 2, y))
            y += 28

        y += 10
        self.draw_small_btn("🔁 MAIN LAGI", cx - 165, y, 150, 45, (30, 100, 50))
        self.draw_small_btn("🏠 MENU", cx - 5, y, 100, 45, (80, 30, 30))
        self.draw_small_btn("🏆 SKOR", cx + 108, y, 100, 45, (30, 60, 80))
        self._replay_btn = pygame.Rect(cx - 165, y, 150, 45)
        self._menu_btn_r = pygame.Rect(cx - 5, y, 100, 45)
        self._lb_btn_r = pygame.Rect(cx + 108, y, 100, 45)

    # ── SCREEN: LEADERBOARD ─────────────────────────────────────────────────────
    def draw_leaderboard(self):
        self.draw_bg()
        cx = SCREEN_W // 2
        title = self.font_big.render("🏆 LEADERBOARD — MIN-HEAP", True, C["gold"])
        self.screen.blit(title, (cx - title.get_width() // 2, 30))
        sub = self.font_sm.render("Diurutkan dengan Priority Queue (Min-Heap) — semakin sedikit lemparan = lebih baik", True, C["subtext"])
        self.screen.blit(sub, (cx - sub.get_width() // 2, 80))

        top = self.scoreboard.get_top(8)
        if not top:
            no = self.font_med.render("Belum ada skor. Mainkan dulu!", True, C["subtext"])
            self.screen.blit(no, (cx - no.get_width() // 2, 300))
        else:
            headers = ["#", "NAMA", "LEVEL", "LEMPARAN", "DURASI"]
            col_x = [cx - 370, cx - 280, cx - 100, cx + 80, cx + 230]
            y = 120
            for i, (hdr, hx) in enumerate(zip(headers, col_x)):
                hs = self.font_sm.render(hdr, True, C["accent"])
                self.screen.blit(hs, (hx, y))
            y += 30
            pygame.draw.line(self.screen, C["accent"], (cx - 380, y), (cx + 380, y), 1)
            y += 10

            medal_colors = [C["gold"], C["silver"], C["bronze"]]
            for i, entry in enumerate(top):
                row_col = medal_colors[i] if i < 3 else C["text"]
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else str(i + 1)
                vals = [medal, entry["name"], LEVELS[entry["level"]]["name"],
                        str(entry["rolls"]), f"{int(entry['duration'])}s"]
                for hx, v in zip(col_x, vals):
                    vs = self.font_sm.render(v, True, row_col)
                    self.screen.blit(vs, (hx, y))
                y += 35

        algo_note = [
            "Cara kerja Min-Heap:",
            "• heappush(score) → O(log n): skor baru masuk, heap otomatis rebalance",
            "• heappop() → O(log n): selalu ambil skor TERKECIL (lemparan paling sedikit)",
            "• Properti heap: parent ≤ children → root = minimum",
        ]
        ay = SCREEN_H - 130
        for ln in algo_note:
            s = self.font_xs.render(ln, True, C["subtext"])
            self.screen.blit(s, (cx - 350, ay))
            ay += 18

        self.draw_small_btn("🏠 MENU", cx - 50, SCREEN_H - 55, 100, 40, (80, 30, 30))
        self._menu_btn_lb = pygame.Rect(cx - 50, SCREEN_H - 55, 100, 40)

    # ── SCREEN: INFO ALGORITMA ──────────────────────────────────────────────────
    def draw_algo_info(self):
        self.draw_bg()
        cx = SCREEN_W // 2
        title = self.font_big.render("📘 ALGORITMA YANG DIGUNAKAN", True, C["accent"])
        self.screen.blit(title, (cx - title.get_width() // 2, 25))

        algos = [
            {
                "name": "1. Fisher-Yates Shuffle (O(n))",
                "color": C["p2"],
                "desc": [
                    "Digunakan: Mengacak posisi ular & tangga di Level LEGENDARIS",
                    "Cara kerja: Iterasi dari elemen terakhir ke pertama.",
                    "  Untuk setiap posisi i, pilih indeks acak j dari [0..i],",
                    "  lalu tukar arr[i] dengan arr[j].",
                    "Keunggulan: Menghasilkan permutasi MERATA (unbiased).",
                    "  Setiap kemungkinan susunan memiliki probabilitas sama.",
                    "Kompleksitas: O(n) waktu, O(1) ruang tambahan.",
                ],
            },
            {
                "name": "2. BFS — Breadth-First Search (O(V+E))",
                "color": C["ladder_h"],
                "desc": [
                    "Digunakan: AI mencari jalur TERPENDEK ke kotak 100.",
                    "  Juga menampilkan hint 'min. lemparan' untuk pemain manusia.",
                    "Cara kerja: Menggunakan queue (antrian FIFO).",
                    "  Eksplorasi semua tetangga sebelum maju ke level berikutnya.",
                    "  Dari kotak i, bisa lompat ke i+1 s/d i+6 (dadu 1-6).",
                    "  Cek ular/tangga saat mendarat di setiap kotak.",
                    "Kompleksitas: O(V+E) — V=100 kotak, E=koneksi dadu+ular+tangga.",
                ],
            },
            {
                "name": "3. Priority Queue / Min-Heap (O(log n))",
                "color": C["gold"],
                "desc": [
                    "Digunakan: Sistem Leaderboard — ranking skor terbaik.",
                    "Cara kerja: heapq Python (array-based binary min-heap).",
                    "  heappush(x) → O(log n): masukkan, heap rebalance otomatis.",
                    "  heappop()  → O(log n): ambil elemen TERKECIL (terbaik).",
                    "  Properti: parent ≤ children → root selalu minimum.",
                    "Keunggulan: Lebih efisien dari sorting O(n log n).",
                    "  Ranking real-time tanpa perlu sort ulang setiap game.",
                ],
            },
        ]

        y = 85
        for algo in algos:
            draw_rounded_rect(self.screen, C["panel"], (cx - 460, y, 920, 155), 12,
                              2, algo["color"])
            header = self.font_sm.render(algo["name"], True, algo["color"])
            self.screen.blit(header, (cx - 450, y + 8))
            dy = y + 32
            for line in algo["desc"]:
                ls = self.font_xs.render(line, True, C["text"])
                self.screen.blit(ls, (cx - 445, dy))
                dy += 17
            y += 168

        self.draw_small_btn("🏠 MENU", cx - 50, SCREEN_H - 50, 100, 40, (80, 30, 30))
        self._menu_btn_algo = pygame.Rect(cx - 50, SCREEN_H - 50, 100, 40)

    # ── EVENT HANDLING ──────────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state != "menu":
                        self.state = "menu"
                if event.key == pygame.K_SPACE and self.state == "game":
                    p = self.players[self.current_player]
                    if not p.is_ai and not self.dice_rolling:
                        self.roll_dice()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if self.state == "menu":
                    for lv, rect in self._level_btns:
                        if rect.collidepoint(mx, my):
                            self.selected_level = lv
                    if self._main_btn.collidepoint(mx, my):
                        self.level = self.selected_level
                        self.init_game()
                    if self._lb_btn_menu.collidepoint(mx, my):
                        self.state = "leaderboard"
                    if self._algo_btn_menu.collidepoint(mx, my):
                        self.state = "algo_info"

                elif self.state == "game":
                    p = self.players[self.current_player]
                    if self._roll_btn_rect and self._roll_btn_rect.collidepoint(mx, my):
                        if not p.is_ai and not self.dice_rolling:
                            self.roll_dice()
                    # Nav buttons
                    bx = PANEL_X
                    by = SCREEN_H - 85
                    if pygame.Rect(bx, by, 90, 35).collidepoint(mx, my):
                        self.state = "menu"
                    if pygame.Rect(bx + 95, by, 90, 35).collidepoint(mx, my):
                        self.state = "leaderboard"
                    if pygame.Rect(bx + 190, by, 90, 35).collidepoint(mx, my):
                        self.state = "algo_info"

                elif self.state == "result":
                    if hasattr(self, "_replay_btn") and self._replay_btn.collidepoint(mx, my):
                        self.init_game()
                    if hasattr(self, "_menu_btn_r") and self._menu_btn_r.collidepoint(mx, my):
                        self.state = "menu"
                    if hasattr(self, "_lb_btn_r") and self._lb_btn_r.collidepoint(mx, my):
                        self.state = "leaderboard"

                elif self.state == "leaderboard":
                    if hasattr(self, "_menu_btn_lb") and self._menu_btn_lb.collidepoint(mx, my):
                        self.state = "menu"

                elif self.state == "algo_info":
                    if hasattr(self, "_menu_btn_algo") and self._menu_btn_algo.collidepoint(mx, my):
                        self.state = "menu"

    # ── MAIN LOOP ───────────────────────────────────────────────────────────────
    def run(self):
        self._roll_btn_rect = None
        self._level_btns = []
        self._main_btn = pygame.Rect(0, 0, 0, 0)
        self._lb_btn_menu = pygame.Rect(0, 0, 0, 0)
        self._algo_btn_menu = pygame.Rect(0, 0, 0, 0)

        while True:
            self.handle_events()
            self.update()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.draw_bg()
                self.draw_board()
                self.draw_particles()
                self.draw_panel()
            elif self.state == "result":
                self.draw_result()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            elif self.state == "algo_info":
                self.draw_algo_info()

            pygame.display.flip()
            self.clock.tick(FPS)


# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("  🎲 GAME ULAR TANGGA — Python + Pygame Edition")
    print("=" * 65)
    print()
    print("  ALGORITMA YANG DIGUNAKAN:")
    print("  ① Fisher-Yates Shuffle  → Acak papan Legendaris  O(n)")
    print("  ② BFS (Breadth-First)   → AI & Hint terpendek    O(V+E)")
    print("  ③ Min-Heap Priority Q   → Sistem Leaderboard     O(log n)")
    print()
    print("  KONTROL:")
    print("  • Klik tombol [LEMPAR] atau tekan SPACE untuk lempar dadu")
    print("  • ESC untuk kembali ke menu")
    print("=" * 65)
    print()

    try:
        game = UlarTangga()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
