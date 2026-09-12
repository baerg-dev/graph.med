#!/usr/bin/env python3
"""Validate the pool under data/ against schema/schema.yaml.

The schema is a JSON Schema (draft 2020-12) and the single point of truth. This
script only (1) validates each data file against the definition the schema's
`x-layout` assigns to it, using the jsonschema library, and (2) checks the few
rules a document schema cannot state because they span files:

  - every id is unique, and in one-per-file namespaces equals <ns>/<file stem>;
  - every entity reference in the data resolves (terminology codes excepted);
  - a claim's id is claims/<source-id>/<first 8 hex of sha256("<at>|<quote>")>;
  - edges are unique per (from, kind, to, discriminator);
  - a view id is not a namespace name (views are served at the site root);
  - a claim's `section` names an entry of its source's `outline` (spec §6.7);
  - `broader` edges form no cycle (spec §5);
  - WORK.yaml, the registry of work packages, is well-formed: ids unique,
    `depends` name packages earlier in the list, initiatives and sources resolve.

With --verify-quotes it also downloads each source (hash-checked, cached) and
verifies every quote is a verbatim substring of `pdftotext -layout` on the cited
physical page. Exit status 1 on any error.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "schema.yaml"


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def walk(node, path=()):
    """Yield (path, value) for every scalar and container in a YAML document."""
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + (i,))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify-quotes", action="store_true", help="download sources and verify every quote")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "graph.med" / "sources")
    args = ap.parse_args(argv)
    errors: list[str] = []

    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    terminologies = set(schema["x-namespaces"]["terminologies"])
    namespaces = set(schema["x-namespaces"]) - {"terminologies"}
    reserved = namespaces | terminologies | {"schema"}   # a view is served at the site root (docs/publication.md §2)

    # 1. each file against its definition ------------------------------------
    docs: list[tuple[str, object, bool]] = []   # (relative path, document, one_per_file)
    for glob, entry in schema["x-layout"].items():
        validator = Draft202012Validator({"$defs": schema["$defs"], **entry["schema"]})
        for path in sorted(ROOT.glob(glob)):
            rel = str(path.relative_to(ROOT))
            try:
                doc = load(path)
            except yaml.YAMLError as exc:
                errors.append(f"{rel}: YAML error: {exc}")
                continue
            for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
                where = "/".join(str(p) for p in err.absolute_path) or "."
                errors.append(f"{rel} at {where}: {err.message}")
            docs.append((rel, doc, entry.get("one_per_file", False)))

    # 2. cross-file rules -------------------------------------------------------
    ids: dict[str, str] = {}
    for rel, doc, one_per_file in docs:
        for ent in (doc if isinstance(doc, list) else [doc]):
            if not (isinstance(ent, dict) and isinstance(ent.get("id"), str)):
                continue
            eid = ent["id"]
            if eid in ids:
                errors.append(f"{rel}: duplicate id {eid} (also in {ids[eid]})")
            ids[eid] = rel
            if one_per_file and eid != f"{Path(rel).parent.name}/{Path(rel).stem}":
                errors.append(f"{rel}: id {eid} does not match the file name")
            if ent.get("type") == "view" and eid.split("/", 1)[-1] in reserved:
                errors.append(f"{rel}: view id {eid} collides with a namespace; it would shadow that path on the site")
            if ent.get("type") == "claim" and isinstance(ent.get("source"), dict):
                at, quote = ent["source"].get("at", ""), ent["source"].get("quote", "")
                digest = hashlib.sha256(f"{at}|{quote}".encode("utf-8")).hexdigest()[:8]
                expected = f"claims/{at.split('/', 1)[-1].split('#')[0]}/{digest}"
                if eid != expected:
                    errors.append(f"{rel}: claim {eid} should be {expected} (sha256 of locator|quote)")

    # a claim's section must be a section of its source's outline (spec §6.7)
    outlines: dict[str, set[str]] = {}
    for _, doc, _ in docs:
        if isinstance(doc, dict) and doc.get("type") == "source" and isinstance(doc.get("outline"), list):
            outlines[doc["id"]] = {str(e.get("section")) for e in doc["outline"] if isinstance(e, dict)}
    for rel, doc, _ in docs:
        for ent in (doc if isinstance(doc, list) else [doc]):
            if isinstance(ent, dict) and ent.get("type") == "claim" and "section" in ent and isinstance(ent.get("source"), dict):
                src = str(ent["source"].get("at", "")).split("#")[0]
                if src not in outlines:
                    errors.append(f"{rel}: claim {ent.get('id')} has section {ent['section']!r} but {src} has no outline")
                elif str(ent["section"]) not in outlines[src]:
                    errors.append(f"{rel}: claim {ent.get('id')} names section {ent['section']!r}, not in the outline of {src}")

    ref_pattern = re.compile(rf"^({'|'.join(map(re.escape, namespaces))})/")
    seen_edges: set[tuple] = set()
    broader: dict[str, list[str]] = {}
    for rel, doc, _ in docs:
        for path, value in walk(doc):
            if isinstance(value, str) and ref_pattern.match(value) and value.split("#")[0] not in ids:
                errors.append(f"{rel} at {'/'.join(map(str, path))}: {value} does not resolve")
        if rel.startswith("data/edges/") and isinstance(doc, list):
            for i, edge in enumerate(doc):
                if isinstance(edge, list) and len(edge) == 4 and isinstance(edge[3], dict):
                    key = (edge[0], edge[1], edge[2], edge[3].get("discriminator"))
                    if key in seen_edges:
                        errors.append(f"{rel} at {i}: duplicate edge; parallel edges need a discriminator")
                    seen_edges.add(key)
                    if edge[1] == "broader":
                        broader.setdefault(edge[0], []).append(edge[2])

    # broader is a hierarchy: no concept may be a special case of itself (spec §5)
    for cycle in cycles(broader):
        errors.append(f"broader edges form a cycle: {' -> '.join(cycle)}")

    errors += check_work(set(ids))

    n_entities, n_edges = len(ids), len(seen_edges)
    print(f"checked {n_entities} entities and {n_edges} edges against schema {schema.get('x-version')}")

    # 3. quotes against the source text (optional) ------------------------------
    if args.verify_quotes:
        sources = {eid: next(e for _, d, _ in docs for e in (d if isinstance(d, list) else [d])
                             if isinstance(e, dict) and e.get("id") == eid)
                   for eid in ids if eid.startswith("sources/")}
        errors += verify_quotes(docs, sources, args.cache)
        print("verified quotes against the source text")

    for line in errors:
        print(f"error: {line}")
    print(f"{len(errors)} error(s)" if errors else "ok")
    return 1 if errors else 0


WORK = ROOT / "WORK.yaml"
WORK_KINDS = ("extraction", "linking", "schema", "build", "docs", "tooling")


def check_work(ids: set[str]) -> list[str]:
    """WORK.yaml (the registry of work packages) is a list a session takes the first
    entry of, so its order has to be sound: every package has an id, a kind, an
    initiative that exists and an instruction; `depends` names packages above it
    (a done package is removed, so a dependency still listed below would never be
    satisfied); an extraction package names a source entity and its pages."""
    if not WORK.exists():
        return []
    errs: list[str] = []
    try:
        work = load(WORK) or {}
    except yaml.YAMLError as exc:
        return [f"WORK.yaml: YAML error: {exc}"]
    if set(work) - {"initiatives", "packages", "later"}:
        errs.append(f"WORK.yaml: unknown top-level keys {sorted(set(work) - {'initiatives', 'packages', 'later'})}")
    initiatives = work.get("initiatives") or {}
    for name, ini in initiatives.items():
        if not isinstance(ini, dict) or not ini.get("title") or not ini.get("scope"):
            errs.append(f"WORK.yaml: initiative {name} needs a title and a scope")
    if not all(isinstance(x, str) and x.strip() for x in (work.get("later") or [])):
        errs.append("WORK.yaml: every entry under later is a non-empty string")
    above: set[str] = set()
    for i, pkg in enumerate(work.get("packages") or []):
        where = f"WORK.yaml package {i}"
        if not isinstance(pkg, dict) or not pkg.get("id"):
            errs.append(f"{where}: needs an id"); continue
        pid = pkg["id"]; where = f"WORK.yaml package {pid}"
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pid):
            errs.append(f"{where}: id is not kebab-case")
        if pid in above:
            errs.append(f"{where}: duplicate id")
        if set(pkg) - {"id", "initiative", "kind", "depends", "does", "source", "pages"}:
            errs.append(f"{where}: unknown keys {sorted(set(pkg) - {'id', 'initiative', 'kind', 'depends', 'does', 'source', 'pages'})}")
        if pkg.get("kind") not in WORK_KINDS:
            errs.append(f"{where}: kind must be one of {', '.join(WORK_KINDS)}")
        if pkg.get("initiative") not in initiatives:
            errs.append(f"{where}: initiative {pkg.get('initiative')!r} is not declared")
        if not isinstance(pkg.get("does"), str) or not pkg["does"].strip():
            errs.append(f"{where}: needs a does")
        for dep in pkg.get("depends") or []:
            if dep not in above:
                errs.append(f"{where}: depends on {dep}, which is not a package above it (done packages are removed — drop the dependency with them)")
        if pkg.get("kind") == "extraction":
            if pkg.get("source") not in ids:
                errs.append(f"{where}: an extraction package names a source entity")
            if not re.fullmatch(r"\d+(-\d+)?", str(pkg.get("pages", ""))):
                errs.append(f"{where}: an extraction package names its pages (N or N-M)")
        elif pkg.get("source") or pkg.get("pages"):
            errs.append(f"{where}: only an extraction package names a source and pages")
        above.add(pid)
    used = {p.get("initiative") for p in work.get("packages") or [] if isinstance(p, dict)}
    for name in initiatives:
        if name not in used:
            errs.append(f"WORK.yaml: initiative {name} has no package left; remove it with its last package")
    return errs


def cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Every elementary cycle reachable in a directed graph, each reported once from its first node."""
    found: list[list[str]] = []
    state: dict[str, int] = {}          # 1 on the current path, 2 finished
    path: list[str] = []
    def visit(node: str) -> None:
        state[node] = 1
        path.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                found.append(path[path.index(nxt):] + [nxt])
            elif nxt not in state:
                visit(nxt)
        path.pop()
        state[node] = 2
    for start in sorted(graph):
        if start not in state:
            visit(start)
    return found


