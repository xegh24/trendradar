#!/usr/bin/env python3
"""Check that every source link in the data files still answers.

Sends a HEAD request (falling back to GET) to each URL in parallel and
lists the ones that fail. Some sites block automated requests (403/429);
those are reported as warnings, not errors.

Usage: python3 scripts/check_links.py [--strict]
  --strict  exit 1 when any link is broken (used in CI)
"""
import concurrent.futures as cf
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (compatible; trendradar-linkcheck/1.0)"
SOFT = {401, 403, 405, 406, 429, 451, 999}


def urls() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    t = json.loads((ROOT / "data/trends.json").read_text(encoding="utf-8"))
    for tr in t["trends"]:
        for s in tr["sources"]:
            found.setdefault(s["url"], []).append(tr["id"])
    c = json.loads((ROOT / "data/calendar.json").read_text(encoding="utf-8"))
    for r in c.get("reports", []) + c.get("monitors", []):
        found.setdefault(r["url"], []).append("naptár")
    return found


def probe(url: str) -> tuple[str, int | None, str]:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return url, r.status, ""
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 404, 405, 501):
                continue
            return url, e.code, ""
        except Exception as e:  # noqa: BLE001 - report any network failure
            if method == "HEAD":
                continue
            return url, None, type(e).__name__
    return url, None, "ismeretlen"


def main() -> int:
    strict = "--strict" in sys.argv
    found = urls()
    bad, soft = [], []
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for url, code, why in ex.map(probe, found):
            if code and code < 400:
                continue
            (soft if code in SOFT else bad).append((url, code, why))
    for url, code, why in soft:
        print(f"figyelmeztetés ({code}): {url}  ← {', '.join(found[url])}")
    for url, code, why in bad:
        print(f"HIBÁS ({code or why}): {url}  ← {', '.join(found[url])}")
    print(f"{len(found)} link ellenőrizve: {len(bad)} hibás, {len(soft)} nem ellenőrizhető")
    return 1 if (strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
