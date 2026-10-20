# Gissa talet: binärsökning vs slumpgissning vs linjär sökning

Projekt i perspektivkursen DT2015 (HT26), "Programming Project with AI Assistance".

Du tänker på ett heltal mellan 0 och 100. Datorn gissar, och du svarar **högre**, **lägre** eller **rätt**.
Programmet jämför tre sätt att gissa:

- **Binärsökning**: gissa mitten av intervallet som är kvar. Varje svar halverar intervallet.
- **Slumpgissning**: gissa ett slumpat tal i intervallet som är kvar.
- **Linjär sökning**: gissa 0, 1, 2, 3, ... tills det blir rätt.

Extra funktioner:

- **Intervallet visas** efter varje svar, både i terminalen och i en animation.
- **Fuskupptäckt**: om svaren motsäger varandra säger programmet till.

## Krav

Python 3.10 eller senare och biblioteket matplotlib:

```
pip install matplotlib pillow
```

## Filer

| Fil | Vad den gör |
|---|---|
| `guessing_game.py` | Strategierna, spelreglerna och det interaktiva spelet. |
| `compare.py` | Experimenten. Skriver ut tabeller och sparar grafer i `resultat/`. |
| `animate.py` | Bild och animation som visar hur intervallet krymper. |
| `test_guessing.py` | 13 tester som kontrollerar att allt fungerar. |
| `presentationsunderlag.md` | Text och siffror att använda i slides. |

## Så kör ni

```
python guessing_game.py           # spela mot binärsökning
python guessing_game.py slump     # spela mot slumpgissning (eller: linjär)
python test_guessing.py           # kör alla tester
python compare.py                 # experimenten (ca 10 s), grafer hamnar i resultat/
python animate.py                 # bild + animation för talet 73 (ca 20 s)
python animate.py 37 --visa       # annat tal, visa animationen i ett fönster
```

## Källor

- Binärsökning: standardalgoritm, se t.ex. Wikipedia "Binary search".
- Koden är skriven med hjälp av AI (Claude). Se `presentationsunderlag.md`.