def verify_quotes(docs, sources: dict[str, dict], cache: Path) -> list[str]:
    errors: list[str] = []
    pdfs: dict[str, Path | None] = {}
    pages: dict[tuple[str, int], str] = {}

    def pdf_for(source_id: str) -> Path | None:
        if source_id in pdfs:
            return pdfs[source_id]
        ent = sources[source_id]
        expected = ent["content_hash"].split(":", 1)[1]
        cache.mkdir(parents=True, exist_ok=True)
        target = cache / f"{expected}.pdf"
        try:
            if not target.exists():
                with urllib.request.urlopen(ent["url"], timeout=120) as resp:
                    target.write_bytes(resp.read())
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                target.unlink()
                raise ValueError("content_hash mismatch")
        except Exception as exc:  # noqa: BLE001 — reported, not raised
            errors.append(f"{source_id}: cannot verify quotes: {exc}")
            target = None
        pdfs[source_id] = target
        return target

    def page_text(source_id: str, page: int) -> str | None:
        pdf = pdf_for(source_id)
        if pdf is None:
            return None
        if (source_id, page) not in pages:
            out = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
                                 capture_output=True, text=True, check=False)
            pages[(source_id, page)] = out.stdout
        return pages[(source_id, page)]

    for rel, doc, _ in docs:
        for path, value in walk(doc):
            if not (isinstance(value, dict) and "at" in value and "quote" in value):
                continue
            m = re.match(r"^(sources/[^#]+)(?:#page=(\d+))?$", str(value["at"]))
            if not m or m.group(1) not in sources:
                continue
            where = f"{rel} at {'/'.join(map(str, path))}"
            if not m.group(2):
                errors.append(f"{where}: locator has no #page=N, quote cannot be verified")
                continue
            text = page_text(m.group(1), int(m.group(2)))
            if text is not None and value["quote"] not in text:
                errors.append(f"{where}: quote not found on page {m.group(2)}: {value['quote']!r}")
    return errors


if __name__ == "__main__":
    sys.exit(main())
