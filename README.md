# Sudokulösare: vanlig vs smart backtracking

Projekt i perspektivkursen DT2015 (HT26), "Programming Project with AI Assistance".

Programmet löser sudokun med två algoritmer och jämför dem:

- **Vanlig backtracking**: fyller rutorna i läsordning och testar 1-9. Blir det fel backar den.
- **Smart backtracking (MRV, "Minimum Remaining Values")**: fyller alltid den ruta som har *minst* möjliga siffror kvar. Om en ruta har 0 möjliga siffror backar den direkt.

## Krav

Python 3.10 eller senare och biblioteket matplotlib:

```
pip install matplotlib pillow
```

## Filer

| Fil | Vad den gör |
|---|---|
| `sudoku_solver.py` | Båda lösarna + hjälpfunktioner. Kör den för en snabb demo. |
| `puzzles.py` | 9 testsudokun (lätt/medel/svår) och en generator för slumpade sudokun med unik lösning. |
| `compare.py` | Jämförelsen. Skriver ut en tabell och sparar grafer i `resultat/`. |
| `animate.py` | Animation där båda lösarna arbetar sida vid sida. |
| `test_sudoku.py` | 13 tester som kontrollerar att allt fungerar. |
| `presentationsunderlag.md` | Text och siffror att använda i slides. |

## Så kör ni

```
python sudoku_solver.py          # demo: löser ett sudoku med båda metoderna
python test_sudoku.py            # kör alla tester
python compare.py                # hela jämförelsen (ca 40 s), grafer hamnar i resultat/
python compare.py --snabb        # snabbare version med färre slumpade sudokun
python animate.py                # sparar resultat/animation.gif (tar ett par minuter)
python animate.py "Lätt 2" --visa  # visar animationen i ett fönster istället
```

Tiderna i resultaten beror på datorn. Antalet steg är däremot alltid detsamma.

## Källor

- Testsudokun: Wikipedia ("Sudoku", "Sudoku solving algorithms"), Arto Inkala (2012),
  Peter Norvig, "Solving Every Sudoku Puzzle", Project Euler problem 96.
- Koden är skriven med hjälp av AI (Claude). Se `presentationsunderlag.md`.
