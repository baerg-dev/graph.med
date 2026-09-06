#!/usr/bin/env python3
"""Build the site under site/ from data/ and schema/schema.yaml (docs/publication.md).

    uv run tools/build.py                      # site/ for the domain (base path "/")
    uv run tools/build.py --base /graph.med/   # for baerg-dev.github.io/graph.med/
    uv run tools/build.py --cname graph.med    # also emit the CNAME file for Pages

Every view becomes <view-id>/index.html — a graph (positions computed here) with a
detail section below it — plus <view-id>.json; every entity becomes
<namespace>/<entity-id>/index.html and <namespace>/<entity-id>.json; the schema is
copied to schema/schema.yaml. Offline, deterministic, nothing authored.
"""

from __future__ import annotations

import argparse
import json
import math
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


def graph_of(view: dict, members: dict[str, dict], pool: Pool) -> dict:
    """Nodes (statements, concepts) and links (slot fills, statement edges) with positions."""
    nodes, links = [], []
    for ent in members.values():
        if ent["type"] == "statement":
            contested = any(k == "contests" for k, _, _ in pool.inc.get(ent["id"], []))
            nodes.append({"id": ent["id"], "type": "statement", "label": ent["label"], "lang": ent["lang"], "contested": contested})
            for slot in SLOTS:
                cid = (ent.get("slots") or {}).get(slot)
                if cid in members:
                    links.append({"from": ent["id"], "to": cid, "kind": slot})
            for kind, to, _ in pool.out.get(ent["id"], []):
                if kind in STATEMENT_EDGES and to in members:
                    links.append({"from": ent["id"], "to": to, "kind": kind})
        elif ent["type"] == "concept":
            nodes.append({"id": ent["id"], "type": "concept", "label": ent["label"], "lang": ent["lang"]})
    nodes.sort(key=lambda n: n["id"])
    links.sort(key=lambda l: (l["from"], l["kind"], l["to"]))
    layout(nodes, links)
    return {"nodes": nodes, "links": links}


def layout(nodes: list[dict], links: list[dict], iterations: int = 250, size: float = 1000.0) -> None:
    """Fruchterman–Reingold with a seeded start, so a commit always draws the same picture."""
    n = len(nodes)
    if n == 0:
        return
    seed = 2463534242
    def rnd():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) % 2**31
        return seed / 2**31
    idx = {node["id"]: i for i, node in enumerate(nodes)}
    pos = [[size * rnd(), size * rnd()] for _ in nodes]
    pairs = [(idx[l["from"]], idx[l["to"]]) for l in links if l["from"] in idx and l["to"] in idx]
    k = math.sqrt(size * size / n) * 0.9
    temp = size / 8
    for it in range(iterations):
        disp = [[0.0, 0.0] for _ in nodes]
        for i in range(n):
            xi, yi = pos[i]
            for j in range(i + 1, n):
                dx, dy = xi - pos[j][0], yi - pos[j][1]
                d2 = dx * dx + dy * dy + 1e-6
                if d2 > (4 * k) ** 2:
                    continue
                f = k * k / d2
                disp[i][0] += dx * f; disp[i][1] += dy * f
                disp[j][0] -= dx * f; disp[j][1] -= dy * f
        for i, j in pairs:
            dx, dy = pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]
            d = math.sqrt(dx * dx + dy * dy) + 1e-6
            f = d / k
            disp[i][0] -= dx / d * f * d; disp[i][1] -= dy / d * f * d
            disp[j][0] += dx / d * f * d; disp[j][1] += dy / d * f * d
        for i in range(n):
            dx, dy = size / 2 - pos[i][0], size / 2 - pos[i][1]   # weak gravity keeps components together
            disp[i][0] += dx * 0.05; disp[i][1] += dy * 0.05
            d = math.sqrt(disp[i][0] ** 2 + disp[i][1] ** 2) + 1e-6
            step = min(d, temp)
            pos[i][0] += disp[i][0] / d * step
            pos[i][1] += disp[i][1] / d * step
        temp = max(temp * 0.97, 1.0)
    xs, ys = [p[0] for p in pos], [p[1] for p in pos]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0, 1.0)
    for node, (x, y) in zip(nodes, pos):
        node["x"] = round((x - x0) / span * size, 1)
        node["y"] = round((y - y0) / span * size, 1)


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
        graph = graph_of(view, members, pool)
        for node in graph["nodes"]:
            node["html"] = detail_tpl.render(**details(pool.entities[node["id"]]))
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
