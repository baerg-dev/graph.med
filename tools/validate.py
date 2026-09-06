#!/usr/bin/env python3
"""Validate the pool under data/ against schema/schema.yaml.

The schema is a JSON Schema (draft 2020-12) and the single point of truth. This
script only (1) validates each data file against the definition the schema's
`x-layout` assigns to it, using the jsonschema library, and (2) checks the few
rules a document schema cannot state because they span files:

  - every id is unique, and in one-per-file namespaces equals <ns>/<file stem>;
  - every entity reference in the data resolves (terminology codes excepted);
  - a claim's id is claims/<source-id>/<first 8 hex of sha256("<at>|<quote>")>;
  - edges are unique per (from, kind, to, discriminator).

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
            if ent.get("type") == "claim" and isinstance(ent.get("source"), dict):
                at, quote = ent["source"].get("at", ""), ent["source"].get("quote", "")
                digest = hashlib.sha256(f"{at}|{quote}".encode("utf-8")).hexdigest()[:8]
                expected = f"claims/{at.split('/', 1)[-1].split('#')[0]}/{digest}"
                if eid != expected:
                    errors.append(f"{rel}: claim {eid} should be {expected} (sha256 of locator|quote)")

    ref_pattern = re.compile(rf"^({'|'.join(map(re.escape, namespaces))})/")
    seen_edges: set[tuple] = set()
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
