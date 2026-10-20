"""
animate.py
==========
Visar hur intervallet krymper efter varje gissning.

1. resultat/intervall_binar.png
   Stillbild: binärsökningens intervall gissning för gissning.

2. resultat/animation.gif
   Animation där alla tre strategierna letar efter samma tal samtidigt.
     Blå stapel  = tal som fortfarande är möjliga
     Röd linje   = datorns gissning
     Svart pil   = talet man tänker på

Kör:
  python animate.py              -> talet 73
  python animate.py 37           -> välj ett annat tal (0-100)
  python animate.py 37 --visa    -> visa animationen i ett fönster istället för att spara
"""

import os
import random
import sys

import matplotlib
if "--visa" not in sys.argv:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

from guessing_game import STRATEGIES, NAMES, LOW, HIGH, play, auto_answer

OUT_DIR = "resultat"
FPS = 3
COLORS = {"binär": "#4C78A8", "slump": "#F58518", "linjär": "#54A24B"}


# ----------------------------------------------------------------------
# Stillbild: binärsökningens intervall per gissning
# ----------------------------------------------------------------------
def static_binary_figure(secret):
    history = play(secret, STRATEGIES["binär"])
    fig, ax = plt.subplots(figsize=(10, 0.8 * len(history) + 1.6))
    for i, (low, high, guess) in enumerate(history, start=1):
        ax.barh(i, high - low + 1, left=low - 0.5, height=0.55,
                color=COLORS["binär"], alpha=0.35)
        ax.plot(guess, i, "o", color="red")
        answer = auto_answer(secret, guess)
        ax.text(101.5, i, f"gissar {guess} -> {answer}   ({high - low + 1} möjliga tal)",
                va="center", fontsize=10)
    ax.axvline(secret, color="black", ls=":", lw=1)
    ax.set_xlim(-1, 101)
    ax.set_ylim(len(history) + 0.7, 0.3)
    ax.set_yticks(range(1, len(history) + 1))
    ax.set_yticklabels([f"Gissning {i}" for i in range(1, len(history) + 1)])
    ax.set_xlabel("Möjliga tal")
    ax.set_title(f"Binärsökning efter talet {secret}: intervallet halveras varje gång")
    fig.tight_layout()
    fig.subplots_adjust(right=0.72)
    path = os.path.join(OUT_DIR, "intervall_binar.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Sparade", path)


# ----------------------------------------------------------------------
# Animation: alla tre strategier samtidigt
# ----------------------------------------------------------------------
class Row:
    """En rad i animationen: en tallinje för en strategi."""

    def __init__(self, ax, name, secret, history):
        self.name = name
        self.secret = secret
        self.history = history
        ax.set_xlim(-1, 101)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xticks(range(0, 101, 10))
        ax.add_patch(Rectangle((-0.5, 0.35), 101, 0.3, color="#e5e5e5"))
        self.interval = Rectangle((-0.5, 0.35), 101, 0.3, color=COLORS[name], alpha=0.6)
        ax.add_patch(self.interval)
        self.guess_line = ax.axvline(-10, ymin=0.25, ymax=0.75, color="red", lw=2.5)
        ax.annotate("", xy=(secret, 0.33), xytext=(secret, 0.05),
                    arrowprops=dict(arrowstyle="->", color="black"))
        self.title = ax.set_title("", loc="left", fontsize=11)

    def show(self, frame):
        k = min(frame, len(self.history) - 1)
        low, high, guess = self.history[k]
        self.interval.set_x(low - 0.5)
        self.interval.set_width(high - low + 1)
        self.guess_line.set_xdata([guess, guess])
        answer = auto_answer(self.secret, guess)
        if frame >= len(self.history) - 1:
            self.title.set_text(f"{NAMES[self.name]}: KLAR, hittade {self.secret} "
                                f"på {len(self.history)} gissningar")
            self.title.set_color("green")
        else:
            self.title.set_text(f"{NAMES[self.name]}: gissning {k + 1}: {guess} -> {answer}   "
                                f"({high - low + 1} möjliga tal)")
            self.title.set_color("black")


def animation(secret):
    rng = random.Random(3)
    histories = {name: play(secret, s, rng=rng) for name, s in STRATEGIES.items()}
    longest = max(len(h) for h in histories.values())
    n_frames = longest + FPS * 3                  # + 3 sekunder paus i slutet

    fig, axes = plt.subplots(3, 1, figsize=(10, 6.5))
    fig.suptitle(f"Datorn letar efter talet {secret}", fontsize=14)
    rows = [Row(ax, name, secret, histories[name]) for ax, name in zip(axes, STRATEGIES)]
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.7, top=0.88)

    def update(frame):
        for row in rows:
            row.show(frame)
        return []

    anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 / FPS, repeat=False)
    if "--visa" in sys.argv:
        plt.show()
    else:
        path = os.path.join(OUT_DIR, "animation.gif")
        print(f"Sparar {path} ({n_frames} bildrutor)...")
        anim.save(path, writer=PillowWriter(fps=FPS), dpi=80)
        print("Sparade", path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    secret = int(args[0]) if args else 73
    if not LOW <= secret <= HIGH:
        print(f"Talet måste vara mellan {LOW} och {HIGH}.")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    static_binary_figure(secret)
    animation(secret)


if __name__ == "__main__":
    main()
