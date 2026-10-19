# Presentationsunderlag: Sudokulösare

Följer upplägget i "Final Presentation Format, Expectations" (5 minuter). Översätt till engelska om slides ska vara på engelska.

---

## Slide 1: Titel

**Sudoku Solver: Backtracking vs Smart Backtracking**
Gruppmedlemmar: [namn 1], [namn 2], [namn 3], [namn 4]

---

## Slide 2: Vad gör programmet och varför valde vi det?

- Programmet löser vilket 9x9-sudoku som helst och jämför två algoritmer.
- **Indata:** ett sudoku som en sträng med 81 tecken (`.` = tom ruta).
- **Utdata:** det lösta sudokut, antal steg, antal backningar och tid.
- **Regler:** varje rad, kolumn och 3x3-ruta ska innehålla 1-9 exakt en gång.
- Varför: sudoku är ett tydligt sökproblem. Det är lätt att förstå reglerna, men antalet möjliga sätt att fylla i ett sudoku är enormt, så valet av algoritm spelar stor roll.

---

## Slide 3: Demo

Kör live (eller visa `resultat/animation.gif`):

```
python sudoku_solver.py
python animate.py "Lätt 2" --visa
```

I animationen ser man att den smarta lösaren blir klar efter 51 steg på "Lätt 1", medan den vanliga behöver 4 208 steg.

---

## Slide 4: Kärnalgoritmen: backtracking

Problemformulering (samma struktur som i föreläsningen):

- **Starttillstånd:** sudokut med de givna siffrorna.
- **Handlingar:** skriv en siffra 1-9 i en tom ruta, om den inte bryter mot reglerna.
- **Måltest:** inga tomma rutor kvar.

Backtracking i ord:

1. Välj en tom ruta.
2. Testa en tillåten siffra och gå vidare till nästa ruta.
3. Om det tar stopp (ingen siffra passar): ta bort den senaste siffran och testa nästa alternativ. Det kallas att **backa**.
4. Upprepa tills alla rutor är ifyllda.

Pseudokod:

```
backtrack():
    om inga tomma rutor finns: return KLAR
    ruta = välj_ruta()
    för varje siffra d som är tillåten i ruta:
        skriv d i ruta
        om backtrack() == KLAR: return KLAR
        sudda ruta            # backning
    return MISSLYCKADES
```

---

## Slide 5: Skillnaden: hur väljer vi ruta?

Den **enda** skillnaden mellan metoderna är funktionen `välj_ruta()`:

| | Vanlig backtracking | Smart backtracking (MRV) |
|---|---|---|
| Vilken ruta? | Nästa tomma ruta i läsordning | Rutan med minst antal möjliga siffror |
| Ruta med 1 möjlighet | Hittas först när den är på tur | Fylls i direkt (som en människa gör) |
| Ruta med 0 möjligheter | Upptäcks sent | Upptäcks direkt, så den backar tidigt |

MRV står för "Minimum Remaining Values". Idén är att välja den ruta där det är minst sannolikt att man gissar fel. Det är en standardteknik inom problemlösning med villkor (constraint satisfaction).

---

## Slide 6: Resultat: experiment 1

Graf: `resultat/jamforelse_steg.png`

| Sudoku | Ledtrådar | Vanlig: steg | Smart: steg |
|---|---|---|---|
| Lätt 1 | 30 | 4 208 | 51 |
| Medel 1 | 23 | 92 512 | 58 |
| Svår 1 (Inkala) | 21 | 49 558 | 13 810 |
| Svår 2 (Norvig) | 17 | gav upp efter 2 000 000 | 718 |
| Svår 3 | 17 | gav upp efter 2 000 000 | 58 233 |

Slutsatser:

- Den smarta metoden behövde färre steg på alla nio testsudokun: från knappt 4 gånger färre till över 2 700 gånger färre.
- Den vanliga metoden klarade inte de två svåraste inom 2 miljoner steg. Den smarta löste dem på under 2 sekunder.

