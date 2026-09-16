#!/usr/bin/env python3
"""
fetch_swagger.py — Fetch fresh Swagger/OpenAPI JSON docs for a registered module
(or ad-hoc URLs) and save them to disk. Meant to be re-run every time an API
mapping task starts, so the JSONs on disk are always the latest from the server.

Usage:
    python fetch_swagger.py --module lending [--outdir DIR] [--config PATH]
    python fetch_swagger.py --url http://host/service/swagger-ui.html [--url ...] --outdir DIR
    python fetch_swagger.py --list-modules [--config PATH]

Behavior:
    - Accepts either a direct api-docs URL (.../v2/api-docs, .../v3/api-docs) or a
      swagger-ui.html URL, from which it derives candidate api-docs URLs.
    - Service name is auto-derived from the first path segment of the URL
      (e.g. "lending-product" from http://host/lending-product/swagger-ui.html).
    - Saves the raw JSON response verbatim to <outdir>/<service>.json (overwriting
      any previous copy — this IS the "latest" copy by design).
    - Writes/overwrites <outdir>/_fetch_report.json with per-service fetch metadata
      (resolved URL used, HTTP status, title, version, spec type, #paths, #schemas,
      timestamp) for audit purposes.
    - Never aborts the whole run because one service failed — reports per-service
      success/failure and exits non-zero only if EVERY source failed.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERROR: the 'requests' package is required. Install it with: pip install requests", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(os.path.dirname(SCRIPT_DIR), "config", "modules.json")

SWAGGER_UI_SUFFIXES = [
    "swagger-ui/index.html",
    "swagger-ui.html",
    "swagger-ui/",
    "swagger-ui",
]


def derive_service_name(url):
    path = urlparse(url).path.strip("/")
    parts = [p for p in path.split("/") if p]
    if parts:
        return parts[0]
    return urlparse(url).hostname or "service"


def derive_api_docs_candidates(url):
    url = url.strip().rstrip("/")
    if url.endswith("api-docs") or "/v2/api-docs" in url or "/v3/api-docs" in url:
        return [url]
    for suffix in SWAGGER_UI_SUFFIXES:
        if url.endswith(suffix):
            base = url[: -len(suffix)].rstrip("/")
            return [f"{base}/v2/api-docs", f"{base}/v3/api-docs", f"{base}/swagger.json"]
    # Fallback: treat given URL as a base and try common suffixes, plus itself.
    return [f"{url}/v2/api-docs", f"{url}/v3/api-docs", f"{url}/swagger.json", url]


def fetch_one(candidates, timeout=20):
    last_err = None
    for c in candidates:
        try:
            r = requests.get(c, timeout=timeout)
        except Exception as e:  # noqa: BLE001
            last_err = f"{c} -> {e}"
            continue
        if r.status_code == 200:
            ctype = r.headers.get("Content-Type", "")
            try:
                data = r.json()
            except Exception as e:  # noqa: BLE001
                last_err = f"{c} -> HTTP 200 but not valid JSON ({e})"
                continue
            return c, r.content, data, ctype
        last_err = f"{c} -> HTTP {r.status_code}"
    raise RuntimeError(last_err or "no candidates tried")


def summarize(data):
    is_openapi3 = "openapi" in data
    info = data.get("info", {}) or {}
    if is_openapi3:
        schemas = ((data.get("components") or {}).get("schemas") or {})
        servers = data.get("servers") or []
        base = servers[0].get("url", "") if servers else ""
        spec_type = f"OpenAPI {data.get('openapi')}"
    else:
        schemas = data.get("definitions") or {}
        base = data.get("basePath", "")
        spec_type = f"Swagger {data.get('swagger', '2.0')}"
    return {
        "spec_type": spec_type,
        "title": info.get("title", ""),
        "version": info.get("version", ""),
        "base_path": base,
        "num_paths": len(data.get("paths") or {}),
        "num_schemas": len(schemas),
    }


def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", help="Module key from the config file (e.g. lending, casa, td)")
    ap.add_argument("--url", action="append", default=[], help="Ad-hoc swagger-ui.html or api-docs URL (repeatable)")
    ap.add_argument("--outdir", help="Output directory for JSON files (default: ./swagger_json/<module> or ./swagger_json/adhoc)")
    ap.add_argument("--config", default=DEFAULT_CONFIG, help="Path to modules.json config")
    ap.add_argument("--list-modules", action="store_true", help="List configured modules and their sources, then exit")
    args = ap.parse_args()

    config = load_config(args.config)

    if args.list_modules:
        if not config:
            print("No modules configured yet.")
            return
        for key, entry in config.items():
            print(f"[{key}] {entry.get('display_name', key)}")
            sources = entry.get("swagger_sources", [])
            if not sources:
                print("    (no swagger sources registered yet)")
            for s in sources:
                print(f"    - {s}")
        return

    urls = list(args.url)
    if args.module:
        entry = config.get(args.module)
        if entry is None:
            print(f"ERROR: module '{args.module}' not found in {args.config}. "
                  f"Known modules: {list(config.keys())}", file=sys.stderr)
            sys.exit(1)
        urls.extend(entry.get("swagger_sources", []))

    if not urls:
        print("ERROR: no URLs to fetch. Provide --module (with sources in config) and/or --url.", file=sys.stderr)
        sys.exit(1)

    outdir = args.outdir or os.path.join("swagger_json", args.module or "adhoc")
    os.makedirs(outdir, exist_ok=True)

    report = {}
    ok_count = 0
    fetched_at = datetime.now(timezone.utc).isoformat()

    for url in urls:
        service = derive_service_name(url)
        candidates = derive_api_docs_candidates(url)
        try:
            resolved_url, raw_bytes, data, ctype = fetch_one(candidates)
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {service}: {e}")
            report[service] = {"status": "failed", "source_url": url, "error": str(e), "fetched_at": fetched_at}
            continue

        out_path = os.path.join(outdir, f"{service}.json")
        with open(out_path, "wb") as f:
            f.write(raw_bytes)

        meta = summarize(data)
        report[service] = {
            "status": "ok",
            "source_url": url,
            "resolved_url": resolved_url,
            "content_type": ctype,
            "saved_to": out_path,
            "fetched_at": fetched_at,
            **meta,
        }
        ok_count += 1
        print(f"[OK]   {service}: {meta['spec_type']} | title='{meta['title']}' v{meta['version']} | "
              f"{meta['num_paths']} paths, {meta['num_schemas']} schemas | saved -> {out_path}")

    report_path = os.path.join(outdir, "_fetch_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nFetch report -> {report_path}")
    print(f"{ok_count}/{len(urls)} sources fetched successfully.")

    if ok_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
