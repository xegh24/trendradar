#!/usr/bin/env python3
"""Validate data/trends.json and data/calendar.json.

Checks structure, allowed values, unique ids, area references, source URLs
and history consistency. Exits with status 1 on any error, so it can gate
commits and CI.

Usage: python3 scripts/validate.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOMENTUM = {"new", "up", "down", "stable"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EDITION = re.compile(r"^\d{4}-\d{2}$")
URL = re.compile(r"^https://[^\s]+$")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def check_trends(d: dict) -> None:
    for key in ("edition", "updated", "rings", "areas", "trends", "changelog"):
        if key not in d:
            err(f"trends.json: hiányzik a(z) '{key}' mező")
    if errors:
        return
    if not EDITION.match(d["edition"]):
        err(f"edition formátuma ÉÉÉÉ-HH legyen: {d['edition']}")
    if not DATE.match(d["updated"]):
        err(f"updated formátuma ÉÉÉÉ-HH-NN legyen: {d['updated']}")
    if sorted(d["rings"].keys()) != ["1", "2", "3", "4"]:
        err("rings: pontosan az 1–4 kulcsok kellenek")

    area_ids = [a["id"] for a in d["areas"]]
    if len(set(area_ids)) != len(area_ids):
        err("areas: ismétlődő terület-azonosító")

    seen = set()
    for i, t in enumerate(d["trends"]):
        where = f"trends[{i}] ({t.get('id', '?')})"
        for key in ("id", "title", "area", "ring", "impact", "indie", "horizon", "summary",
                    "figures", "why", "opportunity", "sources", "firstSeen", "momentum", "history"):
            if key not in t:
                err(f"{where}: hiányzik '{key}'")
        if any(k not in t for k in ("id", "area", "ring", "impact", "sources", "history")):
            continue
        if not re.match(r"^[a-z0-9-]{2,60}$", t["id"]):
            err(f"{where}: az id csak kisbetű, szám és kötőjel lehet")
        if t["id"] in seen:
            err(f"{where}: ismétlődő id")
        seen.add(t["id"])
        if t["area"] not in area_ids:
            err(f"{where}: ismeretlen terület '{t['area']}'")
        if t["ring"] not in (1, 2, 3, 4):
            err(f"{where}: ring 1–4 legyen")
        if t["impact"] not in (1, 2, 3):
            err(f"{where}: impact 1–3 legyen")
        if t.get("momentum") not in MOMENTUM:
            err(f"{where}: momentum értéke {sorted(MOMENTUM)} egyike legyen")
        if not EDITION.match(str(t.get("firstSeen", ""))):
            err(f"{where}: firstSeen formátuma ÉÉÉÉ-HH legyen")
        if len(t.get("summary", "")) > 400:
            warnings.append(f"{where}: az összefoglaló hosszabb 400 karakternél")
        if not t["sources"]:
            err(f"{where}: legalább egy forrás kell")
        elif len(t["sources"]) < 2:
            warnings.append(f"{where}: csak egy forrás van (a módszertan legalább hármat vár)")
        for s in t["sources"]:
            if not URL.match(s.get("url", "")):
                err(f"{where}: érvénytelen vagy nem https forrás: {s.get('url')}")
            if not s.get("title"):
                err(f"{where}: forrás cím nélkül")
        for f in t.get("figures", []):
            if not f.get("value") or not f.get("label"):
                err(f"{where}: szám érték vagy címke nélkül")
        if not t["history"]:
            err(f"{where}: üres előzmények")
        else:
            last = t["history"][-1]
            if last.get("ring") != t["ring"] or last.get("impact") != t["impact"]:
                err(f"{where}: az utolsó előzmény-bejegyzés nem egyezik a jelenlegi gyűrűvel/hatással")
            dates = [h.get("date", "") for h in t["history"]]
            if dates != sorted(dates):
                err(f"{where}: az előzmények nincsenek időrendben")

    editions = [c.get("edition") for c in d["changelog"]]
    if not editions or editions[-1] != d["edition"]:
        err("changelog: az utolsó bejegyzés kiadása egyezzen az aktuális edition-nel")
    for c in d["changelog"]:
        for ref in c.get("added", []) + [m.get("id") for m in c.get("moved", [])]:
            if ref not in seen and c is d["changelog"][-1]:
                err(f"changelog {c.get('edition')}: ismeretlen trend '{ref}'")


def check_calendar(c: dict, area_ids: set) -> None:
    for i, r in enumerate(c.get("reports", [])):
        if r.get("month") not in range(1, 13):
            err(f"calendar.reports[{i}]: month 1–12 legyen")
        if not URL.match(r.get("url", "")):
            err(f"calendar.reports[{i}]: érvénytelen url")
        for a in r.get("areas", []):
            if a not in area_ids:
                err(f"calendar.reports[{i}]: ismeretlen terület '{a}'")
    for i, m in enumerate(c.get("monitors", [])):
        if not URL.match(m.get("url", "")):
            err(f"calendar.monitors[{i}]: érvénytelen url")


def main() -> int:
    try:
        trends = json.loads((ROOT / "data/trends.json").read_text(encoding="utf-8"))
        calendar = json.loads((ROOT / "data/calendar.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"HIBA: nem olvasható adatfájl: {e}")
        return 1
    check_trends(trends)
    check_calendar(calendar, {a["id"] for a in trends.get("areas", [])})
    for w in warnings:
        print(f"figyelmeztetés: {w}")
    for e in errors:
        print(f"HIBA: {e}")
    n = len(trends.get("trends", []))
    print(f"{n} trend, {len(errors)} hiba, {len(warnings)} figyelmeztetés")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
