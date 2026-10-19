"""
puzzles.py
==========
Testsudokun i tre svårighetsgrader + en generator för slumpade sudokun.

Varje sudoku är en sträng med 81 tecken, rad för rad. '.' = tom ruta.

Källor:
- "Lätt 1" är exemplet från Wikipedia-artikeln "Sudoku".
- "Svår 1" är Arto Inkalas sudoku som ofta kallas "världens svåraste" (2012).
- "Svår 2" är "hard1" från Peter Norvigs uppsats "Solving Every Sudoku Puzzle".
- "Svår 3" är exemplet från Wikipedia-artikeln "Sudoku solving algorithms"
  som är konstruerat för att vara så jobbigt som möjligt för vanlig backtracking.
- "Lätt 2" är första sudokut i Project Euler, problem 96. "Lätt 3" är ett vanligt
  exempelsudoku från nätet.
- "Medel 1-3" är skapade med generate_puzzle() nedan (seed 0, 6 och 3).
- Svårighetsgraden är satt efter hur många steg VANLIG backtracking behöver.
- Alla har unik lösning (det kontrolleras i test_sudoku.py).
"""

import random
from sudoku_solver import solve_smart, copy_board

PUZZLES = {
    "lätt": [
        "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79",
        "..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3",
    ],
    "medel": [
        "8..4........1...481.47..........2..52..86.9..9....5....9....56..5..48.....7......",
        "..4....8...37..4.......613......72...3..9...7.5.1...4.......9..9.24.831.8...3..2.",
        ".671....4..........34...57.842....1...1......9....3..8.....64.....4..78.....82.6.",
    ],
    "svår": [
        "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
        "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
        "..............3.85..1.2.......5.7.....4...1...9.......5......73..2.1........4...9",
    ],
}


def generate_solved_board(rng):
    """Skapar ett slumpat, fullständigt löst sudoku."""
    empty = [[0] * 9 for _ in range(9)]
    # Slumpa första raden och låt den smarta lösaren fylla i resten.
    first = list(range(1, 10))
    rng.shuffle(first)
    empty[0] = first
    board = solve_smart(empty).solution
    # Blanda dessutom rader inom samma band för mer variation
    for band in range(3):
        rows = [band * 3 + i for i in range(3)]
        rng.shuffle(rows)
        board[band * 3:band * 3 + 3] = [board[r] for r in rows]
    return board


def generate_puzzle(clues, seed=None):
    """
    Skapar ett sudoku med (ungefär) 'clues' givna siffror och UNIK lösning.

    Metod: börja från ett löst bräde och ta bort siffror i slumpad ordning.
    En siffra får bara tas bort om sudokut fortfarande har exakt en lösning
    (kontrolleras med solve_smart(count_limit=2)).
    Om det inte går att komma ner till 'clues' stannar vi där det tog stopp.
    """
    rng = random.Random(seed)
    board = generate_solved_board(rng)
    puzzle = copy_board(board)
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    filled = 81
    for (r, c) in cells:
        if filled <= clues:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if solve_smart(puzzle, count_limit=2).n_solutions != 1:
            puzzle[r][c] = saved           # blev inte unikt -> lägg tillbaka
        else:
            filled -= 1
    return puzzle


if __name__ == "__main__":
    from sudoku_solver import pretty
    p = generate_puzzle(30, seed=1)
    print("Genererat sudoku med 30 ledtrådar:\n")
    print(pretty(p))
