# Trendradar 2027

Interaktív radar a kialakuló globális trendekről 12 területen: AI, hardver és deep tech, közösségi média, appok és játék, fogyasztói kultúra, egészség, étel és utazás, pénz, energia és klíma, munka és oktatás, mobilitás, makrogazdaság.

Minden trendnél: érettség (gyenge jel → fősodor), becsült hatás, lendület (új / erősödik / gyengül), kulcsszámok, „miért most”, lehetőségek indie fejlesztőknek és creatoroknak, előzmények és források.

## Mit tud a felület

| Nézet | Mire jó |
|---|---|
| **Radar** | Radar-diagram és kártyák; szűrés terület, érettség, kulcsszó, indie-relevancia és követés szerint |
| **Követett** | A megjelölt trendek állapot szerint (Figyelem, Vizsgálom, Építek rá, Elengedtem) saját jegyzetekkel; másolható lista |
| **Saját jelek** | Gyors rögzítés: amit olvasol vagy látsz és trend lehet; Claude értékelheti, a havi frissítés feldolgozza |
| **Változások** | Erősödő, gyengülő és új trendek; kiadásonkénti változásnapló |
| **Jelentésnaptár** | Mikor jelennek meg a nagy éves jelentések, és mely forrásokat érdemes folyamatosan figyelni |
| **Módszertan** | Mikor lesz egy jelből trend, mit jelentenek a gyűrűk és a hatás, havi rutin |

A claude.ai-on közzétett változatban a követés és a jelek tartósan mentődnek, és a trendlapokon a „Kérdezd Claude-ot” gombok is működnek. A GitHub Pages-es változatban ezek az adatok csak a böngésződben maradnak.

## Szerkezet

```
index.html              a kész oldal (src/page.html-ből építve)
src/page.html           az oldal forrása (ezt kell szerkeszteni)
data/trends.json        a trendek, előzmények és változásnapló
data/calendar.json      jelentésnaptár és figyelt források
data/snapshots/         korábbi kiadások pillanatképei
scripts/validate.py     adatellenőrzés (CI is futtatja)
scripts/new_edition.py  havi kiadás: pillanatkép, lendület, változásnapló
scripts/check_links.py  forráslinkek élő-e (hetente CI-ból)
scripts/build_page.py   index.html előállítása
docs/FRISSITES.md       a havi frissítés lépései
```

## Helyi futtatás

Az oldal a `data/` fájlokat tölti be, ezért helyi szerver kell:

```bash
python3 -m http.server 8000
# majd: http://localhost:8000
```

## Közzététel GitHub Pages-en

A `.github/workflows/pages.yml` minden `main`-re küldött változás után közzéteszi az oldalt. Egyszer be kell kapcsolni: **Settings → Pages → Source: GitHub Actions**. Ingyenes fiókban a Pages csak publikus repóval működik.

## Havi frissítés röviden

```bash
python3 scripts/new_edition.py snapshot
# data/trends.json szerkesztése (lásd docs/FRISSITES.md)
python3 scripts/new_edition.py finalize --edition 2026-11 --summary "…"
python3 scripts/validate.py && python3 scripts/build_page.py
```

## Adatok és korlátok

Első kiadás: 2026. október 27. A számok a trendenként linkelt forrásokból származnak (Gartner, IMF, Sensor Tower, Counterpoint, BloombergNEF, Mintel, PwC és mások). Az érettségi besorolás és a hatás-pontszám szerkesztői becslés.
