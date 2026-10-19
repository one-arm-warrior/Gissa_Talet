"""
sudoku_solver.py
================
Två sudokulösare som jämförs i projektet:

1. solve_basic  – vanlig backtracking
   Tar alltid FÖRSTA tomma rutan (rad för rad) och testar siffrorna 1-9 i ordning.

2. solve_smart  – smart backtracking (MRV = "Minimum Remaining Values")
   Tar alltid den tomma ruta som har FÄRST möjliga siffror kvar.
   Om någon ruta har 0 möjliga siffror vet vi direkt att vi gått fel och backar.

Ett bräde representeras som en lista med 9 listor (rader) med 9 heltal.
0 betyder tom ruta.

Båda lösarna returnerar ett SolveResult med:
    solution  – det lösta brädet (eller None om ingen lösning hittades)
    steps     – antal gånger en siffra placerades i en ruta (vårt mått på arbete)
    backtracks– antal gånger en siffra togs bort igen
    time_s    – tid i sekunder
    gave_up   – True om max_steps nåddes innan lösningen hittades
    events    – (valfritt) lista med (rad, kol, siffra) för animationen,
                siffra 0 betyder att rutan tömdes igen
"""

from dataclasses import dataclass, field
import time

SIZE = 9
BOX = 3
DIGITS = range(1, 10)


# ----------------------------------------------------------------------
# Hjälpfunktioner
# ----------------------------------------------------------------------
def parse(text):
    """Gör om en sträng med 81 tecken till ett bräde. '0' eller '.' = tom ruta."""
    chars = [c for c in text if c in "0123456789."]
    if len(chars) != 81:
        raise ValueError(f"Sudokut måste ha 81 rutor, fick {len(chars)}")
    values = [0 if c == "." else int(c) for c in chars]
    return [values[r * 9:(r + 1) * 9] for r in range(9)]


def to_string(board):
    """Gör om ett bräde till en sträng med 81 tecken ('.' för tomma rutor)."""
    return "".join(str(v) if v else "." for row in board for v in row)


def copy_board(board):
    return [row[:] for row in board]


def pretty(board):
    """Snygg utskrift av ett bräde i terminalen."""
    lines = []
    for r in range(9):
        if r in (3, 6):
            lines.append("------+-------+------")
        row = ""
        for c in range(9):
            if c in (3, 6):
                row += "| "
            row += (str(board[r][c]) if board[r][c] else ".") + " "
        lines.append(row.rstrip())
    return "\n".join(lines)


