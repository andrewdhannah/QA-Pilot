#!/usr/bin/env python3
"""
QA-Pilot MCP/API Interaction Capability

Read-only MCP client for testing MCP-based services.
Captures request/response provenance.
Makes MCP failures distinguishable from test failures.

Usage:
    # Health check
    python3 scripts/mcp-capability.py --health

    # Call a tool
    python3 scripts/mcp-capability.py --tool project_get_profile --args '{"project_id": "librarian"}'

    # List available tools
    python3 scripts/mcp-capability.py --list-tools

Configuration:
    Set QA_PILOT_MCP_TARGET to override default MCP endpoint.
    Default: http://127.0.0.1:3456/mcp
"""

import argparse
import json
import os
import sys
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
DEFAULT_MCP_TARGET = "http://127.0.0.1:3456/mcp"
DEFAULT_HEALTH_ENDPOINT = "http://127.0.0.1:3456/api/health"
MCP_TARGET = os.environ.get("QA_PILOT_MCP_TARGET", DEFAULT_MCP_TARGET)
MCP_HEALTH = os.environ.get("QA_PILOT_MCP_HEALTH", DEFAULT_HEALTH_ENDPOINT)

# ── Error Taxonomy ─────────────────────────────────────────────────────────
# MCP failures are distinguishable from test failures via this taxonomy.

class MCPError:
    """MCP error taxonomy — distinguishes MCP infrastructure failures from test failures."""
    
    # Infrastructure errors (MCP service not reachable, malformed response, etc.)
    INFRA_UNREACHABLE = "MCP_INFRA_UNREACHABLE"
    INFRA_MALFORMED_RESPONSE = "MCP_INFRA_MALFORMED_RESPONSE"
    INFRA_TIMEOUT = "MCP_INFRA_TIMEOUT"
    INFRA_AUTH_FAILURE = "MCP_INFRA_AUTH_FAILURE"
    
    # Protocol errors (tool not found, invalid arguments, etc.)
    PROTO_TOOL_NOT_FOUND = "MCP_PROTO_TOOL_NOT_FOUND"
    PROTO_INVALID_ARGUMENTS = "MCP_PROTO_INVALID_ARGUMENTS"
    PROTO_UNKNOWN_CAPABILITY = "MCP_PROTO_UNKNOWN_CAPABILITY"
    
    # Application errors (tool executed but returned error)
    APP_TOOL_ERROR = "MCP_APP_TOOL_ERROR"
    APP_VALIDATION_ERROR = "MCP_APP_VALIDATION_ERROR"
    
    # No error
    NONE = "MCP_NONE"
    
    @staticmethod
    def classify(error):
        """Classify an error into the taxonomy."""
        if error is None:
            return MCPError.NONE
        
        error_str = str(error).lower()
        
        # Infrastructure
        if "connection refused" in error_str or "unreachable" in error_str:
            return MCPError.INFRA_UNREACHABLE
        if "timeout" in error_str:
            return MCPError.INFRA_TIMEOUT
        if "auth" in error_str or "unauthorized" in error_str:
            return MCPError.INFRA_AUTH_FAILURE
        if "json" in error_str or "parse" in error_str or "malformed" in error_str:
            return MCPError.INFRA_MALFORMED_RESPONSE
        
        # Protocol
        if "tool not found" in error_str or "unknown tool" in error_str:
            return MCPError.PROTO_TOOL_NOT_FOUND
        if "invalid argument" in error_str or "missing argument" in error_str:
            return MCPError.PROTO_INVALID_ARGUMENTS
        if "unknown capability" in error_str:
            return MCPError.PROTO_UNKNOWN_CAPABILITY
        
        # Application
        if "validation" in error_str:
            return MCPError.APP_VALIDATION_ERROR
        if "error" in error_str:
            return MCPError.APP_TOOL_ERROR
        
        return MCPError.APP_TOOL_ERROR


# ── Provenance Capture ─────────────────────────────────────────────────────

