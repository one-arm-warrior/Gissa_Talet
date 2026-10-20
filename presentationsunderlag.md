# Presentationsunderlag: Gissa talet

Följer upplägget i "Final Presentation Format, Expectations" (5 minuter). Översätt till engelska om slides ska vara på engelska.

---

## Slide 1: Titel

**Guess the Number: Binary Search vs Random Guessing vs Linear Search**
Gruppmedlemmar: [namn 1], [namn 2], [namn 3], [namn 4]

---

## Slide 2: Vad gör programmet och varför valde vi det?

- Användaren tänker på ett heltal mellan 0 och 100. Datorn gissar, och användaren svarar högre, lägre eller rätt.
- **Indata:** användarens svar efter varje gissning.
- **Utdata:** nästa gissning, hur många tal som är kvar, och till sist antalet gissningar.
- **Regel:** "högre" betyder att talet ligger över gissningen, "lägre" att det ligger under.
- Varför: ett enkelt spel som alla förstår, men som visar en av de viktigaste algoritmerna inom datateknik: binärsökning. Samma idé används när man söker i sorterade listor och databaser.

---

## Slide 3: Demo

Kör live:

```
python guessing_game.py
```

Låt någon i publiken välja ett tal. Programmet hittar det på högst 7 gissningar och visar efter varje svar hur intervallet krymper.

Visa också fuskupptäckten: svara "högre" hela tiden. Till slut säger programmet att svaren inte går ihop.

Animation: `resultat/animation.gif` visar alla tre strategierna leta efter talet 73 samtidigt. Binärsökning är klar efter 6 gissningar, linjär sökning behöver 74.

---

## Slide 4: Kärnalgoritmen: binärsökning

Problemformulering:

- **Starttillstånd:** alla tal 0-100 är möjliga, intervallet [0, 100].
- **Handling:** gissa ett tal i intervallet.
- **Ny information:** "högre" ger intervallet [gissning + 1, high], "lägre" ger [low, gissning - 1].
- **Måltest:** svaret är "rätt".

Pseudokod:

```
low = 0, high = 100
upprepa:
    gissning = (low + high) // 2      # mitten, avrundat nedåt
    om svaret är "rätt":   klart
    om svaret är "högre":  low  = gissning + 1
    om svaret är "lägre":  high = gissning - 1
    om low > high:         användaren har svarat fel (fusk)
```

Bild: `resultat/intervall_binar.png`. Talet 73 hittas så här: 50 (högre), 75 (lägre), 62 (högre), 68 (högre), 71 (högre), 73 (rätt). Antalet möjliga tal går 101, 50, 24, 12, 6, 3.

---

## Slide 5: Varför högst 7 gissningar?

- Efter varje svar finns högst hälften av talen kvar.
- Med k gissningar kan binärsökning skilja på högst 1 + 2 + 4 + ... + 2^(k-1) = 2^k - 1 tal:
  1 tal hittas på första gissningen, 2 tal på andra, 4 tal på tredje, och så vidare.
- 6 gissningar räcker för 2^6 - 1 = 63 tal. Det är för lite, eftersom det finns 101 tal.
- 7 gissningar räcker för 2^7 - 1 = 127 tal. Det räcker.
- Alltså behövs högst 7 gissningar. Programmets test kontrollerar detta för alla 101 tal.

Bild: `resultat/binar_per_tal.png` visar antalet gissningar för varje tal. 50 hittas direkt, 24 och 75 efter 2 gissningar och inget tal kräver mer än 7.

---

## Slide 6: Resultat: experiment 1 (alla tal 0-100)

Graf: `resultat/medel_och_varsta.png`

| Strategi | Medel | Värsta fall |
|---|---|---|
| Binärsökning | 5,81 | 7 |
| Slumpgissning | 7,50 | 18 |
| Linjär sökning | 51 | 101 |

- Binärsökning och linjär sökning ger alltid samma resultat, så där testade vi varje tal en gång.
- Slumpgissning ger olika resultat varje gång, så där körde vi varje tal 200 gånger (20 200 spel).
- Binärsökningens medelvärde är exakt 587/101: 1 tal tar 1 gissning, 2 tal tar 2, 4 tal tar 3, 8 tal tar 4, 16 tal tar 5, 32 tal tar 6 och de resterande 38 talen tar 7.

Graf: `resultat/fordelning.png` visar hur ofta det krävs ett visst antal gissningar. Binärsökning ligger alltid mellan 1 och 7. Slumpgissning sprider sig mycket mer.

---

## Slide 7: Resultat: experiment 2 och fördjupning

