"""football-data.org dan La Liga ma'lumotini olib, site/data.json ga yozadi.

GitHub Actions har bir necha daqiqada shu faylni ishga tushiradi.
Token FOOTBALL_TOKEN nomli maxfiy o'zgaruvchidan olinadi.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ.get("0182d023fa5f4f988eb943c2f3ae5c7d", "")
BASE = "https://api.football-data.org/v4/competitions/PD"   # PD = La Liga


def api_get(path):
    req = urllib.request.Request(BASE + path, headers={"X-Auth-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def load_values():
    """Transfer narxlari: values.json (qo'lda to'ldiriladi)."""
    try:
        with open("values.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    if not TOKEN:
        sys.exit("XATO: FOOTBALL_TOKEN topilmadi. GitHub Secrets ga qo'shing.")

    try:
        standings = api_get("/standings")
        scorers = api_get("/scorers?limit=20")
    except urllib.error.HTTPError as e:
        sys.exit(f"XATO: API {e.code} javob qaytardi. Token yoki so'rovlar chegarasini tekshiring.")
    except Exception as e:
        sys.exit(f"XATO: API ga ulanib bo'lmadi: {e}")

    values = load_values()
    total = next((s for s in standings["standings"] if s.get("type") == "TOTAL"),
                 standings["standings"][0])

    table = [{
        "pos": r["position"],
        "team": r["team"]["name"],
        "crest": r["team"].get("crest", ""),
        "played": r["playedGames"],
        "won": r["won"],
        "draw": r["draw"],
        "lost": r["lost"],
        "gf": r["goalsFor"],
        "ga": r["goalsAgainst"],
        "gd": r["goalDifference"],
        "points": r["points"],
    } for r in total["table"]]

    top = []
    for s in scorers["scorers"]:
        name = s["player"]["name"]
        top.append({
            "name": name,
            "nationality": s["player"].get("nationality") or "—",
            "team": s["team"]["name"],
            "goals": s.get("goals") or 0,
            "assists": s.get("assists") or 0,
            "value": values.get(name, "—"),
        })

    data = {
        "table": table,
        "scorers": top,
        "matchday": standings.get("season", {}).get("currentMatchday"),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"OK: {len(table)} jamoa, {len(top)} to'purar yozildi.")


if __name__ == "__main__":
    main()