class MCPProvenance:
    """Captures request/response provenance for MCP interactions."""
    
    def __init__(self):
        self.entries = []
    
    def record(self, tool, args, response, error, duration_ms):
        """Record a single MCP interaction."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool,
            "args": args,
            "response_hash": hashlib.sha256(json.dumps(response, sort_keys=True).encode()).hexdigest() if response else None,
            "error": error,
            "error_class": MCPError.classify(error),
            "duration_ms": duration_ms,
            "mcp_target": MCP_TARGET,
        }
        self.entries.append(entry)
        return entry
    
    def to_json(self):
        return json.dumps(self.entries, indent=2)


# ── MCP Client ─────────────────────────────────────────────────────────────

def check_health():
    """Check MCP service health. Returns (healthy, details)."""
    import urllib.request
    import urllib.error
    
    try:
        req = urllib.request.Request(MCP_HEALTH, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return True, data
    except urllib.error.URLError as e:
        return False, {"error": str(e), "error_class": MCPError.classify(e)}
    except Exception as e:
        return False, {"error": str(e), "error_class": MCPError.classify(e)}


def call_tool(tool_name, args=None):
    """Call an MCP tool via JSON-RPC. Returns (result, error, duration_ms)."""
    import urllib.request
    import urllib.error
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args or {}
        }
    }
    
    start = time.monotonic()
    try:
        req = urllib.request.Request(
            MCP_TARGET,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            duration_ms = (time.monotonic() - start) * 1000
            
            if "error" in data:
                return None, data["error"], duration_ms
            return data.get("result"), None, duration_ms
    except urllib.error.URLError as e:
        duration_ms = (time.monotonic() - start) * 1000
        return None, str(e), duration_ms
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        return None, str(e), duration_ms


def list_tools():
    """List available MCP tools. Returns (tools, error)."""
    import urllib.request
    import urllib.error
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        req = urllib.request.Request(
            MCP_TARGET,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if "error" in data:
                return None, data["error"]
            return data.get("result", {}).get("tools", []), None
    except Exception as e:
        return None, str(e)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="QA-Pilot MCP/API Interaction Capability")
    parser.add_argument("--health", action="store_true", help="Check MCP service health")
    parser.add_argument("--tool", type=str, help="Call an MCP tool")
    parser.add_argument("--args", type=str, default="{}", help="JSON arguments for the tool")
    parser.add_argument("--list-tools", action="store_true", help="List available MCP tools")
    parser.add_argument("--target", type=str, help="Override MCP target URL")
    parser.add_argument("--provenance-file", type=str, help="Write provenance log to file")
    
    args = parser.parse_args()
    
    if args.target:
        global MCP_TARGET
        MCP_TARGET = args.target
    
    provenance = MCPProvenance()
    
    if args.health:
        healthy, details = check_health()
        result = {
            "healthy": healthy,
            "target": MCP_HEALTH,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if healthy else 1)
    
    if args.list_tools:
        tools, error = list_tools()
        if error:
            result = {
                "error": error,
                "error_class": MCPError.classify(error),
                "target": MCP_TARGET,
            }
            print(json.dumps(result, indent=2))
            sys.exit(1)
        result = {
            "tools": tools,
            "count": len(tools),
            "target": MCP_TARGET,
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    if args.tool:
        try:
            tool_args = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "error": f"Invalid JSON args: {e}",
                "error_class": MCPError.PROTO_INVALID_ARGUMENTS,
            }, indent=2))
            sys.exit(1)
        
        result, error, duration_ms = call_tool(args.tool, tool_args)
        provenance.record(args.tool, tool_args, result, error, duration_ms)
        
        output = {
            "tool": args.tool,
            "args": tool_args,
            "result": result,
            "error": error,
            "error_class": MCPError.classify(error),
            "duration_ms": duration_ms,
            "target": MCP_TARGET,
            "provenance": provenance.entries[-1] if provenance.entries else None,
        }
        
        print(json.dumps(output, indent=2))
        
        if args.provenance_file:
            with open(args.provenance_file, "w") as f:
                json.dump(provenance.entries, f, indent=2)
        
        sys.exit(0 if error is None else 1)
    
    # No action specified
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
