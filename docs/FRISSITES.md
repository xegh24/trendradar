# Havi frissítés

A radar havonta egyszer frissül, jellemzően a hónap első napjaiban. Ugyanezt a folyamatot követi a claude.ai ütemezett feladata is.

## 1. Bemenetek összegyűjtése

1. **Jelentésnaptár** (`data/calendar.json`): az előző hónapban megjelent nagy jelentések.
2. **Saját jelek**: a radar „Saját jelek” fülén beküldött, `uj` állapotú jelek. A claude.ai-os változatban ezek a radar adatbázisának `signals` gyűjteményében vannak.
3. **Követett trendek**: a `watch` gyűjtemény. Az „Építek rá” és „Vizsgálom” állapotúakhoz keress elsőként friss számot, versenytársat, eseményt.
4. **Folyamatos források**: Google Trends, Exploding Topics, Product Hunt, app-toplisták, TikTok Creative Center stb.

## 2. Pillanatkép

```bash
python3 scripts/new_edition.py snapshot
```

## 3. A `data/trends.json` szerkesztése

- **Meglévő trend**: frissítsd a `figures`, `why`, `sources` mezőket. Ha a bizonyítékok alapján belsőbb vagy külsőbb gyűrűbe kerül, írd át a `ring`-et, és adj hozzá egy `"_note"` mezőt az indoklással.
- **Gyűrű-változás nélküli lendület**: ha a friss adatok egyértelmű gyorsulást vagy lassulást mutatnak, de a gyűrű marad, add meg: `"_momentum": "up"` vagy `"down"`, és `"_note"`.
- **Új trend**: csak ha legalább három független, legalább két különböző típusú forrás támasztja alá (piaci adat, pénzmozgás, kulturális vagy szabályozási jel). Az id kisbetűs, kötőjeles. A `history` lehet üres lista, a szkript kitölti.
- **Lekerülő trend**: töröld a listából, ha elvesztette a relevanciáját vagy beolvadt egy másikba; a változásnapló rögzíti.
- **Részletes elemzés**: minden trend `deep` mezője (`context` bekezdések, `drivers`, `players`, `signals`, `risks`, `actions`). Új trendnél kötelező, meglévőnél frissítsd, ha a háttér érdemben változott.
- **Social média nézet** (`data/social.json`): frissítsd a kulcsszámokat (forrással), a platformok irányát és az idővonal közelgő dátumait; a lejárt idővonal-elemek maradhatnak.
- **Feldolgozott jelek**: minden jelnél állítsd a `status` mezőt `feldolgozva` vagy `elvetve` értékre, írj rövid `resolution` szöveget, és ha trendhez kötötted, add meg a `trendId`-t.

## 4. Lezárás

```bash
python3 scripts/new_edition.py finalize --edition ÉÉÉÉ-HH --summary "2–3 mondat a hónap legfontosabb változásairól"
python3 scripts/validate.py
python3 scripts/build_page.py
```

## 5. Közzététel

- **GitHub**: commit és push a `main` ágra; a Pages workflow közzéteszi.
- **claude.ai**: a radar artifact újrapublikálása ugyanarra a címre a `data/trends.json` és `data/calendar.json` fájlokkal.

## Minőségi szabályok

- Szám csak forrással kerülhet be, és a forrásnak elérhetőnek kell lennie (`scripts/check_links.py`).
- Egy forrásból legfeljebb rövid, saját szavas összefoglaló; szó szerinti idézet nem.
- Előrejelzésnél mindig jelöld, kinek az előrejelzése.
- A gyűrű és a hatás változtatását mindig indokold `_note`-ban.
