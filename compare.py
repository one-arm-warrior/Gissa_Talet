"""
compare.py
==========
Jämför vanlig backtracking med smart backtracking (MRV).

Experiment 1: Kör båda lösarna på de 9 testsudokuna (lätt/medel/svår).
              Mäter antal steg, antal backningar och tid.
              -> resultat/jamforelse_steg.png, resultat/jamforelse_tid.png,
                 resultat/jamforelse.csv

Experiment 2: Ändrar EN sak i taget: antalet givna siffror (ledtrådar).
              Genererar slumpade sudokun med 24-40 ledtrådar och mäter
              medelvärdet av antal steg för båda metoderna.
              -> resultat/steg_mot_ledtradar.png

Kör:   python compare.py           (hela jämförelsen, tar runt en minut)
       python compare.py --snabb   (färre slumpade sudokun, går fortare)
"""

import csv
import os
import statistics
import sys

import matplotlib
matplotlib.use("Agg")            # spara bilder utan att öppna fönster
import matplotlib.pyplot as plt

from sudoku_solver import parse, solve_basic, solve_smart, is_solved
from puzzles import PUZZLES, generate_puzzle

OUT_DIR = "resultat"
MAX_STEPS = 2_000_000            # vanlig backtracking får ge upp efter så här många steg
COLORS = {"basic": "#4C78A8", "smart": "#F58518"}


def run_experiment_1():
    rows = []
    print(f"{'Sudoku':10s} {'Ledtr.':>6s} | {'Vanlig: steg':>13s} {'tid (s)':>8s} | "
          f"{'Smart: steg':>12s} {'tid (s)':>8s} | {'Steg-kvot':>9s}")
    print("-" * 82)
    for level, texts in PUZZLES.items():
        for i, text in enumerate(texts, start=1):
            name = f"{level.capitalize()} {i}"
            puzzle = parse(text)
            clues = sum(v != 0 for row in puzzle for v in row)

            basic = solve_basic(puzzle, max_steps=MAX_STEPS)
            smart = solve_smart(puzzle)

            # Kontrollera att svaren faktiskt är korrekta
            assert is_solved(smart.solution, puzzle), name
            if not basic.gave_up:
                assert is_solved(basic.solution, puzzle), name

            ratio = basic.steps / smart.steps
            ge = ">=" if basic.gave_up else "  "
            print(f"{name:10s} {clues:6d} | {ge}{basic.steps:11d} {basic.time_s:8.3f} | "
                  f"{smart.steps:12d} {smart.time_s:8.3f} | {ge}{ratio:7.0f}x")
            rows.append({
                "sudoku": name, "ledtradar": clues,
                "vanlig_steg": basic.steps, "vanlig_backningar": basic.backtracks,
                "vanlig_tid_s": round(basic.time_s, 4), "vanlig_gav_upp": basic.gave_up,
                "smart_steg": smart.steps, "smart_backningar": smart.backtracks,
                "smart_tid_s": round(smart.time_s, 4),
            })
    print(f"\n'>=' betyder att vanlig backtracking gav upp efter {MAX_STEPS:,} steg.\n")
    return rows


def save_csv(rows):
    path = os.path.join(OUT_DIR, "jamforelse.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Sparade", path)


def bar_chart(rows, key_basic, key_smart, ylabel, title, filename):
    names = [r["sudoku"] for r in rows]
    x = range(len(names))
    w = 0.4
    fig, ax = plt.subplots(figsize=(11, 5))
    b1 = ax.bar([i - w / 2 for i in x], [r[key_basic] for r in rows], w,
                label="Vanlig backtracking", color=COLORS["basic"])
    ax.bar([i + w / 2 for i in x], [r[key_smart] for r in rows], w,
           label="Smart backtracking (MRV)", color=COLORS["smart"])
    # Markera staplar där vanlig backtracking gav upp
    for bar, r in zip(b1, rows):
        if r["vanlig_gav_upp"]:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), "gav\nupp",
                    ha="center", va="bottom", fontsize=8)
    ax.set_yscale("log")
    top = max(max(r[key_basic], r[key_smart]) for r in rows)
    ax.set_ylim(top=top * 6)     # plats för texten "gav upp" ovanför staplarna
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_ylabel(ylabel + " (logaritmisk skala)")
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Sparade", path)


def run_experiment_2(per_level):
    clue_levels = [24, 27, 30, 33, 36, 40]
    basic_means, smart_means, actual_clues = [], [], []
    print(f"Experiment 2: {per_level} slumpade sudokun per nivå")
    for clues in clue_levels:
        b_steps, s_steps, real = [], [], []
        for seed in range(per_level):
            puzzle = generate_puzzle(clues, seed=1000 * clues + seed)
            real.append(sum(v != 0 for row in puzzle for v in row))
            b_steps.append(solve_basic(puzzle, max_steps=MAX_STEPS).steps)
            s_steps.append(solve_smart(puzzle).steps)
        basic_means.append(statistics.mean(b_steps))
        smart_means.append(statistics.mean(s_steps))
        actual_clues.append(statistics.mean(real))
        print(f"  ~{clues} ledtrådar: vanlig {basic_means[-1]:>10.0f} steg, "
              f"smart {smart_means[-1]:>8.0f} steg (medel)")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(actual_clues, basic_means, "o-", color=COLORS["basic"], label="Vanlig backtracking")
    ax.plot(actual_clues, smart_means, "o-", color=COLORS["smart"], label="Smart backtracking (MRV)")
    ax.set_yscale("log")
    ax.set_xlabel("Antal givna siffror (ledtrådar)")
    ax.set_ylabel("Medelantal steg (logaritmisk skala)")
    ax.set_title(f"Färre ledtrådar = svårare sudoku ({per_level} sudokun per punkt)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "steg_mot_ledtradar.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Sparade", path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    quick = "--snabb" in sys.argv

    print("=== Experiment 1: testsudokun ===\n")
    rows = run_experiment_1()
    save_csv(rows)
    bar_chart(rows, "vanlig_steg", "smart_steg", "Antal steg",
              "Antal steg: vanlig vs smart backtracking", "jamforelse_steg.png")
    bar_chart(rows, "vanlig_tid_s", "smart_tid_s", "Tid (sekunder)",
              "Tid: vanlig vs smart backtracking", "jamforelse_tid.png")

    print("\n=== Experiment 2: antal ledtrådar ===\n")
    run_experiment_2(per_level=3 if quick else 10)


if __name__ == "__main__":
    main()
