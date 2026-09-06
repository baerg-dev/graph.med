#!/usr/bin/env python3
"""Build the site under site/ from data/ and schema/schema.yaml (docs/publication.md).

    uv run tools/build.py                      # site/ for the domain (base path "/")
    uv run tools/build.py --base /graph.med/   # for baerg-dev.github.io/graph.med/
    uv run tools/build.py --cname graph.med    # also emit the CNAME file for Pages

Every view becomes <view-id>/index.html — a decision graph per chapter (population →
condition → recommendation → outcome, layered top-down, positions computed here)
with a detail section below it — plus <view-id>.json; every entity becomes
<namespace>/<entity-id>/index.html and <namespace>/<entity-id>.json; the schema is
copied to schema/schema.yaml. Offline, deterministic, nothing authored.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "schema.yaml"
SITE_SRC = Path(__file__).resolve().parent / "site"

SLOTS = ("population", "action", "condition", "outcome")
EVIDENCE = ("supports", "contests")
STATEMENT_EDGES = ("specializes", "complements", "conflicts")


# ── the pool ────────────────────────────────────────────────────────────────

def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class Pool:
    def __init__(self, schema: dict):
        self.entities: dict[str, dict] = {}
        self.edges: list[tuple[str, str, str, dict]] = []
        for glob in schema["x-layout"]:
            for path in sorted(ROOT.glob(glob)):
                doc = load(path)
                if str(path.relative_to(ROOT)).startswith("data/edges/"):
                    for e in doc or []:
                        self.edges.append((e[0], e[1], e[2], e[3] if len(e) > 3 else {}))
                else:
                    for ent in (doc if isinstance(doc, list) else [doc]):
                        self.entities[ent["id"]] = ent
        self.out: dict[str, list] = defaultdict(list)
        self.inc: dict[str, list] = defaultdict(list)
        for frm, kind, to, props in self.edges:
            self.out[frm].append((kind, to, props))
            self.inc[to].append((kind, frm, props))

    def of_type(self, t: str):
        return [e for e in self.entities.values() if e.get("type") == t]

    def source_of(self, claim: dict) -> str:
        return claim["source"]["at"].split("#", 1)[0]

    def claims_for(self, statement_id: str) -> list[dict]:
        """Claims linked to a statement by supports/contests, with the edge kind."""
        rows = []
        for kind, frm, _ in self.inc.get(statement_id, []):
            if kind in EVIDENCE and frm in self.entities:
                rows.append({"edge": kind, **self.claim_view(self.entities[frm])})
        rows.sort(key=lambda r: (r["edge"] != "supports", natural(r.get("recommendation_no") or ""), r["id"]))
        return rows

    def claim_view(self, claim: dict) -> dict:
        at = claim["source"]["at"]
        src_id, _, frag = at.partition("#")
        page = frag.split("=", 1)[1] if frag.startswith("page=") else None
        src = self.entities.get(src_id, {})
        link = src.get("url", "")
        if link and page:
            link = f"{link}#page={page}"
        row = {k: claim.get(k) for k in ("id", "kind", "recommendation_no", "label", "grade", "verb", "direction", "consensus", "lang")}
        row.update({"quote": claim["source"]["quote"], "page": page, "source": src_id, "link": link})
        for kind, to, _ in self.out.get(claim["id"], []):
            if kind in EVIDENCE:
                row.setdefault("statements", []).append({"edge": kind, "id": to, "label": self.entities.get(to, {}).get("label", to)})
        return row

    def uses_of(self, concept_id: str) -> list[dict]:
        rows = []
        for st in self.of_type("statement"):
            for slot in SLOTS:
                if (st.get("slots") or {}).get(slot) == concept_id:
                    rows.append({"id": st["id"], "label": st["label"], "slot": slot})
        rows.sort(key=lambda r: r["id"])
        return rows


def natural(s: str):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", s)]


# ── views ───────────────────────────────────────────────────────────────────

def members_of(view: dict, pool: Pool) -> dict[str, dict]:
    """Resolve a view's filter to its member entities (docs/publication.md §2, spec §4)."""
    f = view["filter"]
    if view["view_kind"] != "selection" or "sources" not in f:
        raise SystemExit(f"{view['id']}: only selection views over `sources` are built yet")
    members: dict[str, dict] = {}
    for src in f["sources"]:
        members[src] = pool.entities[src]
    for claim in pool.of_type("claim"):
        if pool.source_of(claim) in f["sources"]:
            members[claim["id"]] = claim
            for kind, to, _ in pool.out.get(claim["id"], []):
                if kind in EVIDENCE and to in pool.entities:
                    members[to] = pool.entities[to]
    for ent in list(members.values()):
        if ent.get("type") == "statement":
            for slot in SLOTS:
                cid = (ent.get("slots") or {}).get(slot)
                if cid in pool.entities:
                    members[cid] = pool.entities[cid]
    return members


