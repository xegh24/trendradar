#!/usr/bin/env python3
"""Start and close a monthly edition of the radar.

1) Before editing:   python3 scripts/new_edition.py snapshot
   Saves the current data/trends.json to data/snapshots/<edition>.json.

2) Edit data/trends.json: change ring/impact, figures, sources, add or remove
   trends. For any trend you may add a temporary "_note" field explaining the
   change; it goes into that trend's history and the changelog.

3) After editing:    python3 scripts/new_edition.py finalize --edition 2026-11 \
                         --summary "Rövid összefoglaló a hónap változásairól"
   Compares with the latest snapshot, sets each trend's momentum
   (new / up / down / stable), appends history entries, writes a changelog
   entry and updates edition + date. Then run scripts/validate.py.

Momentum rule: up = moved to an inner ring or impact increased; down = moved
outward or impact decreased; a "_momentum" field ("up"/"down"/"stable") on a
trend overrides the rule when the data shifted without a ring change.
"""
import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "trends.json"
SNAPS = ROOT / "data" / "snapshots"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snapshot() -> int:
    d = load(DATA)
    SNAPS.mkdir(parents=True, exist_ok=True)
    target = SNAPS / f"{d['edition']}.json"
    shutil.copyfile(DATA, target)
    print(f"Pillanatkép mentve: {target.relative_to(ROOT)}")
    return 0


def finalize(edition: str, summary: str, today: str) -> int:
    snaps = sorted(SNAPS.glob("*.json"))
    if not snaps:
        print("Nincs pillanatkép. Előbb futtasd: new_edition.py snapshot")
        return 1
    prev = load(snaps[-1])
    if prev["edition"] == edition:
        print(f"A legutóbbi pillanatkép már ehhez a kiadáshoz tartozik ({edition}).")
        return 1
    d = load(DATA)
    old = {t["id"]: t for t in prev["trends"]}
    added, moved = [], []
    for t in d["trends"]:
        note = t.pop("_note", "").strip()
        override = t.pop("_momentum", "").strip()
        o = old.get(t["id"])
        if o is None:
            t["momentum"] = "new"
            t.setdefault("firstSeen", edition)
            t["firstSeen"] = t.get("firstSeen") or edition
            t["history"] = [{"date": today, "ring": t["ring"], "impact": t["impact"],
                             "note": note or "Első felvétel a radarra."}]
            added.append(t["id"])
            continue
        delta = (t["ring"] - o["ring"]) * 10 + (t["impact"] - o["impact"])
        mom = "up" if delta > 0 else "down" if delta < 0 else "stable"
        if override in ("up", "down", "stable"):
            mom = override
        t["momentum"] = mom
        if delta != 0 or note:
            t["history"].append({"date": today, "ring": t["ring"], "impact": t["impact"],
                                 "note": note or "Besorolás módosítva."})
        if mom != "stable":
            moved.append({"id": t["id"], "from": o["ring"], "to": t["ring"], "momentum": mom,
                          "note": note or ("Belsőbb gyűrűbe lépett vagy nőtt a hatása." if mom == "up"
                                           else "Kifelé mozdult vagy gyengült.")})
    removed = sorted(set(old) - {t["id"] for t in d["trends"]})
    d["edition"] = edition
    d["updated"] = today
    d["changelog"].append({"date": today, "edition": edition, "summary": summary,
                           "added": added, "moved": moved, "removed": removed})
    save(DATA, d)
    print(f"{edition}: {len(added)} új, {len(moved)} mozdult, {len(removed)} lekerült")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("snapshot")
    f = sub.add_parser("finalize")
    f.add_argument("--edition", required=True, help="pl. 2026-11")
    f.add_argument("--summary", required=True)
    f.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()
    return snapshot() if a.cmd == "snapshot" else finalize(a.edition, a.summary, a.date)


if __name__ == "__main__":
    sys.exit(main())