def box_index(r, c):
    """Vilken av de nio 3x3-rutorna (0-8) cellen (r, c) tillhör."""
    return (r // BOX) * BOX + c // BOX


def is_valid_placement(board, r, c, d):
    """Får siffran d stå i (r, c)? Kollar rad, kolumn och 3x3-ruta."""
    for i in range(9):
        if board[r][i] == d or board[i][c] == d:
            return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == d:
                return False
    return True


def is_consistent(board):
    """Finns det några dubbletter bland de givna siffrorna?"""
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d:
                board[r][c] = 0
                ok = is_valid_placement(board, r, c, d)
                board[r][c] = d
                if not ok:
                    return False
    return True


def is_solved(board, original=None):
    """Är brädet en korrekt, fullständig lösning (och stämmer den med originalet)?"""
    target = set(DIGITS)
    for i in range(9):
        if set(board[i]) != target:
            return False
        if {board[r][i] for r in range(9)} != target:
            return False
    for b in range(9):
        br, bc = (b // 3) * 3, (b % 3) * 3
        if {board[br + i][bc + j] for i in range(3) for j in range(3)} != target:
            return False
    if original is not None:
        for r in range(9):
            for c in range(9):
                if original[r][c] and original[r][c] != board[r][c]:
                    return False
    return True


@dataclass
class SolveResult:
    solution: list | None
    steps: int
    backtracks: int
    time_s: float
    gave_up: bool = False
    events: list = field(default_factory=list)


class _StepLimit(Exception):
    """Kastas internt när max_steps nås."""


# ----------------------------------------------------------------------
# 1. Vanlig backtracking
# ----------------------------------------------------------------------
def solve_basic(puzzle, max_steps=None, record=False):
    board = copy_board(puzzle)
    stats = {"steps": 0, "backtracks": 0}
    events = []

    # Lista över alla tomma rutor i läsordning (rad för rad)
    empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]

    def backtrack(k):
        if k == len(empties):          # alla tomma rutor ifyllda -> klart
            return True
        r, c = empties[k]              # alltid NÄSTA ruta i ordningen
        for d in DIGITS:
            if is_valid_placement(board, r, c, d):
                board[r][c] = d
                stats["steps"] += 1
                if record:
                    events.append((r, c, d))
                if max_steps and stats["steps"] >= max_steps:
                    raise _StepLimit
                if backtrack(k + 1):
                    return True
                board[r][c] = 0        # fel väg -> ångra
                stats["backtracks"] += 1
                if record:
                    events.append((r, c, 0))
        return False

    start = time.perf_counter()
    gave_up = False
    try:
        ok = is_consistent(board) and backtrack(0)
    except _StepLimit:
        ok, gave_up = False, True
    elapsed = time.perf_counter() - start
    return SolveResult(board if ok else None, stats["steps"], stats["backtracks"],
                       elapsed, gave_up, events)


# ----------------------------------------------------------------------
# 2. Smart backtracking (MRV)
# ----------------------------------------------------------------------
def solve_smart(puzzle, max_steps=None, record=False, count_limit=1):
    """
    count_limit: hur många lösningar vi letar efter innan vi stannar.
    Med count_limit=2 kan vi kontrollera om ett sudoku har en unik lösning
    (används av generatorn). Antalet hittade lösningar sparas i result.n_solutions.
    """
    board = copy_board(puzzle)
    stats = {"steps": 0, "backtracks": 0}
    events = []
    solutions = []

    # Mängder med siffror som redan används i varje rad, kolumn och 3x3-ruta.
    # Då går det snabbt att räkna ut vilka siffror som är möjliga i en ruta.
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d:
                rows[r].add(d)
                cols[c].add(d)
                boxes[box_index(r, c)].add(d)
            else:
                empties.append((r, c))

    def candidates(r, c):
        used = rows[r] | cols[c] | boxes[box_index(r, c)]
        return [d for d in DIGITS if d not in used]

    def choose_cell():
        """MRV: välj den tomma ruta som har minst antal möjliga siffror."""
        best, best_cands = None, None
        for (r, c) in empties:
            if board[r][c] == 0:
                cands = candidates(r, c)
                if best is None or len(cands) < len(best_cands):
                    best, best_cands = (r, c), cands
                    if len(cands) <= 1:      # bättre än så blir det inte
                        break
        return best, best_cands

    def backtrack():
        cell, cands = choose_cell()
        if cell is None:                     # inga tomma rutor kvar -> lösning
            solutions.append(copy_board(board))
            return len(solutions) >= count_limit
        if not cands:                        # återvändsgränd -> backa direkt
            return False
        r, c = cell
        b = box_index(r, c)
        for d in cands:
            board[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
            stats["steps"] += 1
            if record:
                events.append((r, c, d))
            if max_steps and stats["steps"] >= max_steps:
                raise _StepLimit
            if backtrack():
                return True
            board[r][c] = 0                  # ångra
            rows[r].discard(d); cols[c].discard(d); boxes[b].discard(d)
            stats["backtracks"] += 1
            if record:
                events.append((r, c, 0))
        return False

    start = time.perf_counter()
    gave_up = False
    try:
        if is_consistent(board):
            backtrack()
    except _StepLimit:
        gave_up = True
    elapsed = time.perf_counter() - start
    result = SolveResult(solutions[0] if solutions else None, stats["steps"],
                         stats["backtracks"], elapsed, gave_up, events)
    result.n_solutions = len(solutions)
    return result


SOLVERS = {
    "Vanlig backtracking": solve_basic,
    "Smart backtracking (MRV)": solve_smart,
}


if __name__ == "__main__":
    # Liten demo: lös ett sudoku med båda metoderna och skriv ut resultatet.
    from puzzles import PUZZLES
    name, text = "Medel 1", PUZZLES["medel"][0]
    puzzle = parse(text)
    print(f"Sudoku: {name}\n")
    print(pretty(puzzle), "\n")
    for label, solver in SOLVERS.items():
        res = solver(puzzle)
        print(f"{label:26s} steg={res.steps:>8d}  backningar={res.backtracks:>8d}  "
              f"tid={res.time_s * 1000:8.1f} ms  korrekt={is_solved(res.solution, puzzle)}")
    print("\nLösning:\n")
    print(pretty(solve_smart(puzzle).solution))