def chapter_of(statement_id: str, pool: Pool) -> str | None:
    """The chapter a statement belongs to: the recommendation numbers of its claims (e.g. 6.3 → 6).
    A display grouping for one-source views, derived, never stored (docs/publication.md §3)."""
    nos = sorted({c["recommendation_no"].split(".")[0] for c in pool.claims_for(statement_id) if c.get("recommendation_no")}, key=natural)
    return nos[0] if nos else None


GRADES = ("A", "B", "0", "EK")


def wrap(text: str, width: int, lines: int) -> list[str]:
    """Greedy word wrap into at most `lines` lines of about `width` characters; ellipsis if cut."""
    out, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            out.append(cur); cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: max(0, width - 1)].rstrip() + "…"
    return out


def decision_graph_of(view: dict, members: dict[str, dict], pool: Pool) -> dict:
    """One decision graph per chapter, derived from the statements' slots (docs/publication.md §3):
    population (a question: is the patient in it?) → condition (a further question) → the
    statement (the recommended action, coloured by its claims' grade) → outcome (its purpose).
    Layered top-down; positions computed here, deterministically."""
    statements = sorted((m for m in members.values() if m["type"] == "statement"), key=lambda s: s["id"])
    chapters: dict[str, list] = defaultdict(list)
    for st in statements:
        chapters[chapter_of(st["id"], pool) or "?"].append(st)
    label = lambda cid: members[cid]["label"] if cid in members else cid
    out = []
    for ch, sts in sorted(chapters.items(), key=lambda kv: natural(kv[0])):
        sts.sort(key=lambda s: natural(min((c["recommendation_no"] for c in pool.claims_for(s["id"]) if c.get("recommendation_no")), default="")) + [s["id"]])
        nodes: dict[str, dict] = {}
        edges: list[dict] = []
        def add(nid, **kw):
            if nid not in nodes:
                nodes[nid] = {"id": nid, **kw}
            return nid
        for st in sts:
            slots = st.get("slots") or {}
            claims = pool.claims_for(st["id"])
            grades = {c["grade"] for c in claims if c["edge"] == "supports" and c.get("grade")}
            against = {c["direction"] for c in claims if c["edge"] == "supports" and c.get("direction")} == {"against"}
            sid = add(st["id"], ref=st["id"], type="statement", layer=2, lang=st["lang"],
                      lines=wrap(st["label"], 26, 3), grade=grades.pop() if len(grades) == 1 else ("mixed" if grades else None),
                      against=against, contested=any(c["edge"] == "contests" for c in claims),
                      no=min((c["recommendation_no"] for c in claims if c.get("recommendation_no")), default=None))
            pop = slots.get("population"); cond = slots.get("condition"); outc = slots.get("outcome")
            prev = None
            if pop in members:
                prev = add(pop, ref=pop, type="population", layer=0, lang=members[pop]["lang"], lines=wrap(label(pop), 20, 3))
            if cond in members:
                cid = f"{pop}|{cond}" if pop else cond      # a condition is asked within its population
                cid = add(cid, ref=cond, type="condition", layer=1, lang=members[cond]["lang"], lines=wrap(label(cond), 20, 3))
                if prev:
                    edges.append({"from": prev, "to": cid, "kind": "branch"})
                prev = cid
            if prev:
                edges.append({"from": prev, "to": sid, "kind": "branch"})
            if outc in members:
                oid = add(outc, ref=outc, type="outcome", layer=3, lang=members[outc]["lang"], lines=wrap(label(outc), 22, 2))
                edges.append({"from": sid, "to": oid, "kind": "purpose"})
        layered_layout(nodes, edges)
        out.append({"id": f"{view['id']}#chapter={ch}", "chapter": ch, "label": f"Kapitel {ch}", "count": len(sts),
                    "nodes": sorted(nodes.values(), key=lambda n: (n["layer"], n["x"], n["id"])),
                    "edges": sorted({(e["from"], e["kind"], e["to"]) for e in edges})})
    for c in out:
        c["edges"] = [{"from": f, "kind": k, "to": t} for f, k, t in c["edges"]]
    return out


