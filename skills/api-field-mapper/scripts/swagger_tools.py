#!/usr/bin/env python3
"""
swagger_tools.py — Inspect large Swagger 2.0 / OpenAPI 3 JSON files without
having to load the raw JSON into an LLM context window. Supports both spec
styles transparently.

Subcommands:

  index   List every operation (service, method, path, tags, operationId, summary)
          across one or more files. Use this first to get the lay of the land.

  search  Full-text search (case-insensitive) across operations (path, tags,
          operationId, summary, description) AND schema property names, across
          one or more files. Use this to find candidate endpoints/fields for a
          business term (e.g. "resident", "guarantor", "collateral").

  show    Print one operation's full resolved detail: parameters, request body
          schema, and success-response schema, with $ref chains recursively
          dereferenced into a readable indented tree. Use this once you've
          picked a candidate path+method from index/search.

  props   Print the resolved property tree of a schema/definition by name
          (substring match), independent of any operation. Useful when a field
          hint points to a DTO name directly.

Files can be passed individually with --file (repeatable) or all *.json files
in a directory with --dir.

Examples:
  python swagger_tools.py index --dir swagger_json/lending
  python swagger_tools.py index --dir swagger_json/lending --tag Customer
  python swagger_tools.py search --dir swagger_json/lending --q "resident"
  python swagger_tools.py show --file swagger_json/lending/lending-origination.json \\
      --path /api/v1/customers/search --method get
  python swagger_tools.py props --file swagger_json/lending/lending-origination.json \\
      --name CustomerDto
"""
import argparse
import glob
import json
import os
import sys

METHODS = ["get", "post", "put", "patch", "delete", "head", "options"]
MAX_DEPTH = 8


