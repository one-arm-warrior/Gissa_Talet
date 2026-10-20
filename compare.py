"""
compare.py
==========
Jämför binärsökning, slumpgissning och linjär sökning.

Experiment 1: Datorn gissar ALLA tal 0-100 med varje strategi.
              Slumpgissning körs 200 gånger per tal eftersom den ger olika
              resultat varje gång.
              -> resultat/medel_och_varsta.png   (medelvärde och värsta fall)
                 resultat/fordelning.png         (hur ofta det krävs k gissningar)
                 resultat/binar_per_tal.png      (antal gissningar för varje tal)
                 resultat/experiment1.csv

Experiment 2: Ändrar EN sak i taget: hur stort intervallet är
              (10, 100, 1 000, 10 000 och 100 000 tal).
              -> resultat/skalning.png
                 resultat/experiment2.csv

Kör:  python compare.py
"""

import csv
import os
import random
import statistics

import matplotlib
matplotlib.use("Agg")            # spara bilder utan att öppna fönster
import matplotlib.pyplot as plt

from guessing_game import STRATEGIES, NAMES, LOW, HIGH, count_guesses

OUT_DIR = "resultat"
RANDOM_RUNS = 200                # antal körningar per tal för slumpgissning
COLORS = {"binär": "#4C78A8", "slump": "#F58518", "linjär": "#54A24B"}