SIZE = {"statement": (170, 62), "population": (150, 56), "condition": (140, 52), "outcome": (150, 40)}
LAYER_Y = (0, 150, 310, 450)


def layered_layout(nodes: dict[str, dict], edges: list[dict]) -> None:
    """Statements in reading order set the x axis; the other layers sit at the barycentre of
    what they connect to, then overlaps are pushed apart. Deterministic."""
    GAP = 22
    for n in nodes.values():
        n["w"], n["h"] = SIZE[n["type"]]
        n["y"] = LAYER_Y[n["layer"]]
    order = [n for n in nodes.values() if n["type"] == "statement"]   # insertion order = reading order
    x = 0.0
    for n in order:
        n["x"] = x + n["w"] / 2; x += n["w"] + GAP
    nbrs: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        nbrs[e["from"]].append(e["to"]); nbrs[e["to"]].append(e["from"])
    for layer in (1, 0, 3):    # conditions from statements, populations from conditions/statements, outcomes from statements
        row = [n for n in nodes.values() if n["layer"] == layer]
        for n in row:
            xs = [nodes[m]["x"] for m in nbrs[n["id"]] if "x" in nodes[m]]
            n["x"] = sum(xs) / len(xs) if xs else 0.0
        row.sort(key=lambda n: (n["x"], n["id"]))
        for i in range(1, len(row)):     # push apart, left to right
            lo = row[i - 1]["x"] + row[i - 1]["w"] / 2 + GAP + row[i]["w"] / 2
            if row[i]["x"] < lo:
                row[i]["x"] = lo
        if row:                          # recentre the row over the neighbours already placed
            targets = [sum(nodes[m]["x"] for m in nbrs[n["id"]] if "x" in nodes[m] and nodes[m] is not n) / max(1, sum(1 for m in nbrs[n["id"]] if "x" in nodes[m] and nodes[m] is not n)) for n in row]
            shift = sum(n["x"] for n in row) / len(row) - sum(targets) / len(targets)
            for n in row:
                n["x"] -= shift
    for n in nodes.values():
        n["x"] = round(n["x"], 1)


