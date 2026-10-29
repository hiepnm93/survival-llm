"""Safety for hazard questions: official safety cards are matched and put in front of the model, the rules no longer
tell it to make something up, the search reranks off-topic titles down, and a short check replaces an answer that
sends the person into the danger. No Ollama, no library: a fake model (core._stream) and a fake library.

Usage: .venv/bin/python tests/safety_test.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
from library import safety_cards, search  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
    if not ok:
        FAILS.append(name)


def titles(q):
    return [c["title"] for c in safety_cards.match(q)]


# Cards match the hazard a question names, and nothing else
POWER = "A power line is down in my front yard. What should I do?"
for q, want in [(POWER, "Downed power lines"),
                ("Can I run my gas generator in the garage if I leave the big door open?",
                 "Generators, engines and carbon monoxide"),
                ("The tap water might be contaminated. How many drops of household bleach per gallon make it safe?",
                 "Disinfecting drinking water with bleach")]:
    check(f"card for {q!r}", want in titles(q), titles(q))
    check(f"a hazard: {q!r}", safety_cards.is_hazard(q))
RICE = "How do I cook rice without power?"
check("no card for an everyday question", titles(RICE) == [], titles(RICE))
check("not a hazard: an everyday question", not safety_cards.is_hazard(RICE))
check("every card has a title, a source and guidance",
      all(c["title"] and c["source"] and c["text"] for c in safety_cards.CARDS),
      [c["key"] for c in safety_cards.CARDS if not (c["title"] and c["source"] and c["text"])])


# The rules: no more "make something up"; hazards without a source get only cautious steps
class Lib:
    has_personal = False

    def labels(self):
        return ["Ready.gov", "CDC"]

    def search(self, query, topic="any", limit=8):
        return []

    def read(self, pid, max_chars=5000):
        return None


for name, prompt in [("with tools", core.system_prompt(Lib())), ("without tools", core.system_prompt(Lib(), tools=False)),
                     ("no library", core.system_prompt(None))]:
    check(f"rules {name}: no 'make something up'", "make something up" not in prompt.lower())
    check(f"rules {name}: no hands-on rescue without a source", "Never give hands-on rescue" in prompt)
    check(f"rules {name}: still a best guess for estimates", "Always answer" in prompt)

# Search: the hazard's other terms are added, and a title about the question beats one that only mentions its words
words, extra = search.query_words(POWER), search.expand(POWER)
check("expansion: a power line is down -> 'power line'", "power line" in extra, extra)
check("expansion: nothing for rice", search.expand(RICE) == [], search.expand(RICE))
hits = [(-7.0, "Flood Safety Social Media Toolkit", "ready-gov"), (-5.0, "Downed Power Lines", "ready-gov")]
order = sorted(hits, key=lambda h: search.relevance(h[0], h[1], h[2], words, extra))
check("rerank: the off-topic title drops below the one about power lines",
      [h[1] for h in order] == ["Downed Power Lines", "Flood Safety Social Media Toolkit"], order)
check("authority: agencies above Wikipedia above wikiHow and Q&A sites",
      search.authority("ready-gov") > search.authority("wikipedia") > 1.0 > search.authority("wikihow")
      and search.authority("se-outdoors") < 1.0)

# The self-check: an answer that contradicts the card is replaced by the correction
UNSAFE = "1. Push the victim off the line with a dry wooden broom handle.\n2. Call 911."
FIX = "Stay at least 35 feet away and call 911."
asked, check_reply = [], [FIX]  # what each call got; what the check replies


def fake_stream(model, messages, tools, think, options):
    last = messages[-1]["content"]
    asked.append({"tools": bool(tools), "last": last, "predict": options.get("num_predict")})
    if "reply with only: OK" in last:
        yield {"message": {"content": check_reply[0]}}
    else:
        yield {"message": {"content": UNSAFE}}
    yield {"done": True, "eval_count": 2, "eval_duration": 1}


core._stream = fake_stream


def ask(q):
    asked.clear()
    messages = [{"role": "system", "content": "sys"}, {"role": "user", "content": q}]
    evs = list(core.chat_events("nemotron", Lib(), messages, caps={"tools"}))
    return evs, messages, next(e for e in evs if e["type"] == "done")


evs, messages, done = ask(POWER)
cards = [e for e in evs if e["type"] == "card"]
check("card event for the power line",
      {"type": "card", "title": "Downed power lines", "source": "Ready.gov"} in cards, cards)
check("the card is in front of the model on the first round", "Downed power lines (Ready.gov)" in asked[0]["last"]
      and core.CARDS_NOTE in asked[0]["last"], asked[0]["last"][-300:])
check("one short check after the answer, without tools",
      len(asked) == 2 and not asked[1]["tools"] and asked[1]["predict"] == 800 and "broom" in asked[1]["last"], asked)
check("safety_fix event with the correction", any(e["type"] == "safety_fix" and e["answer"] == FIX for e in evs),
      [e["type"] for e in evs])
check("the answer is the correction", done["answer"].startswith(FIX) and "broom" not in done["answer"], done["answer"])
check("the card counts as a source", "Downed power lines (Ready.gov)" in done["answer"]
      and done["cards"] == [{"title": "Downed power lines", "source": "Ready.gov"}], done["answer"])
check("the saved chat keeps the correction", messages[-1] == {"role": "assistant", "content": FIX}, messages[-1])

check_reply[0] = "OK"
evs, messages, done = ask(POWER)
check("check says OK: the answer stands", done["answer"].startswith(UNSAFE)
      and not any(e["type"] == "safety_fix" for e in evs), done["answer"])
check_reply[0] = "**Corrected answer:** " + FIX
evs, messages, done = ask(POWER)
check("a 'Corrected answer:' label is dropped", done["answer"].startswith(FIX), done["answer"])

evs, messages, done = ask(RICE)
check("no card, no check for an everyday question",
      len(asked) == 1 and not any(e["type"] in ("card", "safety_fix") for e in evs), [e["type"] for e in evs])

# The memory step reads what the person said, not the cards added to it
check("cards are kept out of what the person said", core.ADDED.split(asked[0]["last"] if asked else "", 1)[0] == RICE)
evs, messages, done = ask(POWER)
check("the question with its cards splits back to what they asked", core.ADDED.split(messages[1]["content"], 1)[0] == POWER,
      messages[1]["content"][:200])

print(f"\n{len(FAILS)} failed" if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
