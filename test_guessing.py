"""
test_guessing.py
================
Tester som visar att programmet fungerar som det ska.

Kör:  python test_guessing.py      (eller: python -m pytest test_guessing.py)
"""

import random

from guessing_game import (STRATEGIES, LOW, HIGH, CheatError, play, count_guesses,
                           update_interval, auto_answer, binary_guess)

binary = STRATEGIES["binär"]
rand = STRATEGIES["slump"]
linear = STRATEGIES["linjär"]


def test_first_binary_guess_is_50():
    assert binary_guess(0, 100) == 50


def test_binary_finds_every_number_in_at_most_7_guesses():
    counts = [count_guesses(s, binary) for s in range(LOW, HIGH + 1)]
    assert max(counts) == 7
    assert counts[50] == 1                       # 50 hittas direkt


def test_binary_worst_case_formula():
    # Med n möjliga tal behöver binärsökning som mest floor(log2 n) + 1 gissningar.
    # I Python är det samma sak som n.bit_length().
    for n in [1, 2, 3, 7, 8, 100, 101, 1000, 1024]:
        worst = max(count_guesses(s, binary, 0, n - 1) for s in range(n))
        assert worst == n.bit_length(), n


def test_linear_needs_secret_plus_one_guesses():
    for s in range(LOW, HIGH + 1):
        assert count_guesses(s, linear) == s + 1


def test_random_always_finds_the_number():
    rng = random.Random(0)
    for s in range(LOW, HIGH + 1):
        history = play(s, rand, rng=rng)
        assert history[-1][2] == s


def test_guesses_always_inside_interval_and_never_repeated():
    rng = random.Random(1)
    for strategy in STRATEGIES.values():
        for s in range(LOW, HIGH + 1):
            history = play(s, strategy, rng=rng)
            guesses = [g for _, _, g in history]
            assert len(guesses) == len(set(guesses))
            assert all(low <= g <= high for low, high, g in history)


def test_update_interval():
    assert update_interval(0, 100, 50, "högre") == (51, 100)
    assert update_interval(0, 100, 50, "lägre") == (0, 49)


def test_auto_answer():
    assert auto_answer(73, 50) == "högre"
    assert auto_answer(73, 80) == "lägre"
    assert auto_answer(73, 73) == "rätt"


def test_cheat_is_detected():
    # Spelaren säger "högre" hela tiden, även när datorn gissar 100.
    low, high = LOW, HIGH
    try:
        while True:
            low, high = update_interval(low, high, binary(low, high), "högre")
        assert False, "fusket upptäcktes inte"
    except CheatError:
        assert low == 100 and high == 100        # sista gissningen var 100


def test_cheat_contradicting_answers():
    # "Högre än 50" och sedan "lägre än 51" -> inget tal kvar
    low, high = update_interval(0, 100, 50, "högre")
    try:
        update_interval(low, high, 51, "lägre")
        assert False, "fusket upptäcktes inte"
    except CheatError:
        pass


def test_invalid_answer_and_secret():
    for bad_call in (lambda: update_interval(0, 100, 50, "kanske"),
                     lambda: play(101, binary),
                     lambda: play(-1, binary)):
        try:
            bad_call()
            assert False
        except ValueError:
            pass


def test_interval_with_one_number():
    assert count_guesses(5, binary, 5, 5) == 1


def test_binary_better_than_random_better_than_linear_on_average():
    rng = random.Random(2)
    mean = {}
    for name, strategy in STRATEGIES.items():
        counts = [count_guesses(s, strategy, rng=rng) for s in range(LOW, HIGH + 1) for _ in range(20)]
        mean[name] = sum(counts) / len(counts)
    assert mean["binär"] < mean["slump"] < mean["linjär"]


if __name__ == "__main__":
    tests = [(name, f) for name, f in globals().items()
             if name.startswith("test_") and callable(f)]
    failed = 0
    for name, f in tests:
        try:
            f()
            print(f"OK    {name}")
        except AssertionError as e:
            failed += 1
            print(f"FEL   {name}  {e}")
    print(f"\n{len(tests) - failed} av {len(tests)} tester lyckades.")
