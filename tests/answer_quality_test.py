"""Answer quality after the held-out blind judging: facts listed before the answer and numbers checked against what it
read, a fixed shape for safety answers, articles read even when a safety card matches, the self-check on every answer,
and more reasoning for hazard questions. No Ollama: a fake model (core._stream) and a fake library.

Usage: .venv/bin/python tests/answer_quality_test.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
    if not ok:
        FAILS.append(name)


# ---- e. more reasoning for hazard questions ----
for reasoning, hazard, want in [("off", False, 1000), ("off", True, 2000), ("short", True, 2000), ("medium", False, 4000),
                                ("medium", True, 8000), ("long", True, 32000), ("none", False, -1), ("none", True, -1)]:
    check(f"think_budget({reasoning}, hazard={hazard}) == {want}", core.think_budget(reasoning, hazard) == want,
          core.think_budget(reasoning, hazard))

# ---- c. articles read even when a card matches ----
CARD = [{"title": "Downed power lines", "source": "Ready.gov", "text": "Stay at least 35 feet away."}]
for cards, articles, nudges, want in [(CARD, 0, 0, True), (CARD, 1, 1, True), (CARD, 2, 0, False), (CARD, 0, 2, False),
                                      ([], 0, 0, False)]:
    check(f"needs_more_reading(cards={len(cards)}, read={articles}, asked={nudges}) == {want}",
          core.needs_more_reading(cards, articles, nudges) == want)

# ---- b. the safety answer template ----
GOOD = ("**Do this now:**\n1. Stay at least 35 feet away.\n2. Call 911 and the power company.\n\n"
        "**Do NOT:**\n- Touch the line or anything touching it.\n\n"
        "**Get help if:**\n- Someone is touching the line: call 911.\n\nSources: Downed power lines (Ready.gov)")
check("template followed: no gaps", core.template_gaps(GOOD) == [], core.template_gaps(GOOD))
check("plain headings count too", core.template_gaps("Do this now:\n1. x\nDo not:\n- y\nGet help if: z\nSources: w") == [])
no_dont = GOOD.replace("**Do NOT:**\n- Touch the line or anything touching it.\n\n", "")
check("a missing heading is named", core.template_gaps(no_dont) == ["Do NOT"], core.template_gaps(no_dont))
swapped = "**Get help if:**\n- x\n\n**Do this now:**\n1. y\n\n**Do NOT:**\n- z\n\nSources: w"
check("out of order counts as missing", core.template_gaps(swapped) == ["Get help if"], core.template_gaps(swapped))
check("a 'Do not touch' step isn't the Do NOT heading",
      core.template_gaps("Do this now:\n1. Do not touch it.\nSources: x") == ["Do NOT", "Get help if"])

# ---- a. extract, then answer ----
facts, answer = core.split_facts("Facts:\n- Store 1 gallon per person per day (Water storage, Ready.gov)\n"
                                 "- Keep a 3-day supply (Water storage, Ready.gov)\nAnswer:\nStore 1 gallon a day.")
check("split_facts: the list, item by item", facts == ["Store 1 gallon per person per day (Water storage, Ready.gov)",
                                                       "Keep a 3-day supply (Water storage, Ready.gov)"], facts)
check("split_facts: the answer after 'Answer:'", answer == "Store 1 gallon a day.", answer)
facts, answer = core.split_facts("**Facts:**\n- A (x)\n**Answer:** Boil it.")
check("split_facts: bold headings", facts == ["A (x)"] and answer == "Boil it.", (facts, answer))
facts, answer = core.split_facts("Facts:\n- A (x)\n- B (y)\n\nBoil it for 1 minute.")
check("split_facts: no 'Answer:' heading, the list ends at its first non-item",
      facts == ["A (x)", "B (y)"] and answer == "Boil it for 1 minute.", (facts, answer))
check("split_facts: no list, the text as it was", core.split_facts("Boil it.\n\nFacts: none") == ([], "Boil it.\n\nFacts: none"))
for text, want in [("Fac", True), ("**Facts:**\n- x", True), ("Facts:\n- x\nAnswer: y", False), ("First, go", False),
                   ("Fill the tub.", False), ("Boil it.", False)]:
    check(f"_facts_open({text!r}) == {want}", core._facts_open(text) == want)

ORS = ["Mix 6 level teaspoons of sugar and 1/2 teaspoon of salt in 1 liter of clean water."]
got = core.answer_numbers("1. Mix 8 teaspoons of sugar and 1/2 teaspoon of salt in 1 liter of water.\n"
                          "2. Call 911 if they can't drink.\n\nSources: Oral rehydration (WHO) 2019",
                          core.allowed_numbers([], ORS))
check("a wrong ORS number is caught; list numbers, 911 and the Sources block aren't", got == ["8 teaspoons"], got)
got = core.answer_numbers("Up to 4 hours.", core.allowed_numbers([], ["Breast milk keeps four hours at room temperature."]))
check("a number written out in the source counts", got == [], got)
SOURCE = ["Store 1 gallon of water per person per day for at least 3 days."]
LISTED = ["Store 1 gallon per person per day (Water storage, Ready.gov)"]
got = core.answer_numbers("Store 1 gallon a day for 3 days.", core.allowed_numbers(LISTED, SOURCE))
check("with a Facts list, only numbers in it (and in the source) are allowed", got == ["3 days"], got)
got = core.answer_numbers("Store 1 gallon a day for 3 days.", core.allowed_numbers([], SOURCE))
check("without a Facts list, numbers in the source are allowed", got == [], got)
got = core.answer_numbers("Store 1 gallon a day.", core.allowed_numbers(["Store 2 gallons a day (made up)"], SOURCE))
check("a number in the Facts list but not in the source isn't allowed", got == ["1 gallon"], got)
got = core.answer_numbers("At 3 months, give 70% alcohol gel; ids 1403312.", core.allowed_numbers([], ["60% alcohol"],
                                                                                                    "My baby is 3 months old"))
check("question numbers allowed, a wrong percentage caught, passage ids skipped", got == ["70%"], got)
check("a note goes above the Sources line", core._with_note("Body.\n\nSources: X (Y)", "(note)")
      == "Body.\n\n(note)\n\nSources: X (Y)")
check("and at the end with none", core._with_note("Body.", "(note)") == "Body.\n\n(note)")
check("the note doesn't say Sources (that word marks the citation line)", "source" not in core.UNVERIFIED_NOTE.lower())
check("the tool rules ask for the Facts list", core.FACTS_RULE.strip() in core.system_prompt(type(
    "L", (), {"labels": lambda self: ["CDC"], "has_personal": False})()))


# ---- the whole turn, with a fake model and library ----
class Lib:
    has_personal = False

    def labels(self):
        return ["Ready.gov"]

    def search(self, query, topic="any", limit=8):
        return [{"id": 1403312 + i, "title": t, "source": "Ready.gov", "official": True,
                 "snippet": "Store 1 gallon of water per person per day."}
                for i, t in enumerate(["Water storage", "Power outage safety"])]

    def read(self, pid, max_chars=5000):
        title = {1403312: "Water storage", 1403313: "Power outage safety"}.get(pid)
        return title and {"title": title, "source": "Ready.gov", "official": True, "url": "",
                          "text": "Store at least 1 gallon of water per person per day.", "next_id": None}


rounds, calls = [], []


def fake_stream(model, messages, tools, think, options):
    last = messages[-1]["content"]
    calls.append({"tools": bool(tools), "last": last, "predict": options.get("num_predict")})
    if "reply with only: OK" in last:
        yield {"message": {"content": "OK"}}
    else:
        yield from rounds.pop(0)
    yield {"done": True, "eval_count": 1, "eval_duration": 1}


core._stream = fake_stream


def say(*pieces):
    return [{"message": {"content": p}} for p in pieces]


def call(name, args):
    return [{"message": {"content": "", "tool_calls": [{"function": {"name": name, "arguments": args}}]}}]


def ask(q, script):
    rounds[:], calls[:] = script, []
    messages = [{"role": "system", "content": "s"}, {"role": "user", "content": q}]
    evs = list(core.chat_events("nemotron", Lib(), messages, caps={"tools"}))
    return evs, messages, next(e for e in evs if e["type"] == "done")


# A card matches: it answers before reading, is asked to read until it has read two articles, then answers in the template
POWER = "A power line is down in my front yard. What should I do?"
evs, messages, done = ask(POWER, [say("Stay away."), call("search_library", {"query": "power line"}),
                                  call("read_article", {"id": 1403312}), say("Stay away."),
                                  call("read_article", {"id": 1403313}), say(GOOD)])
kinds = [e["type"] for e in evs if e["type"] in ("retry", "search", "read")]
check("card: asked to read until two articles are read", kinds == ["retry", "search", "read", "retry", "read"], kinds)
check("card: the retries say why", all(e["why"] == "read" for e in evs if e["type"] == "retry"))
check("card: the app's note asks for the reading", calls[1]["last"] == core.READ_NUDGE.format(n=2)
      and calls[1]["tools"], calls[1])
check("card: its notes stay out of the saved chat", core.READ_NUDGE[:40] not in str(messages)
      and "Stay away." not in str(messages))
check("hazard: the template is in front of the model", core.TEMPLATE_NOTE in calls[0]["last"], calls[0]["last"][-200:])
check("hazard: twice the reasoning", calls[0]["predict"] == 8192 + 2 * core.REASONING_LIMITS["short"], calls[0])
check("hazard: the answer follows the template", done["template"] == [], done["template"])
check("hazard: the self-check ran", "reply with only: OK" in calls[-1]["last"] and not calls[-1]["tools"])
check("hazard: 35 feet is in the card, so no number is flagged", done["unverified"] == [] and "uncertain" not in
      done["answer"], done["answer"])
check("hazard: the question with its notes splits back to what they asked", core.ADDED.split(messages[1]["content"], 1)[0]
      == POWER)
evs, _, done = ask(POWER, [say("Stay away."), say("Stay away."), say("Stay away from it.")])
check("card: asked twice at most, then its answer stands", [e["type"] for e in evs].count("retry") == 2
      and done["answer"].startswith("Stay away from it."), done["answer"])
check("card: an answer without the template has gaps", done["template"] == ["Do this now", "Do NOT", "Get help if"],
      done["template"])

# No card: the Facts list is held back from the screen, numbers not in what it read are flagged, the check still runs
core.match_cards, core.is_hazard = (lambda q: []), (lambda q: False)
WATER = "How much drinking water should we store?"
evs, messages, done = ask(WATER, [call("search_library", {"query": "water storage"}),
                                  call("read_article", {"id": 1403312}),
                                  say("Fac", "ts:\n- Store 1 gallon per person per day (Water storage, Ready.gov)\n",
                                      "Answer:\nStore 1 gallon", " per person a day, for 3 days.")])
shown = "".join(e["text"] for e in evs if e["type"] == "token")
check("facts: the list isn't streamed to the screen", shown == "Store 1 gallon per person a day, for 3 days.", shown)
check("facts: the done event keeps the list", done["facts"] == ["Store 1 gallon per person per day (Water storage, "
                                                                "Ready.gov)"], done["facts"])
check("facts: the saved chat keeps only the answer",
      messages[-1] == {"role": "assistant", "content": "Store 1 gallon per person a day, for 3 days."}, messages[-1])
check("numbers: 3 days isn't in what it read, so it is flagged above the Sources line",
      done["answer"] == "Store 1 gallon per person a day, for 3 days.\n\n" + core.UNVERIFIED_NOTE.format("3 days")
      + "\n\nSources: Water storage (Ready.gov)" and done["unverified"] == ["3 days"], done["answer"])
check("not a hazard: no template, normal reasoning", done["template"] is None
      and calls[0]["predict"] == 8192 + core.REASONING_LIMITS["short"] and core.TEMPLATE_NOTE not in calls[0]["last"])
check("d. the self-check runs on an everyday answer too", "reply with only: OK" in calls[-1]["last"]
      and core.NO_CARD in calls[-1]["last"], calls[-1]["last"][:300])
evs, _, done = ask(WATER, [say("Store 1 gallon a day, from what I know.")])
check("numbers: nothing read, nothing flagged (its Sources line says so)", done["unverified"] == []
      and done["answer"].endswith("Sources: none (from its own knowledge)"), done["answer"])
evs, _, done = ask(WATER, [say("Facts:\n- 1 gallon (x)\n\nStore 1 gallon a day.")])
check("facts with no 'Answer:' heading: shown whole while streaming, cut from the answer",
      done["answer"].startswith("Store 1 gallon a day.") and "Facts" not in done["answer"], done["answer"])
core.CHECK_EVERY_ANSWER = False
evs, _, done = ask(WATER, [say("Boil it.")])
check("with CHECK_EVERY_ANSWER off, no check for an everyday question", len(calls) == 1, calls)

print(f"\n{len(FAILS)} failed" if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
