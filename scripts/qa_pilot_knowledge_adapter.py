#!/usr/bin/env python3
"""
QA Pilot Librarian Knowledge Adapter — QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1
Migrated to use Evidence SDK (QA-PILOT-SDK-INTEGRATION-1) instead of direct
filesystem scraping.

Governed read-only bridge for consuming Librarian canonical knowledge.
Discovers, queries, references, and produces provenance records for
Librarian source documents. Uses the governed Evidence SDK instead of
direct libraian path access.

Commands:
    scan              — Discover all available Librarian sources (via SDK)
    query <pattern>   — Search sources by path pattern or type (via SDK)
    reference <path>  — Create a structured source reference for a file
    provenance <refs> — Create a provenance record linking multiple sources
    verify <ref..>    — Verify that referenced sources are still accessible
    status            — Show adapter configuration and state

Authority: advisory-only. No cross-project write authority.
"""

import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Import the governed Evidence SDK for all Librarian evidence access
SDK_AVAILABLE = False
try:
    from qa_pilot_evidence_sdk import EvidenceProvider, SDK_VERSION
    SDK_AVAILABLE = True
except ImportError:
    EvidenceProvider = None
    SDK_VERSION = "unavailable"

# Paths to Librarian source directories (resolved relative to CarbideFrame workspace)
CARBIDE_WORKSPACE = REPO_ROOT.parent.parent  # CarbideFrame root
LIBRARIAN_ROOT = CARBIDE_WORKSPACE / "active" / "librarian"

ADAPTER_VERSION = "knowledge-adapter-v1"
KNOWN_SOURCE_TYPES = {
    "governance": LIBRARIAN_ROOT / "docs" / "governance",
    "schema": LIBRARIAN_ROOT / "docs" / "schemas",
    "rule": LIBRARIAN_ROOT / "docs" / "rules",
    "ledger": LIBRARIAN_ROOT / "project-state" / "sprint-ledger.json",
    "receipt": LIBRARIAN_ROOT / "receipts" / "decision-resolutions",
}

