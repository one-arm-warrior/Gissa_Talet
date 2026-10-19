"""
test_sudoku.py
==============
Tester som visar att lösarna fungerar som de ska.

Kör:  python test_sudoku.py      (eller: python -m pytest test_sudoku.py)
"""

from sudoku_solver import (parse, to_string, solve_basic, solve_smart,
                           is_solved, is_valid_placement)
from puzzles import PUZZLES, generate_puzzle

# Känd lösning till "Lätt 1" (Wikipedia-exemplet)
LATT1_SOLUTION = ("534678912672195348198342567859761423426853791"
                  "713924856961537284287419635345286179")


def test_parse_and_to_string():
    text = PUZZLES["lätt"][0]
    assert to_string(parse(text)) == text


def test_valid_placement():
    board = parse(PUZZLES["lätt"][0])
    assert not is_valid_placement(board, 0, 2, 5)   # 5 finns redan i raden
    assert not is_valid_placement(board, 0, 2, 9)   # 9 finns redan i 3x3-rutan
    assert not is_valid_placement(board, 0, 2, 8)   # 8 finns redan i kolumnen
    assert is_valid_placement(board, 0, 2, 4)       # 4 är tillåten (och rätt svar)


def test_both_solvers_give_known_solution():
    puzzle = parse(PUZZLES["lätt"][0])
    assert to_string(solve_basic(puzzle).solution) == LATT1_SOLUTION
    assert to_string(solve_smart(puzzle).solution) == LATT1_SOLUTION


def test_all_puzzles_unique_and_solved_correctly():
    for level, texts in PUZZLES.items():
        for text in texts:
            puzzle = parse(text)
            result = solve_smart(puzzle, count_limit=2)
            assert result.n_solutions == 1, f"{level}: inte unik lösning"
            assert is_solved(result.solution, puzzle), f"{level}: fel lösning"


def test_basic_and_smart_agree():
    # Samma sudoku ska ge samma lösning med båda metoderna
    for text in PUZZLES["lätt"] + PUZZLES["medel"]:
        puzzle = parse(text)
        assert solve_basic(puzzle).solution == solve_smart(puzzle).solution


def test_original_board_not_changed():
    puzzle = parse(PUZZLES["lätt"][0])
    before = to_string(puzzle)
    solve_basic(puzzle)
    solve_smart(puzzle)
    assert to_string(puzzle) == before


def test_already_solved_board():
    solved = parse(LATT1_SOLUTION)
    for solver in (solve_basic, solve_smart):
        result = solver(solved)
        assert result.solution == solved and result.steps == 0


def test_empty_board_can_be_solved():
    empty = [[0] * 9 for _ in range(9)]
    assert is_solved(solve_basic(empty).solution)
    assert is_solved(solve_smart(empty).solution)


def test_invalid_start_returns_none():
    # Två femmor i första raden -> omöjligt från början
    bad = parse("55" + "." * 79)
    assert solve_basic(bad).solution is None
    assert solve_smart(bad).solution is None


def test_unsolvable_but_no_duplicates():
    # Inga dubbletter, men ruta (0,8) kan inte få någon siffra:
    # rad 0 har 1-8 och raden under har en 9 i samma kolumn (och 3x3-ruta).
    text = "12345678." + "........9" + "." * 63
    puzzle = parse(text)
    assert solve_basic(puzzle).solution is None
    assert solve_smart(puzzle).solution is None


def test_step_limit():
    hard = parse(PUZZLES["svår"][2])
    result = solve_basic(hard, max_steps=1000)
    assert result.gave_up and result.solution is None and result.steps == 1000


def test_smart_uses_fewer_steps_on_test_puzzles():
    for text in PUZZLES["lätt"] + PUZZLES["medel"]:
        puzzle = parse(text)
        assert solve_smart(puzzle).steps < solve_basic(puzzle).steps


def test_generator_gives_unique_puzzle():
    puzzle = generate_puzzle(30, seed=42)
    assert solve_smart(puzzle, count_limit=2).n_solutions == 1


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
