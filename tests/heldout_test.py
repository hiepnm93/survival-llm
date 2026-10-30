"""Held-out questions: 20 questions with 20 pieces of official guidance, every check compiles and finds its fact in
the guidance the judges get (grader and key agree), and none is one of the 22 questions the safety cards were written
from. No Ollama.

Usage: .venv/bin/python tests/heldout_test.py"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals"))
from heldout import GOLD, HELDOUT  # noqa: E402
from retrieval_eval import QUESTIONS, grade  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
    if not ok:
        FAILS.append(name)


check("20 held-out questions", len(HELDOUT) == 20, len(HELDOUT))
check("20 pieces of guidance", len(GOLD) == 20, len(GOLD))
check("every question has q, must and about", all(set(item) == {"q", "must", "about"} for item in HELDOUT),
      [item.get("q") for item in HELDOUT if set(item) != {"q", "must", "about"}])
check("1-4 checks per question", all(1 <= len(item["must"]) <= 4 for item in HELDOUT),
      [item["q"] for item in HELDOUT if not 1 <= len(item["must"]) <= 4])
bad = []
for item in HELDOUT:
    for p in item["must"] + [item["about"]]:
        try:
            re.compile(p)
        except re.error as exc:
            bad.append((p, str(exc)))
check("every regex compiles", not bad, bad)
if not bad:
    for item, gold in zip(HELDOUT, GOLD):
        g = grade(item, gold, [])
        check(f"guidance has every fact: {item['q'][:50]!r}", g["facts"] == 1, g["missed"])
check("every piece of guidance names the agency",
      all(re.search(r"CDC|Red Cross|Ready\.gov|FEMA|NHS|Mayo Clinic|EPA|NWS|USGS|WHO", g) for g in GOLD),
      [g[:40] for g in GOLD if not re.search(r"CDC|Red Cross|Ready\.gov|FEMA|NHS|Mayo Clinic|EPA|NWS|USGS|WHO", g)])
old = {item["q"].strip().lower() for item in QUESTIONS}
check("no held-out question is an old one", not [i["q"] for i in HELDOUT if i["q"].strip().lower() in old],
      [i["q"] for i in HELDOUT if i["q"].strip().lower() in old])
check("held-out questions are all different", len({i["q"] for i in HELDOUT}) == len(HELDOUT))

print(f"\n{len(FAILS)} failed" if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
