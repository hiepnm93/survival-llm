"""Read-only search over the offline library built by build_library.py (stdlib only)."""
import json
import math
import os
import re
import sqlite3
import urllib.request

def _find_library():
    """$SURVIVAL_LLM_LIBRARY, else ~/Survival LLM Library, else the library.noindex next to this code."""
    if os.environ.get("SURVIVAL_LLM_LIBRARY"):  # an explicit choice wins, even before anything is installed
        return os.environ["SURVIVAL_LLM_LIBRARY"]
    dev = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "library.noindex"))
    home = os.path.join(os.path.expanduser("~"), "Survival LLM Library")
    for path in (home, dev):
        if os.path.exists(os.path.join(path, "index.sqlite")):
            return path
    return home


LIB = _find_library()
DB_PATH = os.path.join(LIB, "index.sqlite")
TEXT_DIR = os.path.join(LIB, "text")
TOPICS = ("medical", "emergency", "howto", "repair", "encyclopedia")

# Ranking boost for sources with editorial review over wikiHow and Q&A sites, most for government and WHO/IFRC
# guidance, so for equally good matches Ready.gov, CDC, MedlinePlus or the NHS come before Wikipedia, wikiHow and Q&A.
OFFICIAL = ("ready-gov", "cdc-travel", "medlineplus", "nhs-medicines", "military-medicine", "wikem",
            "medical-library", "water", "post-disaster", "food-prep", "survival-manuals", "first-aid-guides",
            "usda-canning", "risk")
AGENCIES = ("ready-gov", "cdc-travel", "medlineplus", "nhs-medicines", "military-medicine", "survival-manuals",
            "first-aid-guides", "usda-canning")
AUTHORITY = {**{k: 1.4 for k in OFFICIAL}, **{k: 1.8 for k in AGENCIES}, "wikipedia": 1.15, "wikimed": 1.15,
             "wikihow": 0.9}
QA_WEIGHT = 0.85  # Stack Exchange sites (keys "se-...")
TITLE_WEIGHT = 1.5  # how much a title sharing all the query's words raises a result
# Words people use for a hazard, and the terms articles about it use: "a power line is down in my yard" also looks for
# "power lines" and electrocution, so a flood toolkit that mentions yards doesn't win.
EXPANSIONS = [(re.compile(p, f), terms) for p, f, terms in [
    (r"\b(?:power|electric(?:al)?|utility|overhead)[ -]?(?:lines?|wires?|cables?|poles?)\b|\blive wires?\b"
     r"|\blines? (?:is |are )?down\b", re.I, ["power line", "power lines", "electrocution"]),
    (r"electrocut|electric(?:al)? shock|\bshocked\b", re.I, ["electric shock", "electrical injuries"]),
    (r"\bCO\b", 0, ["carbon monoxide"]),
    (r"\bgenerators?\b|\bco (?:alarm|detector|poisoning)", re.I, ["carbon monoxide"]),
    (r"gas leak|smell(?:s|ing)? (?:of |like )?gas|rotten eggs?", re.I, ["gas leak", "natural gas"]),
    (r"\bflood", re.I, ["floodwater", "flood water"]),
    (r"\bbleach\b|disinfect\w* water|purif\w* water|contaminated water", re.I, ["water disinfection", "purification"]),
    (r"heat ?stroke|stopped sweating", re.I, ["heat stroke", "heatstroke"]),
    (r"\bshiver\w*|\bfreezing\b|frostbite", re.I, ["hypothermia"]),
    (r"\bchok(?:e|es|ed|ing)\b", re.I, ["choking", "heimlich"]),
    (r"drown\w*|in(?:to)? the (?:water|river|lake|pool)\b", re.I, ["drowning", "water rescue"]),
    (r"\bbleed\w*|\bdeep cut\b", re.I, ["bleeding", "tourniquet"]),
    (r"nuclear|fallout|radiation|dirty bomb", re.I, ["radiation", "fallout"]),
    (r"chain ?saws?", re.I, ["chainsaw", "chain saw"]),
]]
EMBED_TOP = 30  # how many of the best candidates an embedding model reranks (SURVIVAL_LLM_EMBED)
OLLAMA = "http://" + os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
# Sources published by a government health/emergency agency, the IFRC or WHO: shown with an "Official" label.
# (Not the UK medicines guide: the NHS terms say an unrefreshed copy must not be presented as the NHS's.)
OFFICIAL_LABEL = {"ready-gov", "cdc-travel", "medlineplus", "military-medicine", "survival-manuals",
                  "first-aid-guides", "usda-canning"}

STOPWORDS = set("""a about above after again against all am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have having he her here
hers herself him himself his how i if in into is it its itself just me more most my myself no nor not now of off on
once only or other our ours ourselves out over own same she should so some such than that the their theirs them
themselves then there these they this those through to too under until up very was we were what when where which
while who whom why will with would you your yours yourself yourselves""".split())


