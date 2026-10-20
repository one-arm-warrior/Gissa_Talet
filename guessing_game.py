"""
guessing_game.py
================
"Gissa talet": du tänker på ett heltal mellan 0 och 100 och datorn gissar.
Efter varje gissning svarar du om ditt tal är högre eller lägre.

Tre gissningsstrategier jämförs i projektet:

1. Binärsökning  - gissa alltid MITTEN av intervallet som är kvar.
                   Varje svar halverar intervallet.
2. Slumpgissning - gissa ett SLUMPAT tal i intervallet som är kvar.
3. Linjär sökning - gissa det MINSTA talet som är kvar: 0, 1, 2, 3, ...

Alla tre använder samma regel för att uppdatera intervallet [low, high]:
    svar "högre" -> nytt intervall blir [gissning + 1, high]
    svar "lägre" -> nytt intervall blir [low, gissning - 1]

Fuskupptäckt: om intervallet blir tomt (low > high) finns det inget tal som
stämmer med alla svar. Då har användaren svarat fel någon gång.

Kör:  python guessing_game.py            (spela mot binärsökning)
      python guessing_game.py slump      (spela mot slumpgissning)
      python guessing_game.py linjär     (spela mot linjär sökning)
"""

import random
import sys

LOW, HIGH = 0, 100


# ----------------------------------------------------------------------
# De tre strategierna. Alla får det intervall som är kvar och returnerar
# nästa gissning. rng är en slumpgenerator (används bara av slumpgissning).
# ----------------------------------------------------------------------
def binary_guess(low, high, rng=None):
    """Binärsökning: mitten av intervallet (avrundat nedåt)."""
    return (low + high) // 2


def random_guess(low, high, rng=None):
    """Slumpgissning: ett slumpat tal i intervallet."""
    rng = rng or random
    return rng.randint(low, high)


def linear_guess(low, high, rng=None):
    """Linjär sökning: det minsta talet som är kvar."""
    return low


STRATEGIES = {
    "binär": binary_guess,
    "slump": random_guess,
    "linjär": linear_guess,
}

NAMES = {
    "binär": "Binärsökning",
    "slump": "Slumpgissning",
    "linjär": "Linjär sökning",
}


# ----------------------------------------------------------------------
# Spelregler
# ----------------------------------------------------------------------
class CheatError(Exception):
    """Svaren går inte ihop: inget tal stämmer med alla svar."""


def update_interval(low, high, guess, answer):
    """Krymper intervallet efter ett svar. Kastar CheatError om det blir tomt."""
    if answer == "högre":
        low = guess + 1
    elif answer == "lägre":
        high = guess - 1
    else:
        raise ValueError(f"Okänt svar: {answer!r}")
    if low > high:
        raise CheatError(f"Inget tal kvar (low={low}, high={high})")
    return low, high


def auto_answer(secret, guess):
    """Svarar som en ärlig spelare som tänker på talet 'secret'."""
    if guess == secret:
        return "rätt"
    return "högre" if secret > guess else "lägre"


def play(secret, strategy, low=LOW, high=HIGH, rng=None):
    """
    Spelar ett helt spel automatiskt.

    Returnerar historiken: en lista med (low, high, gissning) för varje gissning.
    Antalet gissningar är len(historiken).
    """
    if not low <= secret <= high:
        raise ValueError(f"Talet {secret} ligger inte mellan {low} och {high}")
    history = []
    while True:
        guess = strategy(low, high, rng)
        history.append((low, high, guess))
        answer = auto_answer(secret, guess)
        if answer == "rätt":
            return history
        low, high = update_interval(low, high, guess, answer)


def count_guesses(secret, strategy, low=LOW, high=HIGH, rng=None):
    """Hur många gissningar behöver strategin för att hitta 'secret'?"""
    return len(play(secret, strategy, low, high, rng))


# ----------------------------------------------------------------------
# Interaktivt spel i terminalen
# ----------------------------------------------------------------------
ANSWER_KEYS = {"h": "högre", "l": "lägre", "r": "rätt"}


def ask(guess, number):
    """Frågar användaren tills ett giltigt svar ges."""
    while True:
        text = input(f"Gissning {number}: Är ditt tal {guess}?  "
                     f"(h = högre, l = lägre, r = rätt): ").strip().lower()
        if text in ANSWER_KEYS:
            return ANSWER_KEYS[text]
        if text in ANSWER_KEYS.values():
            return text
        print("   Svara med h, l eller r.")


def interval_bar(low, high, width=50):
    """Ritar intervallet som en textstapel, t.ex. [.....#######.......]"""
    start = round(low / (HIGH - LOW + 1) * width)
    end = max(start + 1, round((high + 1) / (HIGH - LOW + 1) * width))
    return "[" + "." * start + "#" * (end - start) + "." * (width - end) + "]"


def play_interactive(strategy_name="binär"):
    strategy = STRATEGIES[strategy_name]
    low, high = LOW, HIGH
    print(f"\nTänk på ett heltal mellan {LOW} och {HIGH}. Jag använder {NAMES[strategy_name].lower()}.")
    print(f"   {interval_bar(low, high)}  {high - low + 1} möjliga tal\n")
    number = 0
    while True:
        number += 1
        guess = strategy(low, high)
        answer = ask(guess, number)
        if answer == "rätt":
            word = "gissning" if number == 1 else "gissningar"
            print(f"\nJag hittade ditt tal {guess} på {number} {word}!")
            return number
        try:
            low, high = update_interval(low, high, guess, answer)
        except CheatError:
            print(f"\nNu går svaren inte ihop! Inget tal mellan {LOW} och {HIGH} "
                  f"passar alla dina svar. Har du svarat fel någonstans?")
            return None
        left = high - low + 1
        if left == 1:
            print(f"   {interval_bar(low, high)}  nu kan det bara vara {low}!\n")
        else:
            print(f"   {interval_bar(low, high)}  talet är mellan {low} och {high} "
                  f"({left} möjliga tal kvar)\n")


if __name__ == "__main__":
    name = sys.argv[1].lower() if len(sys.argv) > 1 else "binär"
    if name not in STRATEGIES:
        print(f"Okänd strategi '{name}'. Välj en av: {', '.join(STRATEGIES)}")
        sys.exit(1)
    play_interactive(name)