def load_spec(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_openapi3(spec):
    return "openapi" in spec


def get_schemas(spec):
    if is_openapi3(spec):
        return (spec.get("components") or {}).get("schemas") or {}
    return spec.get("definitions") or {}


def resolve_ref(ref, spec):
    name = ref.split("/")[-1]
    return name, get_schemas(spec).get(name)


def resolve_schema(schema, spec, depth=0, seen=None):
    if seen is None:
        seen = frozenset()
    if schema is None:
        return {"type": "unknown"}
    if depth > MAX_DEPTH:
        return {"type": "...", "note": "max depth reached"}

    if "$ref" in schema:
        name, target = resolve_ref(schema["$ref"], spec)
        if target is None:
            return {"type": "unknown", "ref": schema["$ref"], "unresolved": True}
        if name in seen:
            return {"type": "object", "schemaName": name, "note": "circular reference, not expanded further"}
        resolved = resolve_schema(target, spec, depth + 1, seen | {name})
        if isinstance(resolved, dict):
            resolved = dict(resolved)
            resolved["schemaName"] = name
        return resolved

    for key in ("allOf", "oneOf", "anyOf"):
        if key in schema:
            merged_props, merged_required, parts = {}, [], []
            for sub in schema[key]:
                r = resolve_schema(sub, spec, depth + 1, seen)
                parts.append(r)
                if isinstance(r, dict) and r.get("type") == "object":
                    merged_props.update(r.get("properties") or {})
                    merged_required.extend(r.get("required") or [])
            if key == "allOf":
                out = {"type": "object", "properties": merged_props}
                if merged_required:
                    out["required"] = sorted(set(merged_required))
                return out
            return {"type": key, "options": parts}

    t = schema.get("type")
    if t == "array" or "items" in schema:
        return {"type": "array", "items": resolve_schema(schema.get("items") or {}, spec, depth + 1, seen)}

    if t == "object" or "properties" in schema:
        props = {}
        for pname, pschema in (schema.get("properties") or {}).items():
            props[pname] = resolve_schema(pschema, spec, depth + 1, seen)
        out = {"type": "object", "properties": props}
        if schema.get("required"):
            out["required"] = schema["required"]
        return out

    out = {"type": t or "unknown"}
    for k in ("format", "enum", "description", "example"):
        if k in schema:
            out[k] = schema[k]
    return out


def print_tree(tree, indent=0, name=None, required_names=None):
    pad = "  " * indent
    required_names = required_names or set()
    req_tag = " (required)" if name in required_names else ""
    t = tree.get("type", "unknown") if isinstance(tree, dict) else "unknown"
    schema_name = tree.get("schemaName") if isinstance(tree, dict) else None
    label = f"{name}: " if name else ""
    name_suffix = f" [{schema_name}]" if schema_name else ""

    if t == "object":
        print(f"{pad}{label}object{name_suffix}{req_tag}")
        props = tree.get("properties") or {}
        req = set(tree.get("required") or [])
        if not props:
            print(f"{pad}  (no properties defined)")
        for pname, pschema in props.items():
            print_tree(pschema, indent + 1, pname, req)
    elif t == "array":
        print(f"{pad}{label}array{req_tag}")
        print_tree(tree.get("items") or {}, indent + 1, "[item]")
    elif t in ("oneOf", "anyOf"):
        print(f"{pad}{label}{t}{req_tag}")
        for i, opt in enumerate(tree.get("options") or []):
            print_tree(opt, indent + 1, f"option{i}")
    else:
        extras = []
        if tree.get("format"):
            extras.append(f"format={tree['format']}")
        if tree.get("enum"):
            extras.append(f"enum={tree['enum']}")
        if tree.get("description"):
            extras.append(f"desc=\"{tree['description']}\"")
        extra_str = (" " + " ".join(extras)) if extras else ""
        print(f"{pad}{label}{t}{name_suffix}{req_tag}{extra_str}")


def collect_files(args):
    files = list(args.file or [])
    if args.dir:
        for d in args.dir:
            files.extend(sorted(glob.glob(os.path.join(d, "*.json"))))
    files = [f for f in files if not os.path.basename(f).startswith("_")]
    if not files:
        print("ERROR: no input files. Use --file or --dir.", file=sys.stderr)
        sys.exit(1)
    return files


def iter_operations(spec):
    for path, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in METHODS:
            op = path_item.get(method)
            if isinstance(op, dict):
                yield path, method, op


def cmd_index(args):
    files = collect_files(args)
    for fpath in files:
        service = os.path.splitext(os.path.basename(fpath))[0]
        spec = load_spec(fpath)
        for path, method, op in iter_operations(spec):
            tags = op.get("tags") or []
            if args.tag and not any(args.tag.lower() in t.lower() for t in tags):
                continue
            op_id = op.get("operationId", "")
            summary = op.get("summary", "") or op.get("description", "")
            if args.q:
                haystack = " ".join([path, op_id, summary, " ".join(tags)]).lower()
                if args.q.lower() not in haystack:
                    continue
            print(f"[{service}] {method.upper():6s} {path}  tags={tags} opId={op_id}  summary={summary[:100]}")


def schema_matches_q(pname, pschema, q):
    ql = q.lower()
    if ql in pname.lower():
        return True
    desc = (pschema or {}).get("description", "") or ""
    return ql in desc.lower()


def cmd_search(args):
    files = collect_files(args)
    q = args.q.lower()
    for fpath in files:
        service = os.path.splitext(os.path.basename(fpath))[0]
        spec = load_spec(fpath)

        print(f"\n=== {service} : operation matches ===")
        found_op = False
        for path, method, op in iter_operations(spec):
            tags = op.get("tags") or []
            op_id = op.get("operationId", "")
            summary = op.get("summary", "") or op.get("description", "")
            haystack = " ".join([path, op_id, summary, " ".join(tags)]).lower()
            if q in haystack:
                found_op = True
                print(f"  {method.upper():6s} {path}  tags={tags} opId={op_id}  summary={summary[:100]}")
        if not found_op:
            print("  (no operation matches)")

        print(f"=== {service} : schema property matches ===")
        schemas = get_schemas(spec)
        found_prop = False
        for sname, sdef in schemas.items():
            props = (sdef or {}).get("properties") or {}
            for pname, pschema in props.items():
                if schema_matches_q(pname, pschema, args.q) or q in sname.lower():
                    found_prop = True
                    ptype = (pschema or {}).get("type") or ("$ref" in (pschema or {}) and pschema["$ref"].split("/")[-1]) or "object"
                    print(f"  {sname}.{pname}  (type={ptype})")
        if not found_prop:
            print("  (no schema property matches)")


def cmd_show(args):
    spec = load_spec(args.file[0])
    path_item = (spec.get("paths") or {}).get(args.path)
    if path_item is None:
        # tolerant lookup ignoring trailing slash / case
        for p in (spec.get("paths") or {}):
            if p.rstrip("/").lower() == args.path.rstrip("/").lower():
                path_item = spec["paths"][p]
                args.path = p
                break
    if path_item is None:
        print(f"ERROR: path '{args.path}' not found in {args.file[0]}", file=sys.stderr)
        sys.exit(1)
    op = path_item.get(args.method.lower())
    if op is None:
        print(f"ERROR: method '{args.method}' not found on path '{args.path}'. "
              f"Available: {[m for m in METHODS if m in path_item]}", file=sys.stderr)
        sys.exit(1)

    print(f"{args.method.upper()} {args.path}")
    print(f"  tags: {op.get('tags')}")
    print(f"  operationId: {op.get('operationId')}")
    print(f"  summary: {op.get('summary')}")
    if op.get("description"):
        print(f"  description: {op.get('description')}")

    params = op.get("parameters") or []
    non_body = [p for p in params if p.get("in") != "body"]
    body_param = next((p for p in params if p.get("in") == "body"), None)

    if non_body:
        print("\n  -- Parameters --")
        for p in non_body:
            req = " (required)" if p.get("required") else ""
            print(f"    {p.get('name')} [in={p.get('in')}] type={p.get('type', p.get('schema', {}).get('type', 'object'))}{req}"
                  + (f" desc=\"{p['description']}\"" if p.get("description") else ""))

    print("\n  -- Request body --")
    if body_param is not None:
        tree = resolve_schema(body_param.get("schema") or {}, spec)
        print_tree(tree, indent=2)
    elif is_openapi3(spec) and op.get("requestBody"):
        content = (op["requestBody"].get("content") or {})
        json_content = content.get("application/json") or next(iter(content.values()), {})
        tree = resolve_schema(json_content.get("schema") or {}, spec)
        print_tree(tree, indent=2)
    else:
        print("    (none)")

    print("\n  -- Responses --")
    responses = op.get("responses") or {}
    success_code = next((c for c in ("200", "201") if c in responses), next(iter(responses), None))
    if success_code:
        resp = responses[success_code]
        print(f"    [{success_code}] {resp.get('description', '')}")
        if is_openapi3(spec):
            content = (resp.get("content") or {})
            json_content = content.get("application/json") or next(iter(content.values()), {})
            schema = json_content.get("schema")
        else:
            schema = resp.get("schema")
        if schema:
            tree = resolve_schema(schema, spec)
            print_tree(tree, indent=2)
        else:
            print("      (no response body schema)")
    else:
        print("    (no responses documented)")


def cmd_props(args):
    spec = load_spec(args.file[0])
    schemas = get_schemas(spec)
    matches = [name for name in schemas if args.name.lower() in name.lower()]
    if not matches:
        print(f"No schema matching '{args.name}' in {args.file[0]}")
        return
    for name in matches:
        print(f"\n=== {name} ===")
        tree = resolve_schema(schemas[name], spec)
        print_tree(tree, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--file", action="append", help="Swagger/OpenAPI JSON file (repeatable)")
    common.add_argument("--dir", action="append", help="Directory of *.json files (repeatable)")

    p_index = sub.add_parser("index", parents=[common], help="List all operations")
    p_index.add_argument("--tag", help="Filter by tag substring")
    p_index.add_argument("--q", help="Filter by keyword substring across path/opId/summary/tags")
    p_index.set_defaults(func=cmd_index)

    p_search = sub.add_parser("search", parents=[common], help="Search operations and schema properties")
    p_search.add_argument("--q", required=True, help="Keyword to search for")
    p_search.set_defaults(func=cmd_search)

    p_show = sub.add_parser("show", parents=[common], help="Show full resolved detail for one operation")
    p_show.add_argument("--path", required=True)
    p_show.add_argument("--method", required=True)
    p_show.set_defaults(func=cmd_show)

    p_props = sub.add_parser("props", parents=[common], help="Show resolved properties of a schema by name")
    p_props.add_argument("--name", required=True)
    p_props.set_defaults(func=cmd_props)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