class Library:
    def __init__(self, path=DB_PATH):
        # check_same_thread=False only so a library swap can close it from another thread (see app/server.py)
        self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
        try:
            self.db.execute("SELECT 1 FROM sources LIMIT 1")
        except sqlite3.OperationalError:  # e.g. a WAL-mode file on a read-only disk
            self.db = sqlite3.connect(f"file:{path}?immutable=1", uri=True, check_same_thread=False)

    def stats(self):
        """(articles, sources) that are fully indexed."""
        sources, docs = self.db.execute(
            "SELECT COUNT(*), COALESCE(SUM(docs), 0) FROM sources WHERE done=1").fetchone()
        return docs, sources

    def labels(self):
        """Names of the indexed sources, largest first, for telling the model what it can search."""
        return [r[0] for r in self.db.execute("SELECT label FROM sources WHERE done=1 ORDER BY docs DESC")]

    def _read(self, file_id, offset, length):
        return self._read_bytes(file_id, offset, length).decode("utf-8", "replace")

    def search(self, query, topic=None, limit=8, scores=False):
        """Best passages for a keyword query, at most one per article. scores=True adds each result's ranking
        score (lower is better) and how many of the query's words its passage contains, for merging result lists."""
        words = query_words(query)
        if not words:
            return []
        extra = [t for t in expand(query) if t not in words]
        terms = ['"' + w.replace('"', "") + '"' for w in words]
        more = ['"' + t.replace('"', "") + '"' for t in extra]
        hits = []
        # All words (or a term the hazard is known by) first; any of them if that finds too little.
        for match in ([f"({' '.join(terms)}) OR " + " OR ".join(more) if more else " ".join(terms)],
                      [" OR ".join(terms + more)]):
            hits = self.db.execute(
                "SELECT rowid, rank FROM fts WHERE fts MATCH ? AND rank MATCH 'bm25(4.0, 1.0)' "
                "ORDER BY rank LIMIT 600", match).fetchall()
            if len(hits) >= 3 or len(words) + len(extra) == 1:
                break
        if not hits:
            return []
        rank = dict(hits)
        marks = ",".join("?" * len(rank))
        info = {r[0]: r for r in self.db.execute(
            "SELECT p.id, d.id, d.title, s.label, s.topic, d.file_id, p.offset, p.length, s.key, d.offset, d.length "
            f"FROM passages p JOIN docs d ON d.id = p.doc_id JOIN sources s ON s.id = d.source_id "
            f"WHERE p.id IN ({marks})", list(rank))}
        score = {pid: relevance(rank[pid], r[2], r[8], words, extra) for pid, r in info.items()}
        order = sorted((pid for pid in info if not topic or topic == "any" or info[pid][4] == topic), key=score.get)
        order = self._embed_rerank(query, order, info)
        results, seen_docs, shown = [], set(), set()
        for pid in order:
            r = info[pid]
            if r[1] in seen_docs:
                continue
            seen_docs.add(r[1])
            body = self._read_bytes(r[5], r[9], r[10]).split(b"\n\n", 1)[-1]  # the article without its title header
            if body in shown:  # the same article under another title (iFixit's guides for each model variant)
                continue
            shown.add(body)
            text = self._read(r[5], r[6], r[7])
            results.append({"id": pid, "title": r[2], "source": r[3], "official": r[8] in OFFICIAL_LABEL,
                            "snippet": _snippet(text, words + extra)})
            if scores:
                low = f"{r[2]} {text}".lower()
                results[-1].update(score=score[pid], matched=sum(w[:5] in low for w in words))
            if len(results) >= limit:
                break
        return results

    def _embed_rerank(self, query, order, info):
        """With $SURVIVAL_LLM_EMBED naming an Ollama embedding model, the best EMBED_TOP articles reordered by keyword
        rank and closeness in meaning together; otherwise, or if the model can't be reached, order unchanged."""
        model = os.environ.get("SURVIVAL_LLM_EMBED")
        if not model:
            return order
        top, docs = [], set()
        for pid in order:
            if info[pid][1] not in docs:
                docs.add(info[pid][1])
                top.append(pid)
                if len(top) == EMBED_TOP:
                    break
        try:
            texts = [f"{info[p][2]}\n{self._read(info[p][5], info[p][6], info[p][7])[:1000]}" for p in top]
            vectors = embed(model, [query] + texts)
            near = {p: _cosine(vectors[0], v) for p, v in zip(top, vectors[1:])}
        except (OSError, ValueError, KeyError, TypeError, IndexError):
            return order
        if len(near) < len(top):
            return order
        by_meaning = {p: i for i, p in enumerate(sorted(top, key=lambda p: -near[p]))}
        rerank = sorted(top, key=lambda p: top.index(p) + by_meaning[p])
        chosen = set(rerank)
        return rerank + [p for p in order if p not in chosen]

    def read(self, passage_id, max_chars=5000):
        """Article text starting at a passage, about max_chars long."""
        row = self.db.execute(
            "SELECT p.doc_id, d.title, s.label, d.url, d.file_id, s.key FROM passages p JOIN docs d ON d.id = p.doc_id "
            "JOIN sources s ON s.id = d.source_id WHERE p.id=?", (passage_id,)).fetchone()
        if not row:
            return None
        doc_id, title, label, url, file_id, key = row
        parts, size, next_id = [], 0, None
        for pid, offset, length in self.db.execute(
                "SELECT id, offset, length FROM passages WHERE doc_id=? AND id>=? ORDER BY id", (doc_id, passage_id)):
            if parts and size + length > max_chars:
                next_id = pid
                break
            parts.append(self._read(file_id, offset, length))
            size += length
        return {"title": title, "source": label, "url": url, "official": key in OFFICIAL_LABEL,
                "text": "\n\n".join(parts), "next_id": next_id}


    def document(self, passage_id):
        """The whole article holding a passage, split into passages so a viewer can mark the cited one."""
        row = self.db.execute(
            "SELECT d.id, d.title, s.label, d.url, d.file_id, d.offset, d.length, s.key FROM passages p "
            "JOIN docs d ON d.id = p.doc_id JOIN sources s ON s.id = d.source_id WHERE p.id=?",
            (passage_id,)).fetchone()
        if not row:
            return None
        doc_id, title, label, url, file_id, start, length, key = row
        raw = self._read_bytes(file_id, start, length)
        parts = [{"id": pid, "text": raw[off - start:off - start + n].decode("utf-8", "replace")}
                 for pid, off, n in self.db.execute(
                     "SELECT id, offset, length FROM passages WHERE doc_id=? ORDER BY id", (doc_id,))]
        return {"doc_id": doc_id, "title": title, "source": label, "url": url, "official": key in OFFICIAL_LABEL,
                "license": self.license(key), "focus": passage_id, "parts": parts}

    def license(self, key):
        """The source's license line, from libraries built since licenses were kept ('' before that)."""
        try:
            row = self.db.execute("SELECT license FROM sources WHERE key=?", (key,)).fetchone()
        except sqlite3.OperationalError:  # no license column yet
            return ""
        return (row and row[0]) or ""

    def _read_bytes(self, file_id, offset, length):
        (path,) = self.db.execute("SELECT path FROM files WHERE id=?", (file_id,)).fetchone()
        with open(os.path.join(TEXT_DIR, path), "rb") as f:
            f.seek(offset)
            return f.read(length)