---

## Slide 7: Resultat: experiment 2 och fördjupning

Graf: `resultat/steg_mot_ledtradar.png`

- Vi ändrade **en sak i taget**: antalet ledtrådar (24-40), med 10 slumpade sudokun per nivå.
- Färre ledtrådar ger fler steg för båda metoderna, men den vanliga ökar mycket snabbare.

Saker vi upptäckte:

- **Ett smart steg kostar mer.** Den smarta metoden måste räkna möjliga siffror för alla tomma rutor varje gång. Ett steg tar därför flera gånger så lång tid som i den vanliga metoden. På "Svår 1" tog båda därför nästan lika lång tid, trots att den smarta gjorde fyra gånger färre steg.
- **Smart är inte alltid bäst.** Bland de slumpade sudokuna fanns fall där den vanliga metoden behövde färre steg. MRV är en tumregel, ingen garanti.
- **Inkalas sudoku är svårt för båda.** Där har många rutor 2-3 möjligheter, så även den smarta metoden måste gissa mycket.

---

## Slide 8: Hur AI hjälpte oss

Vi använde Claude (AI-assistent) i alla steg i kursens projektstruktur:

| Steg | Hur AI hjälpte |
|---|---|
| Välja uppgift | Föreslog projektidéer som passade kraven och tidsramen |
| Förstå algoritmen | Förklarade backtracking och MRV, gav pseudokod |
| Bygga | Skrev en första version av koden som vi sedan gick igenom |
| Testa | Föreslog testfall: redan löst, tomt, olösbart, ogiltigt sudoku |
| Experiment | Föreslog experimentet med antal ledtrådar och gjorde graferna |

Exempel på prompts vi använde:

> "Gör en sudokulösare som använder backtracking mot smart backtracking. Allt ska kodas i Python enligt instruktionerna i projektbeskrivningen."

> [Fyll i egna prompts ni använder när ni går igenom koden, t.ex. de nedan.]

Begränsningar vi märkte:

- AI:n gissade först fel på vilka sudokun som var "medelsvåra". Vi fick mäta och sortera om dem efter faktiskt antal steg.
- Ett av sudokuna AI:n först föreslog hade två lösningar. Det upptäcktes när vi lät programmet räkna antalet lösningar, och vi bytte ut det. Nu finns ett test som kontrollerar att alla testsudokun har unik lösning.

---

## Prompts att använda när ni lär er koden

Från kursens förslag (L2). Kör dem själva så har ni egna exempel att visa:

- "Förklara vad funktionen `choose_cell` i `sudoku_solver.py` gör och varför den slutar leta när den hittar en ruta med 1 möjlighet."
- "Spåra `solve_basic` steg för steg på de första fem tomma rutorna i 'Lätt 1'. Låt mig gissa nästa steg innan du visar det."
- "Varför tar ett steg längre tid i den smarta lösaren än i den vanliga?"
- "Ställ en fråga i taget om backtracking och MRV för att testa min förståelse. Vänta på mitt svar och ge feedback."

---

## Frågor ni kan få

- **Varför är vissa sudokun svåra för datorn?** Det beror på hur många gånger den måste gissa fel och backa, inte hur svårt det är för en människa.
- **Hittar backtracking alltid en lösning?** Ja, om det finns en. Den testar i värsta fall alla möjligheter (fullständig sökning).
- **Hur vet ni att lösningen är rätt?** Funktionen `is_solved` kontrollerar alla rader, kolumner och rutor, och testerna jämför med en känd lösning.
- **Vad räknas som ett steg?** Varje gång en siffra skrivs in i en ruta.
- **Hur skulle man kunna göra den ännu bättre?** Till exempel med constraint propagation: fyll i alla rutor som bara har en möjlighet innan man gissar, eller Knuths "Dancing Links".
