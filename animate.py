"""
animate.py
==========
Animerar båda lösarna sida vid sida, så man ser skillnaden direkt.

  Vänster: vanlig backtracking     Höger: smart backtracking (MRV)

  Svarta siffror  = givna från början
  Blå siffror     = placerade av lösaren
  Röd ruta        = siffran togs precis bort igen (backning)

Varje bildruta i animationen motsvarar lika många steg för båda lösarna,
så den smarta lösaren blir klar mycket tidigare.

Kör:
  python animate.py                      -> sparar resultat/animation.gif (Lätt 1)
  python animate.py "Medel 3"            -> välj ett annat sudoku ur puzzles.py
  python animate.py "Lätt 1" --visa      -> visa i ett fönster istället för att spara

Tips: välj ett lätt sudoku. På svåra sudokun gör vanlig backtracking
miljontals steg och då blir animationen för lång.
"""

import os
import sys

import matplotlib
if "--visa" not in sys.argv:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

from sudoku_solver import parse, solve_basic, solve_smart, copy_board
from puzzles import PUZZLES

MAX_FRAMES = 300          # max antal bildrutor (håller GIF:en lagom stor)
FPS = 15


def find_puzzle(name):
    level, number = name.split()
    return PUZZLES[level.lower()][int(number) - 1]


def draw_grid(ax, title):
    ax.set_xlim(0, 9)
    ax.set_ylim(9, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    for i in range(10):
        lw = 2.5 if i % 3 == 0 else 0.6
        ax.plot([0, 9], [i, i], color="black", lw=lw)
        ax.plot([i, i], [0, 9], color="black", lw=lw)
    ax.set_title(title, fontsize=13)


class BoardView:
    """Håller koll på ett brädes texter och färger i animationen."""

    def __init__(self, ax, puzzle, events, title):
        self.puzzle = puzzle
        self.board = copy_board(puzzle)
        self.events = events
        self.pos = 0                                  # hur många händelser som spelats upp
        self.steps = 0
        self.backtracks = 0
        draw_grid(ax, title)
        self.highlight = Rectangle((0, 0), 1, 1, color="red", alpha=0.0)
        ax.add_patch(self.highlight)
        self.texts = [[ax.text(c + 0.5, r + 0.55, "", ha="center", va="center", fontsize=15)
                       for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                if puzzle[r][c]:
                    self.texts[r][c].set_text(str(puzzle[r][c]))
                    self.texts[r][c].set_fontweight("bold")
        self.counter = ax.text(4.5, 9.6, "", ha="center", va="center", fontsize=11)

    def advance_to(self, target):
        last = None
        while self.pos < min(target, len(self.events)):
            r, c, d = self.events[self.pos]
            self.board[r][c] = d
            self.texts[r][c].set_text(str(d) if d else "")
            self.texts[r][c].set_color("tab:blue")
            if d:
                self.steps += 1
            else:
                self.backtracks += 1
            last = (r, c, d)
            self.pos += 1
        # Markera senaste backning med röd ruta
        if last and last[2] == 0:
            self.highlight.set_xy((last[1], last[0]))
            self.highlight.set_alpha(0.35)
        else:
            self.highlight.set_alpha(0.0)
        done = self.pos >= len(self.events)
        status = "  KLAR!" if done else ""
        self.counter.set_text(f"steg: {self.steps}   backningar: {self.backtracks}{status}")
        self.counter.set_color("green" if done else "black")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    name = args[0] if args else "Lätt 1"
    puzzle = parse(find_puzzle(name))

    basic = solve_basic(puzzle, record=True, max_steps=200_000)
    smart = solve_smart(puzzle, record=True)
    if basic.gave_up:
        print("Vanlig backtracking behöver för många steg för en animation. Välj ett lättare sudoku.")
        return

    longest = max(len(basic.events), len(smart.events))
    per_frame = max(1, -(-longest // MAX_FRAMES))       # avrunda uppåt
    n_frames = -(-longest // per_frame) + FPS * 2        # + 2 sekunder paus i slutet

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 6.2))
    fig.suptitle(f"Sudoku: {name}   ({per_frame} händelser per bildruta)", fontsize=14)
    left = BoardView(ax1, puzzle, basic.events, "Vanlig backtracking")
    right = BoardView(ax2, puzzle, smart.events, "Smart backtracking (MRV)")
    fig.subplots_adjust(bottom=0.08)

    def update(frame):
        target = (frame + 1) * per_frame
        left.advance_to(target)
        right.advance_to(target)
        return []

    anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 / FPS, repeat=False)

    if "--visa" in sys.argv:
        plt.show()
    else:
        os.makedirs("resultat", exist_ok=True)
        path = os.path.join("resultat", "animation.gif")
        print(f"Sparar {path} ({n_frames} bildrutor), det kan ta ett par minuter...")
        anim.save(path, writer=PillowWriter(fps=FPS), dpi=80)
        print("Klart!")


if __name__ == "__main__":
    main()