Graf: `resultat/skalning.png`

Vi ändrade **en sak i taget**: hur många tal som är möjliga.

| Antal tal | Binär (medel) | Binär (värsta) | Slump (medel) | Linjär (medel) |
|---|---|---|---|---|
| 10 | 2,90 | 4 | 3,39 | 5,5 |
| 100 | 5,80 | 7 | 7,54 | 50,5 |
| 1 000 | 8,99 | 10 | 11,95 | 500,5 |
| 10 000 | 12,36 | 14 | 16,77 | ca 5 000 |
| 100 000 | 15,69 | 17 | 21,21 | ca 50 000 |

(För 10 000 och 100 000 tal testades linjär sökning och slumpgissning på 300 slumpade tal.)

Saker vi upptäckte:

- **Linjär sökning växer lika snabbt som antalet tal.** 10 gånger fler tal ger 10 gånger fler gissningar.
- **Binärsökning växer nästan inte alls.** 10 gånger fler tal ger bara ungefär 3 gissningar till. 100 000 tal kräver högst 17 gissningar.
- **Slumpgissning är förvånansvärt bra i medel.** I medel behöver den bara 17-36 % fler gissningar än binärsökning. Men den kan ha otur: värsta fallet på 0-100 var 18 gissningar mot 7.
- **Fuskupptäckt kommer gratis.** Eftersom programmet håller koll på intervallet märker det direkt om intervallet blir tomt, alltså om inget tal passar alla svar.

---

## Slide 8: Hur AI hjälpte oss

Vi använde Claude (AI-assistent) i alla steg i kursens projektstruktur:

| Steg | Hur AI hjälpte |
|---|---|
| Välja uppgift | Bedömde vår idé och föreslog att jämföra tre strategier så att den passar kursens krav |
| Förstå algoritmen | Förklarade binärsökning och varför den behöver högst 7 gissningar |
| Bygga | Skrev en första version av koden som vi sedan gick igenom |
| Testa | Föreslog testfall: talen 0 och 100, intervall med ett enda tal, fusk, ogiltiga svar |
| Experiment | Föreslog experimentet med olika stora intervall och gjorde graferna |

Exempel på prompts vi använde:

> "Vi valde istället att göra ett program där man väljer en siffra mellan 0-100. Sen ska programmet gissa talet genom att man svarar högre eller lägre. Är detta en idé som fungerar bra för projektet?"

> "Gör gärna koden och presentationsunderlaget, och gör extrastegen (ambitionsnivå 2)."

> [Fyll i egna prompts ni använder när ni går igenom koden, t.ex. de nedan.]

Begränsningar vi märkte:

- AI:n skrev först i en graf att talet 25 hittas efter 2 gissningar. När vi kontrollerade grafen såg vi att det är 24: mitten av 0-49 är (0 + 49) // 2 = 24, eftersom divisionen avrundar nedåt. Det visar att man måste kontrollera det AI:n skriver.
- [Lägg till egna exempel om ni hittar fler.]

---

## Prompts att använda när ni lär er koden

Från kursens förslag (L2). Kör dem själva så har ni egna exempel att visa:

- "Förklara vad funktionen `update_interval` i `guessing_game.py` gör och hur den upptäcker fusk."
- "Spåra binärsökningen steg för steg när talet är 37. Låt mig gissa nästa gissning innan du visar den."
- "Varför blir värsta fallet för slumpgissning så mycket sämre än för binärsökning, fast medelvärdet ligger nära?"
- "Ställ en fråga i taget om binärsökning för att testa min förståelse. Vänta på mitt svar och ge feedback."

---

## Frågor ni kan få

- **Varför gissar binärsökningen 50 och inte 51?** Mitten räknas som (0 + 100) // 2 = 50. Divisionen `//` avrundar nedåt.
- **Kan man göra bättre än binärsökning?** Inte i värsta fall. Varje svar ger bara två riktningar (högre eller lägre), så med 7 frågor kan man som mest skilja på 127 tal. 6 frågor räcker inte för 101 tal.
- **Hur vet ni att programmet är rätt?** Testerna kör alla 101 tal med varje strategi och kontrollerar att rätt tal hittas, att gissningen alltid ligger i intervallet och att ingen gissning upprepas.
- **Vad händer om användaren ljuger en gång?** Då kan programmet hamna fel. Om svaren motsäger varandra upptäcks det, men en lögn som inte ger en motsägelse kan inte upptäckas.
- **Var används binärsökning i verkligheten?** Sökning i sorterade listor, databaser och ordböcker, och i `git bisect` som letar upp vilken ändring som orsakade en bugg.