def query_words(query):
    """The words of a query worth searching for."""
    return [w for w in re.findall(r"[\w']+", query.lower()) if w not in STOPWORDS and len(w) > 1][:12]


def expand(query):
    """Other terms for the hazards a query names (EXPANSIONS), each once, in order."""
    found = [t for pattern, terms in EXPANSIONS if pattern.search(query or "") for t in terms]
    return list(dict.fromkeys(found))[:6]


def authority(key):
    """How much a source's rank is raised: agencies most, reviewed references next, Q&A sites lowered."""
    return AUTHORITY.get(key, QA_WEIGHT if (key or "").startswith("se-") else 1.0)


def title_overlap(title, words, extra=()):
    """Share of the query's words (by their first five letters) in a title, where the hazard's other terms count too."""
    tokens = re.findall(r"[\w']+", (title or "").lower())
    wanted = set(words) | {w for t in extra for w in t.split()}
    hits = sum(any(tok.startswith(w[:5]) for tok in tokens) for w in wanted)
    return min(1.0, hits / max(1, len(set(words))))


def relevance(rank, title, key, words, extra=()):
    """A result's score, lower is better: its BM25 rank (negative) raised for official sources and for a title that
    shares the query's words, so an article that merely mentions them drops below one about them."""
    return rank * authority(key) * (1 + TITLE_WEIGHT * title_overlap(title, words, extra))


def embed(model, texts):
    """Ollama's embedding vectors for texts."""
    req = urllib.request.Request(OLLAMA + "/api/embed", data=json.dumps({"model": model, "input": texts}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["embeddings"]


def _cosine(a, b):
    return sum(x * y for x, y in zip(a, b)) / ((math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1)


def _snippet(text, words, width=360):
    flat = " ".join(line.lstrip("#").strip() for line in text.splitlines() if line.strip())
    low = flat.lower()
    hits = [low.find(w) for w in words if low.find(w) >= 0]
    start = max(0, min(hits) - 80) if hits else 0
    out = flat[start:start + width]
    return ("..." if start else "") + out + ("..." if start + width < len(flat) else "")