VALIDATOR_SCRIPT = SCRIPT_DIR / "validate-qa-pilot-knowledge-adapter.py"
SCHEMA_FILE = REPO_ROOT / "docs" / "schemas" / "qa-pilot-knowledge-adapter.schema.json"


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path):
    """Compute SHA-256 hash of file content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_revision(path):
    """Get git revision for a file path."""
    try:
        result = os.popen(f"cd {LIBRARIAN_ROOT} && git log -1 --format=%h -- {path} 2>/dev/null").read().strip()
        return result if result else "unknown"
    except Exception:
        return "unknown"


def make_source_reference(path_str, source_type):
    """Create a structured source reference for a file relative to Librarian root."""
    full_path = LIBRARIAN_ROOT / path_str
    if not full_path.exists():
        return {
            "path": path_str,
            "revision": "unknown",
            "source_type": source_type,
            "accessible": False,
            "title": path_str.split("/")[-1],
            "content_hash": None,
            "last_modified": None,
            "referenced_at": now_utc(),
        }

    revision = get_git_revision(path_str)
    content_hash = sha256_file(full_path)
    mtime = datetime.datetime.fromtimestamp(full_path.stat().st_mtime, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Extract title from first line of markdown files
    title = path_str.split("/")[-1]
    if path_str.endswith(".md"):
        try:
            with open(full_path) as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    title = first_line[2:]
        except Exception:
            pass

    return {
        "path": path_str,
        "revision": revision,
        "source_type": source_type,
        "accessible": True,
        "title": title,
        "content_hash": content_hash,
        "last_modified": mtime,
        "referenced_at": now_utc(),
    }


def compute_source_hash(sources):
    """Compute SHA-256 hash over concatenated source content."""
    h = hashlib.sha256()
    for src in sources:
        path_str = src.get("path", "")
        full_path = LIBRARIAN_ROOT / path_str
        if full_path.exists():
            try:
                h.update(full_path.read_bytes())
            except Exception:
                h.update(path_str.encode())
        h.update(src.get("revision", "unknown").encode())
        h.update(src.get("source_type", "unknown").encode())
    return h.hexdigest()


# ── Commands ─────────────────────────────────────────────────────────

def cmd_scan(args):
    """Scan all known Librarian source directories.
    
    Primary data source: Evidence SDK. Falls back to filesystem scan
    when SDK is unavailable or evidence plane data is not present.
    """
    # Try SDK first
    if SDK_AVAILABLE:
        try:
            provider = EvidenceProvider()
            snapshot = provider.getEvidenceSnapshot()
            provenance = provider.getProvenanceChain()
            
            if snapshot.get("data", {}).get("evidence_available"):
                sdk_data = snapshot["data"]
                prov_data = provenance.get("data", {})
                
                # Build source list from SDK provenance records
                sdk_sources = []
                records = prov_data.get("provenance_records", [])
                for rec in records:
                    source_path = rec.get("source_path") or ""
                    source_type = "governance"
                    cat = rec.get("category", "").lower()
                    if "schema" in cat:
                        source_type = "schema"
                    elif "runtime" in cat or "source" in cat:
                        source_type = "rule"
                    elif "lifecycle" in cat:
                        source_type = "ledger"
                    
                    sdk_sources.append({
                        "path": source_path,
                        "source_type": source_type,
                        "revision": "sdk_snapshot",
                        "accessible": rec.get("evidence_status") != "ABSENT",
                        "title": rec.get("source_id", "unknown"),
                        "content_hash": None,
                        "last_modified": rec.get("last_reconciled_at"),
                        "referenced_at": now_utc(),
                        "evidence_status": rec.get("evidence_status"),
                        "governance_confidence": rec.get("governance_confidence"),
                        "age_hours": rec.get("age_hours"),
                    })
                
                output = {
                    "adapter_version": ADAPTER_VERSION,
                    "generated_at": now_utc(),
                    "operation": "scan",
                    "source": "evidence_sdk",
                    "sdk_version": SDK_VERSION,
                    "run_id": sdk_data.get("run_id"),
                    "result": {
                        "total_sources": len(sdk_sources),
                        "by_type": {},
                        "sources": sdk_sources,
                    },
                }
                
                counts = {}
                for r in sdk_sources:
                    t = r["source_type"]
                    counts[t] = counts.get(t, 0) + 1
                output["result"]["by_type"] = counts
                
                print(json.dumps(output, indent=2))
                return 0
        except Exception as e:
            # Fall through to filesystem scan
            pass
    
    # Fallback: filesystem scan (direct read)
    results = []

    for source_type, dir_path in KNOWN_SOURCE_TYPES.items():
        if dir_path.is_file():
            rel_path = str(dir_path.relative_to(LIBRARIAN_ROOT))
            ref = make_source_reference(rel_path, source_type)
            results.append(ref)
        elif dir_path.is_dir():
            for f in sorted(dir_path.rglob("*")):
                if f.is_file() and f.suffix in (".md", ".json"):
                    rel_path = str(f.relative_to(LIBRARIAN_ROOT))
                    ref = make_source_reference(rel_path, source_type)
                    results.append(ref)

    output = {
        "adapter_version": ADAPTER_VERSION,
        "generated_at": now_utc(),
        "operation": "scan",
        "source": "filesystem",
        "result": {
            "total_sources": len(results),
            "by_type": {},
            "sources": results,
        },
    }

    counts = {}
    for r in results:
        t = r["source_type"]
        counts[t] = counts.get(t, 0) + 1
    output["result"]["by_type"] = counts

    print(json.dumps(output, indent=2))
    return 0


def cmd_query(args):
    """Search sources by path pattern or type.
    
    Uses SDK findings/snapshot as primary source, falls back to filesystem.
    """
    pattern = " ".join(args) if args else ""
    results = []

    source_type_filter = "all"
    keyword_filter = None

    # Parse --type and --keyword flags
    clean_args = []
    i = 0
    while i < len(args):
        if args[i] == "--type" and i + 1 < len(args):
            source_type_filter = args[i + 1]
            i += 2
        elif args[i] == "--keyword" and i + 1 < len(args):
            keyword_filter = args[i + 1].lower()
            i += 2
        else:
            clean_args.append(args[i])
            i += 1

    pattern = " ".join(clean_args) if clean_args else ""

    # Try SDK query first
    if SDK_AVAILABLE and not keyword_filter and source_type_filter in ("all", "governance", "schema"):
        try:
            provider = EvidenceProvider()
            snapshot = provider.getEvidenceSnapshot()
            if snapshot.get("data", {}).get("evidence_available"):
                sdk_data = snapshot["data"]
                sources = sdk_data.get("sources", {})
                for source_key, source_val in sources.items():
                    sname_lower = source_key.lower()
                    if pattern and pattern.lower() not in sname_lower:
                        continue
                    results.append({
                        "path": source_val.get("source_path") or source_key,
                        "source_type": "governance",
                        "revision": None,
                        "accessible": source_val.get("evidence_status") != "ABSENT",
                        "title": source_key,
                        "content_hash": None,
                        "last_modified": source_val.get("last_reconciled_at"),
                        "referenced_at": now_utc(),
                    })
                
                output = {
                    "adapter_version": ADAPTER_VERSION,
                    "generated_at": now_utc(),
                    "operation": "query",
                    "source": "evidence_sdk",
                    "query": {
                        "pattern": pattern,
                        "source_type": source_type_filter,
                        "keyword": keyword_filter,
                    },
                    "result": {
                        "total_matches": len(results),
                        "sources": results[:50],
                    },
                }
                print(json.dumps(output, indent=2))
                return 0
        except Exception:
            pass

    # Fallback: filesystem query
    for source_type, dir_path in KNOWN_SOURCE_TYPES.items():
        if source_type_filter != "all" and source_type != source_type_filter:
            continue

        files_to_check = []
        if dir_path.is_file():
            files_to_check.append(dir_path)
        elif dir_path.is_dir():
            files_to_check.extend(sorted(dir_path.rglob("*")))

        for f in files_to_check:
            if not f.is_file() or f.suffix not in (".md", ".json"):
                continue
            rel_path = str(f.relative_to(LIBRARIAN_ROOT))
            fname_lower = f.name.lower()

            if pattern and pattern.lower() not in fname_lower:
                continue
            if keyword_filter:
                try:
                    content = f.read_text().lower()
                    if keyword_filter not in content:
                        continue
                except Exception:
                    continue

            ref = make_source_reference(rel_path, source_type)
            results.append(ref)

    output = {
        "adapter_version": ADAPTER_VERSION,
        "generated_at": now_utc(),
        "operation": "query",
        "source": "filesystem",
        "query": {
            "pattern": pattern,
            "source_type": source_type_filter,
            "keyword": keyword_filter,
            "limit": None,
        },
        "result": {
            "total_matches": len(results),
            "sources": results[:50],
        },
    }

    print(json.dumps(output, indent=2))
    return 0


def cmd_reference(args):
    """Create a structured source reference for a specific file."""
    if not args:
        print("Usage: knowledge_adapter.py reference <path> [<path> ...]")
        return 1

    results = []
    for path_arg in args:
        # Try exact path relative to Librarian root
        full_path = LIBRARIAN_ROOT / path_arg
        if full_path.exists() and full_path.is_file():
            # Determine source type by directory
            rel = full_path.relative_to(LIBRARIAN_ROOT)
            source_type = "governance"
            for st, sp in KNOWN_SOURCE_TYPES.items():
                if sp.is_dir() and str(sp) in str(full_path):
                    source_type = st
                    break
                elif sp.is_file() and full_path == sp:
                    source_type = st
                    break
            ref = make_source_reference(str(rel), source_type)
            results.append(ref)
        else:
            results.append({
                "path": path_arg,
                "revision": None,
                "source_type": "unknown",
                "accessible": False,
                "title": path_arg.split("/")[-1],
                "content_hash": None,
                "last_modified": None,
                "referenced_at": now_utc(),
            })

    output = {
        "adapter_version": ADAPTER_VERSION,
        "generated_at": now_utc(),
        "operation": "reference",
        "sources": results,
        "result": {
            "total_referenced": len(results),
            "accessible_count": sum(1 for r in results if r["accessible"]),
        },
    }

    print(json.dumps(output, indent=2))
    return 0


def cmd_provenance(args):
    """Create a provenance record linking multiple sources."""
    if not args:
        print("Usage: knowledge_adapter.py provenance <path> [<path> ...]")
        return 1

    # Create source references
    sources = []
    for path_arg in args:
        full_path = LIBRARIAN_ROOT / path_arg
        if full_path.exists() and full_path.is_file():
            rel = full_path.relative_to(LIBRARIAN_ROOT)
            source_type = "governance"
            for st, sp in KNOWN_SOURCE_TYPES.items():
                if sp.is_dir() and str(sp) in str(full_path):
                    source_type = st
                    break
                elif sp.is_file() and full_path == sp:
                    source_type = st
                    break
            ref = make_source_reference(str(rel), source_type)
            sources.append(ref)

    if not sources:
        print("ERROR: No accessible sources found", file=sys.stderr)
        return 1

    # Generate provenance ID
    ts = now_utc()
    hash_input = "|".join(s["path"] for s in sources) + ts
    prov_id = "KAP-" + hashlib.sha256(hash_input.encode()).hexdigest()[:12].upper()

    source_hash = compute_source_hash(sources)

    provenance_record = {
        "provenance_id": prov_id,
        "generated_at": ts,
        "sources": sources,
        "source_hash": source_hash,
        "advisory": True,
        "no_authority_promotion": True,
    }

    output = {
        "adapter_version": ADAPTER_VERSION,
        "generated_at": ts,
        "operation": "provenance",
        "sources": sources,
        "result": {
            "provenance": provenance_record,
            "source_count": len(sources),
        },
    }

    print(json.dumps(output, indent=2))
    return 0


def cmd_verify(args):
    """Verify that referenced sources are still accessible."""
    use_stdin = "--stdin" in args

    refs = []
    if use_stdin:
        try:
            data = json.load(sys.stdin)
            refs = data.get("sources", [])
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON on stdin", file=sys.stderr)
            return 1
    elif args:
        for path_arg in args:
            if path_arg in ("--stdin",):
                continue
            full_path = LIBRARIAN_ROOT / path_arg
            refs.append({
                "path": path_arg,
                "accessible": full_path.exists(),
            })

    if not refs:
        print("Usage: knowledge_adapter.py verify <path>... | --stdin")
        return 1

    results = []
    for ref in refs:
        path_str = ref.get("path", "")
        full_path = LIBRARIAN_ROOT / path_str
        existing = full_path.exists()

        content_hash = None
        revision = None
        if existing:
            content_hash = sha256_file(full_path)
            revision = get_git_revision(path_str)

        expected_hash = ref.get("content_hash")
        hash_match = expected_hash is None or content_hash == expected_hash

        results.append({
            "path": path_str,
            "accessible": existing,
            "hash_match": hash_match,
            "current_hash": content_hash,
            "expected_hash": expected_hash,
            "current_revision": revision,
            "verified_at": now_utc(),
        })

    all_accessible = all(r["accessible"] for r in results)
    all_hash_match = all(r["hash_match"] for r in results)

    output = {
        "adapter_version": ADAPTER_VERSION,
        "generated_at": now_utc(),
        "operation": "verify",
        "sources": results,
        "result": {
            "total_verified": len(results),
            "all_accessible": all_accessible,
            "all_hash_match": all_hash_match,
            "status": "verified" if (all_accessible and all_hash_match) else "degraded",
        },
    }

    print(json.dumps(output, indent=2))
    return 0 if (all_accessible and all_hash_match) else 2


def cmd_status(args):
    """Show adapter configuration and state."""
    librarian_exists = LIBRARIAN_ROOT.exists()

    type_counts = {}
    for source_type, dir_path in KNOWN_SOURCE_TYPES.items():
        if dir_path.is_dir():
            count = len([f for f in dir_path.rglob("*") if f.is_file() and f.suffix in (".md", ".json")])
        elif dir_path.is_file():
            count = 1
        else:
            count = 0
        type_counts[source_type] = {"path": str(dir_path), "files": count, "exists": dir_path.exists()}

    # Check SDK availability
    sdk_available = SDK_AVAILABLE
    sdk_evidence_available = False
    if sdk_available:
        try:
            provider = EvidenceProvider()
            snapshot = provider.getEvidenceSnapshot()
            sdk_evidence_available = snapshot.get("data", {}).get("evidence_available", False)
        except Exception:
            pass

    output = {
        "adapter_version": ADAPTER_VERSION,
        "generated_at": now_utc(),
        "operation": "status",
        "sdk_integration": {
            "sdk_available": sdk_available,
            "sdk_version": SDK_VERSION if sdk_available else "unavailable",
            "evidence_available_via_sdk": sdk_evidence_available,
            "primary_data_source": "sdk" if sdk_evidence_available else "filesystem",
        },
        "result": {
            "librarian_root": str(LIBRARIAN_ROOT),
            "librarian_accessible": librarian_exists,
            "source_types": type_counts,
            "total_source_files": sum(tc["files"] for tc in type_counts.values()),
            "authority": "advisory-only",
            "cross_project_write": "NOT AUTHORIZED",
            "read_only": True,
        },
    }

    print(json.dumps(output, indent=2))
    return 0


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("QA Pilot Librarian Knowledge Adapter — QA-PILOT-LIBRARIAN-KNOWLEDGE-ADAPTER-1")
        print()
        print("Usage:")
        print("  scan                        — Discover all available Librarian sources")
        print("  query <pattern>             — Search sources by path pattern")
        print("  query --type <type> <pat>   — Filter by source type (governance/schema/rule/ledger/receipt)")
        print("  query --keyword <kw> <pat>  — Filter by keyword in content")
        print("  reference <path>...         — Create structured source references")
        print("  provenance <path>...        — Create provenance record linking sources")
        print("  verify <path>...            — Verify source accessibility and hash")
        print("  verify --stdin              — Verify sources from JSON stdin")
        print("  status                      — Show adapter configuration")
        print()
        print("Authority: advisory-only. Read-only. No cross-project write.")
        if SDK_AVAILABLE:
            print(f"Data source: Evidence SDK ({SDK_VERSION}) — governed read-only queries")
            print("  Primary path: SDK query -> evidence plane -> Librarian contracts")
        else:
            print("All source reads go through: " + str(LIBRARIAN_ROOT))
            print("  SDK not available — using filesystem fallback path")
        return 0

    command = sys.argv[1]
    cmd_args = sys.argv[2:]

    commands = {
        "scan": cmd_scan,
        "query": cmd_query,
        "reference": cmd_reference,
        "provenance": cmd_provenance,
        "verify": cmd_verify,
        "status": cmd_status,
    }

    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Valid commands: {', '.join(commands.keys())}", file=sys.stderr)
        return 1

    return commands[command](cmd_args)


if __name__ == "__main__":
    sys.exit(main())