# ── rendering ───────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT / "site")
    ap.add_argument("--base", default="/", help="base path every link starts with (default: /)")
    ap.add_argument("--cname", default=None, help="emit a CNAME file with this domain")
    args = ap.parse_args(argv)
    base = args.base if args.base.endswith("/") else args.base + "/"

    schema = load(SCHEMA)
    pool = Pool(schema)
    commit = git_commit()
    env = Environment(loader=FileSystemLoader(SITE_SRC / "templates"), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.globals.update(base=base, commit=commit, built=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                       version=schema.get("x-version"))
    env.filters["short"] = lambda eid: eid.split("/", 1)[-1]

    out = args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / ".nojekyll").write_text("")
    if args.cname:
        (out / "CNAME").write_text(args.cname + "\n")
    (out / "schema").mkdir()
    shutil.copy(SCHEMA, out / "schema" / "schema.yaml")
    shutil.copytree(SITE_SRC / "static", out / "assets")

    def details(ent: dict) -> dict:
        """What the sheet and the entity page show for one entity (docs/publication.md §3)."""
        d = {"entity": ent}
        t = ent["type"]
        if t == "statement":
            d["slots"] = [{"slot": s, "id": cid, "label": pool.entities.get(cid, {}).get("label", cid)}
                          for s in SLOTS if (cid := (ent.get("slots") or {}).get(s))]
            d["claims"] = pool.claims_for(ent["id"])
            d["contested"] = any(c["edge"] == "contests" for c in d["claims"])
            d["related"] = [{"kind": k, "id": to, "label": pool.entities.get(to, {}).get("label", to)}
                            for k, to, _ in pool.out.get(ent["id"], []) if k in STATEMENT_EDGES]
        elif t == "concept":
            d["uses"] = pool.uses_of(ent["id"])
            d["codes"] = [to for k, to, _ in pool.out.get(ent["id"], []) if k == "codes_as"]
        elif t == "claim":
            d["claim"] = pool.claim_view(ent)
        elif t == "source":
            d["claim_count"] = sum(1 for c in pool.of_type("claim") if pool.source_of(c) == ent["id"])
        return d

    def edges_json(eid: str) -> dict:
        return {"out": [{"kind": k, "to": to, **p} for k, to, p in pool.out.get(eid, [])],
                "in": [{"kind": k, "from": frm, **p} for k, frm, p in pool.inc.get(eid, [])]}

    entity_tpl = env.get_template("entity.html")
    detail_tpl = env.get_template("details.html")
    for eid, ent in sorted(pool.entities.items()):
        if ent["type"] == "view":
            continue
        d = details(ent)
        page = out / eid
        page.mkdir(parents=True, exist_ok=True)
        (page / "index.html").write_text(entity_tpl.render(**d), encoding="utf-8")
        (out / (eid + ".json")).write_text(dumps({**ent, "edges": edges_json(eid)}), encoding="utf-8")

    views = []
    view_tpl = env.get_template("view.html")
    for view in sorted(pool.of_type("view"), key=lambda v: v["id"]):
        vid = view["id"].split("/", 1)[1]
        members = members_of(view, pool)
        chapters = decision_graph_of(view, members, pool)
        html = {}
        for c in chapters:
            for node in c["nodes"]:
                html.setdefault(node["ref"], detail_tpl.render(**details(pool.entities[node["ref"]])))
        graph = {"chapters": chapters, "html": html}
        sources = [members[s] for s in view["filter"]["sources"]]
        title = sources[0]["title"] if len(sources) == 1 else vid
        counts = {t: sum(1 for m in members.values() if m["type"] == t) for t in ("statement", "concept", "claim")}
        data = {"id": view["id"], "title": title, "sources": [s["id"] for s in sources], "commit": commit, **graph}
        (out / vid).mkdir(parents=True, exist_ok=True)
        (out / vid / "index.html").write_text(
            view_tpl.render(view=view, vid=vid, title=title, sources=sources, counts=counts,
                            graph_json=dumps(data).replace("</", "<\\/")), encoding="utf-8")   # safe inside <script>
        (out / (vid + ".json")).write_text(dumps(data), encoding="utf-8")
        views.append({"vid": vid, "title": title, "sources": sources, "counts": counts})

    (out / "index.html").write_text(env.get_template("index.html").render(views=views, sources=sorted(pool.of_type("source"), key=lambda s: s["id"])), encoding="utf-8")
    print(f"built {len(views)} view(s) and {len(pool.entities) - len(views)} entity pages into {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} (base {base})")
    return 0


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True, cwd=ROOT).stdout.strip()
    except Exception:  # noqa: BLE001 — a tarball build has no git
        return "unknown"


if __name__ == "__main__":
    sys.exit(main())
