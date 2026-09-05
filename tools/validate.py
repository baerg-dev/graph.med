#!/usr/bin/env python3
"""Validate the pool under data/ against schema/schema.yaml.

The schema is the authority on syntax (docs/graph-representation.md §9); this
script is what enforces it. It checks:

  - every YAML file parses; one entity per file in the one-per-file namespaces,
    a list of entities in claims/, a list of edges in edges/;
  - ids are unique, live in the namespace their type belongs to, and match the
    file that holds them;
  - every property is one the schema knows, required properties are present,
    enum values and value shapes (bcp47, sha256, url, date, concept-url) are
    valid;
  - provenance: every entity that has sourced properties carries a default
    `source`; overrides under `provenance:` name real properties; a property
    the schema marks `provenance: required` never resolves to `modelling`;
    every reference names an existing source with a non-empty quote;
  - claims: the id is the first 8 hex of sha256("<locator>|<quote>");
  - statements: slots are schema slots and reference existing concepts;
  - edges: known kind, endpoint types match the schema, endpoints resolve,
    modelling-only kinds carry their required properties, derived ids
    (from, kind, to[, discriminator]) are unique;
  - with --verify-quotes: each source is downloaded (or read from --cache),
    its content_hash verified, and every quote checked to be a verbatim
    single-line substring of `pdftotext -layout` on the physical page it cites.

Exit status is 1 when any error was found, 0 otherwise. No dependency beyond
PyYAML (tools/requirements.txt); --verify-quotes needs pdftotext (poppler).
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

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "schema.yaml"
DATA = ROOT / "data"

# Which namespace each node type is minted in (spec §2).
TYPE_NAMESPACE = {
    "source": "sources",
    "claim": "claims",
    "concept": "concepts",
    "statement": "statements",
    "decision": "pathways",
    "outcome": "pathways",
    "gap": "pathways",
    "agent": "agents",
    "attestation": "attestations",
    "view": "views",
}
ONE_PER_FILE = {"sources", "concepts", "statements", "views", "agents", "attestations"}
BASE_KEYS = {"id", "type", "source", "provenance"}
EDGE_BASE_KEYS = {"source", "provenance", "lang", "discriminator"}
RE_BCP47 = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
RE_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_LOCATOR = re.compile(r"^(sources/[A-Za-z0-9._-]+)(#page=(\d+))?$")
RE_ID = re.compile(r"^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)+$")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")


def load_yaml(path: Path, rep: Report):
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:  # pragma: no cover - reported, not raised
        rep.error(str(path.relative_to(ROOT)), f"YAML error: {exc}")
        return None


def is_reference(value) -> bool:
    return isinstance(value, dict) and "at" in value and "quote" in value


# ── value shapes ─────────────────────────────────────────────────────────────

def check_value(where: str, prop: str, spec: dict, value, rep: Report, terminologies: set[str]) -> None:
    kind = spec.get("type", "any")
    ok = True
    if kind == "string":
        ok = isinstance(value, str) and value.strip() != ""
    elif kind == "bcp47":
        ok = isinstance(value, str) and bool(RE_BCP47.match(value))
    elif kind == "sha256":
        ok = isinstance(value, str) and bool(RE_SHA256.match(value))
    elif kind == "url":
        ok = isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))
    elif kind == "date":
        ok = isinstance(value, str) and bool(RE_DATE.match(value)) or hasattr(value, "isoformat")
    elif kind == "enum":
        values = [str(v) for v in spec.get("values", [])]
        ok = str(value) in values
        if not ok:
            rep.error(where, f"{prop}: {value!r} is not one of {values}")
            return
    elif kind == "list":
        ok = isinstance(value, list)
    elif kind == "object":
        ok = isinstance(value, dict)
    elif kind == "concept-url":
        ok = isinstance(value, str) and (
            value.startswith("concepts/") or any(value.startswith(t + "/") for t in terminologies)
        )
    elif kind == "agent-url":
        ok = isinstance(value, str) and value.startswith("agents/")
    elif kind == "any":
        ok = True
    if not ok:
        rep.error(where, f"{prop}: {value!r} is not a valid {kind}")


# ── provenance ───────────────────────────────────────────────────────────────

def check_provenance_value(where: str, label: str, value, rep: Report, source_ids: set[str]) -> None:
    """A provenance value is `modelling`, one reference, or a list of references."""
    if value == "modelling":
        return
    refs = value if isinstance(value, list) else [value]
    if not refs:
        rep.error(where, f"{label}: empty provenance list")
    for ref in refs:
        if not is_reference(ref):
            rep.error(where, f"{label}: expected 'modelling' or {{at, quote}}, got {ref!r}")
            continue
        m = RE_LOCATOR.match(str(ref["at"]))
        if not m:
            rep.error(where, f"{label}: locator {ref['at']!r} is not sources/<id>[#page=N]")
        elif m.group(1) not in source_ids:
            rep.error(where, f"{label}: locator names unknown source {m.group(1)}")
        if not isinstance(ref["quote"], str) or not ref["quote"].strip():
            rep.error(where, f"{label}: quote must be a non-empty string")
        elif "\n" in ref["quote"]:
            rep.error(where, f"{label}: quote must be a single line")


# ── entities ─────────────────────────────────────────────────────────────────

def check_entity(where: str, ent, schema: dict, rep: Report, source_ids: set[str], terminologies: set[str]) -> None:
    if not isinstance(ent, dict):
        rep.error(where, f"entity is not a mapping: {ent!r}")
        return
    eid, etype = ent.get("id"), ent.get("type")
    if not isinstance(eid, str) or not RE_ID.match(eid):
        rep.error(where, f"missing or malformed id: {eid!r}")
        return
    where = f"{where} [{eid}]"
    node_types = schema["node_types"]
    if etype not in node_types:
        rep.error(where, f"unknown type {etype!r}")
        return
    ns = eid.split("/")[0]
    if TYPE_NAMESPACE[etype] != ns:
        rep.error(where, f"type {etype} belongs in {TYPE_NAMESPACE[etype]}/, id is in {ns}/")

    props: dict = node_types[etype].get("properties", {})
    allowed = BASE_KEYS | set(props)
    for key in ent:
        if key not in allowed:
            rep.error(where, f"property {key!r} is not in the schema for {etype}")

    for prop, spec in props.items():
        if prop == "slots":
            continue
        if spec.get("required") and prop not in ent:
            rep.error(where, f"required property {prop!r} missing")
        if prop in ent:
            check_value(where, prop, spec, ent[prop], rep, terminologies)

    # provenance: default on the entity, override per property (spec §6.4)
    needs_source = any(spec.get("provenance") in ("required", "optional") for spec in props.values())
    default = ent.get("source")
    if needs_source and default is None:
        rep.error(where, "entity carries sourced properties but no default `source`")
    if default is not None:
        check_provenance_value(where, "source", default, rep, source_ids)
    overrides = ent.get("provenance") or {}
    if not isinstance(overrides, dict):
        rep.error(where, "`provenance` must be a mapping of property → provenance value")
        overrides = {}
    for prop, value in overrides.items():
        if prop not in props:
            rep.error(where, f"provenance override for unknown property {prop!r}")
        elif prop not in ent:
            rep.error(where, f"provenance override for absent property {prop!r}")
        elif props[prop].get("provenance") == "not_applicable":
            rep.error(where, f"provenance override for {prop!r}, which takes no provenance")
        check_provenance_value(where, f"provenance.{prop}", value, rep, source_ids)
    for prop, spec in props.items():
        if spec.get("provenance") == "required" and prop in ent:
            resolved = overrides.get(prop, default)
            if resolved is None:
                rep.error(where, f"{prop} requires provenance and none resolves")
            elif resolved == "modelling":
                rep.error(where, f"{prop} requires a source passage, resolves to `modelling`")

    if etype == "claim":
        anchor = ent.get("source")
        if is_reference(anchor):
            digest = hashlib.sha256(f"{anchor['at']}|{anchor['quote']}".encode("utf-8")).hexdigest()[:8]
            expected_prefix = "claims/"
            parts = eid.split("/")
            if len(parts) != 3 or parts[2] != digest:
                rep.error(where, f"claim id must be claims/<source-id>/{digest} (sha256 of locator|quote)")
            elif f"sources/{parts[1]}" != RE_LOCATOR.match(str(anchor["at"])).group(1):
                rep.error(where, "claim id's source segment does not match its locator")
            _ = expected_prefix
        else:
            rep.error(where, "a claim's default `source` must be a single reference {at, quote}")

    if etype == "statement":
        slot_specs = props.get("slots", {})
        slots = ent.get("slots") or {}
        if not isinstance(slots, dict):
            rep.error(where, "`slots` must be a mapping")
        else:
            for slot, value in slots.items():
                if slot not in slot_specs:
                    rep.error(where, f"unknown slot {slot!r}")
                else:
                    check_value(where, f"slots.{slot}", slot_specs[slot], value, rep, terminologies)


# ── edges ────────────────────────────────────────────────────────────────────

def endpoint_matches(expected, actual_type: str | None, target: str, terminologies: set[str]) -> bool:
    expected = expected if isinstance(expected, list) else [expected]
    for e in expected:
        if e == "terminology-concept":
            if any(target.startswith(t + "/") for t in terminologies):
                return True
        elif actual_type == e:
            return True
    return False


def check_edge(where: str, edge, schema: dict, entities: dict[str, dict], rep: Report,
               source_ids: set[str], terminologies: set[str], seen_edges: set[tuple]) -> None:
    if not (isinstance(edge, list) and 3 <= len(edge) <= 4 and all(isinstance(x, str) for x in edge[:3])):
        rep.error(where, f"edge must be [from, kind, to, {{properties}}]: {edge!r}")
        return
    src, kind, dst = edge[0], edge[1], edge[2]
    props = edge[3] if len(edge) == 4 else {}
    where = f"{where} [{src} {kind} {dst}]"
    kinds = schema["edge_kinds"]
    if kind not in kinds:
        rep.error(where, f"unknown edge kind {kind!r}")
        return
    spec = kinds[kind]
    if not isinstance(props, dict):
        rep.error(where, "edge properties must be a mapping")
        return

    for endpoint, side in ((src, "from"), (dst, "to")):
        ent = entities.get(endpoint)
        is_term = any(endpoint.startswith(t + "/") for t in terminologies)
        if ent is None and not is_term:
            rep.error(where, f"{side} endpoint {endpoint} does not exist")
        elif not endpoint_matches(spec[side], ent.get("type") if ent else None, endpoint, terminologies):
            rep.error(where, f"{side} endpoint must be {spec[side]}, is {ent.get('type') if ent else 'terminology-concept'}")

    edge_props: dict = spec.get("properties", {})
    allowed = EDGE_BASE_KEYS | set(edge_props)
    for key in props:
        if key not in allowed:
            rep.error(where, f"property {key!r} is not in the schema for edge kind {kind}")
    for prop, pspec in edge_props.items():
        if pspec.get("required") and prop not in props:
            rep.error(where, f"required property {prop!r} missing")
        if prop in props:
            check_value(where, prop, pspec, props[prop], rep, terminologies)

    if "source" not in props:
        rep.error(where, "every edge carries provenance; `source` missing")
    else:
        check_provenance_value(where, "source", props["source"], rep, source_ids)
        if spec.get("provenance") == "modelling-only" and props["source"] != "modelling":
            rep.error(where, f"{kind} edges are modelling-only")
    if any(isinstance(props.get(p), str) for p in ("rationale", "guard")) and "lang" not in props:
        rep.error(where, "edge carries text (rationale/guard) but declares no `lang`")
    if "lang" in props and not RE_BCP47.match(str(props["lang"])):
        rep.error(where, f"lang {props['lang']!r} is not BCP 47")

    key = (src, kind, dst, props.get("discriminator"))
    if key in seen_edges:
        rep.error(where, "duplicate edge; parallel edges of one kind need a `discriminator`")
    seen_edges.add(key)


# ── quotes against the source text ───────────────────────────────────────────

def fetch_source(ent: dict, cache: Path, rep: Report) -> Path | None:
    expected = ent["content_hash"].split(":", 1)[1]
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / f"{expected}.pdf"
    if not target.exists():
        try:
            with urllib.request.urlopen(ent["url"], timeout=120) as resp:
                target.write_bytes(resp.read())
        except Exception as exc:  # noqa: BLE001 - reported
            rep.error(ent["id"], f"could not fetch {ent['url']}: {exc}")
            return None
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != expected:
        target.unlink()
        rep.error(ent["id"], f"content_hash mismatch: expected {expected}, got {actual}")
        return None
    return target


def verify_quotes(entities: dict[str, dict], edges_props: list[tuple[str, dict]], cache: Path, rep: Report) -> None:
    pdfs: dict[str, Path | None] = {}
    pages: dict[tuple[str, int], str] = {}

    def page_text(source_id: str, page: int) -> str | None:
        if source_id not in pdfs:
            pdfs[source_id] = fetch_source(entities[source_id], cache, rep)
        pdf = pdfs[source_id]
        if pdf is None:
            return None
        key = (source_id, page)
        if key not in pages:
            out = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
                                 capture_output=True, text=True, check=False)
            pages[key] = out.stdout
        return pages[key]

    def check(where: str, label: str, value) -> None:
        if value == "modelling" or value is None:
            return
        for ref in value if isinstance(value, list) else [value]:
            if not is_reference(ref):
                continue
            m = RE_LOCATOR.match(str(ref["at"]))
            if not m or m.group(1) not in entities:
                continue
            if not m.group(3):
                rep.error(where, f"{label}: locator has no #page=N, quote cannot be verified")
                continue
            text = page_text(m.group(1), int(m.group(3)))
            if text is None:
                continue
            if ref["quote"] not in text:
                rep.error(where, f"{label}: quote not found on page {m.group(3)}: {ref['quote']!r}")

    for eid, ent in entities.items():
        check(eid, "source", ent.get("source"))
        for prop, value in (ent.get("provenance") or {}).items():
            check(eid, f"provenance.{prop}", value)
    for where, props in edges_props:
        check(where, "source", props.get("source"))


# ── driver ───────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify-quotes", action="store_true",
                    help="download each source (hash-checked) and verify every quote on its page")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "graph.med" / "sources",
                    help="where downloaded sources are kept, named <sha256>.pdf")
    args = ap.parse_args(argv)

    rep = Report()
    schema = load_yaml(SCHEMA_PATH, rep)
    if not schema:
        return finish(rep)
    terminologies = set(schema.get("namespaces", {}).get("terminologies", []) or [])
    if not DATA.is_dir():
        print("no data/ directory; nothing to validate")
        return finish(rep)

    entities: dict[str, dict] = {}
    files_of: dict[str, str] = {}
    edge_files: list[tuple[str, list]] = []

    for path in sorted(DATA.rglob("*.yaml")):
        rel = str(path.relative_to(ROOT))
        parts = path.relative_to(DATA).parts
        ns = parts[0]
        if path.name == "PROGRESS.yaml" and len(parts) == 1:
            continue
        doc = load_yaml(path, rep)
        if doc is None:
            continue
        if ns == "edges":
            if not isinstance(doc, list):
                rep.error(rel, "an edges file is a list of edges")
                continue
            edge_files.append((rel, doc))
            continue
        items = doc if isinstance(doc, list) else [doc]
        if ns in ONE_PER_FILE and (isinstance(doc, list) or len(parts) != 2):
            rep.error(rel, f"{ns}/ holds one entity per file, data/{ns}/<id>.yaml")
        if ns == "claims" and (not isinstance(doc, list) or len(parts) != 3):
            rep.error(rel, "claims/ holds a list of claims per data/claims/<source-id>/<chunk>.yaml")
        for i, ent in enumerate(items):
            where = rel if len(items) == 1 else f"{rel}#{i}"
            if not isinstance(ent, dict) or not isinstance(ent.get("id"), str):
                rep.error(where, f"entity without a string id: {ent!r}")
                continue
            eid = ent["id"]
            if eid in entities:
                rep.error(where, f"duplicate id {eid} (also in {files_of[eid]})")
                continue
            if ns in ONE_PER_FILE and eid != f"{ns}/{path.stem}":
                rep.error(where, f"id {eid} does not match file name; expected {ns}/{path.stem}")
            if ns == "claims" and len(parts) == 3 and not eid.startswith(f"claims/{parts[1]}/"):
                rep.error(where, f"claim {eid} filed under data/claims/{parts[1]}/")
            entities[eid] = ent
            files_of[eid] = where

    source_ids = {eid for eid, e in entities.items() if e.get("type") == "source"}
    for eid, ent in entities.items():
        check_entity(files_of[eid], ent, schema, rep, source_ids, terminologies)
        if ent.get("type") == "statement" and isinstance(ent.get("slots"), dict):
            for slot, target in ent["slots"].items():
                if isinstance(target, str) and target not in entities \
                        and not any(target.startswith(t + "/") for t in terminologies):
                    rep.error(f"{files_of[eid]} [{eid}]", f"slot {slot} references missing {target}")

    seen_edges: set[tuple] = set()
    edges_props: list[tuple[str, dict]] = []
    for rel, edges in edge_files:
        for i, edge in enumerate(edges):
            where = f"{rel}#{i}"
            check_edge(where, edge, schema, entities, rep, source_ids, terminologies, seen_edges)
            if isinstance(edge, list) and len(edge) == 4 and isinstance(edge[3], dict):
                edges_props.append((f"{where} [{edge[0]} {edge[1]} {edge[2]}]", edge[3]))

    n_edges = sum(len(e) for _, e in edge_files)
    print(f"checked {len(entities)} entities and {n_edges} edges against schema {schema.get('version')}")
    if args.verify_quotes:
        verify_quotes(entities, edges_props, args.cache, rep)
        print("verified quotes against the source text")
    return finish(rep)


def finish(rep: Report) -> int:
    for line in rep.errors:
        print(f"error: {line}")
    if rep.errors:
        print(f"{len(rep.errors)} error(s)")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