def save_figure(fig, filename):
    path = os.path.join(OUT_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Sparade", path)


def save_csv(rows, filename):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Sparade", path)


# ----------------------------------------------------------------------
# Experiment 1: alla tal 0-100
# ----------------------------------------------------------------------
def experiment_1():
    rng = random.Random(1)       # fast frö -> samma resultat varje körning
    counts = {}
    for name, strategy in STRATEGIES.items():
        runs = RANDOM_RUNS if name == "slump" else 1
        counts[name] = [count_guesses(secret, strategy, rng=rng)
                        for secret in range(LOW, HIGH + 1) for _ in range(runs)]

    print(f"{'Strategi':16s} {'Medel':>7s} {'Median':>7s} {'Bästa':>6s} {'Värsta':>7s}")
    print("-" * 47)
    rows = []
    for name, c in counts.items():
        mean = statistics.mean(c)
        print(f"{NAMES[name]:16s} {mean:7.2f} {statistics.median(c):7.1f} "
              f"{min(c):6d} {max(c):7d}")
        rows.append({"strategi": NAMES[name], "medel": round(mean, 3),
                     "median": statistics.median(c), "basta": min(c), "varsta": max(c)})
    print()
    save_csv(rows, "experiment1.csv")

    # Graf 1: medelvärde och värsta fall
    fig, ax = plt.subplots(figsize=(8, 5))
    names = list(counts)
    x = range(len(names))
    w = 0.38
    means = [statistics.mean(counts[n]) for n in names]
    worst = [max(counts[n]) for n in names]
    b1 = ax.bar([i - w / 2 for i in x], means, w, label="Medelvärde", color="#9ecae1")
    b2 = ax.bar([i + w / 2 for i in x], worst, w, label="Värsta fall",
                color=[COLORS[n] for n in names])
    for bars, values, fmt in ((b1, means, "{:.1f}"), (b2, worst, "{:d}")):
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, v * 1.15, fmt.format(v),
                    ha="center", va="bottom", fontsize=10)
    ax.set_yscale("log")
    ax.set_ylim(top=max(worst) * 4)
    ax.set_xticks(list(x))
    ax.set_xticklabels([NAMES[n] for n in names])
    ax.set_ylabel("Antal gissningar (logaritmisk skala)")
    ax.set_title("Antal gissningar för att hitta ett tal mellan 0 och 100")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save_figure(fig, "medel_och_varsta.png")

    # Graf 2: fördelning för binärsökning och slumpgissning
    fig, ax = plt.subplots(figsize=(8, 5))
    max_k = max(max(counts["binär"]), max(counts["slump"]))
    ks = range(1, max_k + 1)
    w = 0.4
    for offset, name in ((-w / 2, "binär"), (w / 2, "slump")):
        c = counts[name]
        share = [100 * c.count(k) / len(c) for k in ks]
        ax.bar([k + offset for k in ks], share, w, label=NAMES[name], color=COLORS[name])
    ax.set_xticks(list(ks))
    ax.set_xlabel("Antal gissningar")
    ax.set_ylabel("Andel av spelen (%)")
    ax.set_title("Hur många gissningar krävs? (tal 0-100)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save_figure(fig, "fordelning.png")

    # Graf 3: binärsökning, antal gissningar för varje tal
    fig, ax = plt.subplots(figsize=(11, 4))
    secrets = list(range(LOW, HIGH + 1))
    ax.bar(secrets, counts["binär"], color=COLORS["binär"], width=0.8)
    ax.set_xlabel("Talet man tänker på")
    ax.set_ylabel("Antal gissningar")
    ax.set_title("Binärsökning: 50 hittas direkt, 24 och 75 efter 2 gissningar, ... "
                 "inget tal kräver fler än 7")
    ax.set_xlim(-1, 101)
    ax.set_yticks(range(0, 8))
    ax.grid(axis="y", alpha=0.3)
    save_figure(fig, "binar_per_tal.png")


# ----------------------------------------------------------------------
# Experiment 2: hur stort är intervallet?
# ----------------------------------------------------------------------
def experiment_2():
    rng = random.Random(2)
    sizes = [10, 100, 1_000, 10_000, 100_000]
    results = {name: [] for name in STRATEGIES}
    rows = []
    print(f"{'Antal tal':>10s} | {'Binär medel':>11s} {'värsta':>7s} | "
          f"{'Slump medel':>11s} | {'Linjär medel':>12s}")
    print("-" * 64)
    for n in sizes:
        low, high = 0, n - 1
        # Binärsökning går snabbt, så vi testar ALLA tal i intervallet.
        binary = [count_guesses(s, STRATEGIES["binär"], low, high) for s in range(n)]
        # Linjär sökning och slumpgissning testas på ett urval av tal.
        sample = list(range(n)) if n <= 1000 else rng.sample(range(n), 300)
        runs = max(1, 2000 // len(sample))
        rand = [count_guesses(s, STRATEGIES["slump"], low, high, rng)
                for s in sample for _ in range(runs)]
        linear = [count_guesses(s, STRATEGIES["linjär"], low, high) for s in sample]

        b_mean, r_mean, l_mean = (statistics.mean(c) for c in (binary, rand, linear))
        results["binär"].append(b_mean)
        results["slump"].append(r_mean)
        results["linjär"].append(l_mean)
        print(f"{n:10,d} | {b_mean:11.2f} {max(binary):7d} | {r_mean:11.2f} | {l_mean:12.1f}")
        rows.append({"antal_tal": n, "binar_medel": round(b_mean, 3),
                     "binar_varsta": max(binary), "slump_medel": round(r_mean, 3),
                     "linjar_medel": round(l_mean, 1)})
    print()
    save_csv(rows, "experiment2.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    for name in STRATEGIES:
        ax.plot(sizes, results[name], "o-", color=COLORS[name], label=NAMES[name] + " (medel)")
    worst = [n.bit_length() for n in sizes]   # floor(log2 n) + 1
    ax.plot(sizes, worst, "--", color=COLORS["binär"], alpha=0.6,
            label="Binärsökning, värsta fall")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Antal möjliga tal (logaritmisk skala)")
    ax.set_ylabel("Antal gissningar (logaritmisk skala)")
    ax.set_title("Större intervall: linjär växer som n, binär och slump som log n")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    save_figure(fig, "skalning.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=== Experiment 1: alla tal 0-100 ===\n")
    experiment_1()
    print("\n=== Experiment 2: olika stora intervall ===\n")
    experiment_2()


if __name__ == "__main__":
    main()
