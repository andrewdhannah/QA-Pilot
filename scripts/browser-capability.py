#!/usr/bin/env python3
"""
QA-Pilot Browser Interaction Capability

Playwright-based browser client for testing web applications.
Captures request/response provenance.
Makes browser failures distinguishable from test failures.

Usage:
    # Health check (verify Playwright is available)
    python3 scripts/browser-capability.py --health

    # Navigate to a URL
    python3 scripts/browser-capability.py --navigate http://localhost:8080

    # Execute JavaScript
    python3 scripts/browser-capability.py --eval "document.title"

    # Take screenshot
    python3 scripts/browser-capability.py --screenshot /tmp/screenshot.png

    # Run a test suite
    python3 scripts/browser-capability.py --test-suite path/to/suite.json

Configuration:
    Set QA_PILOT_BROWSER_TARGET to override default target URL.
    Default: http://localhost:8080
"""

import argparse
import json
import os
import sys
import time
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BROWSER_TARGET = "http://localhost:8080"
BROWSER_TARGET = os.environ.get("QA_PILOT_BROWSER_TARGET", DEFAULT_BROWSER_TARGET)


class BrowserError:
    """Browser error taxonomy — distinguishes infrastructure failures from test failures."""

    INFRA_UNREACHABLE = "BROWSER_INFRA_UNREACHABLE"
    INFRA_TIMEOUT = "BROWSER_INFRA_TIMEOUT"
    INFRA_NAVIGATION_FAILED = "BROWSER_INFRA_NAVIGATION_FAILED"
    INFRA_JS_ERROR = "BROWSER_INFRA_JS_ERROR"
    APP_ELEMENT_NOT_FOUND = "BROWSER_APP_ELEMENT_NOT_FOUND"
    APP_ASSERTION_FAILED = "BROWSER_APP_ASSERTION_FAILED"
    NONE = "BROWSER_NONE"

    @staticmethod
    def classify(error):
        if error is None:
            return BrowserError.NONE
        error_str = str(error).lower()
        if "timeout" in error_str:
            return BrowserError.INFRA_TIMEOUT
        if "navigation" in error_str or "net::err" in error_str:
            return BrowserError.INFRA_NAVIGATION_FAILED
        if "referenceerror" in error_str or "syntaxerror" in error_str:
            return BrowserError.INFRA_JS_ERROR
        if "element" in error_str or "selector" in error_str:
            return BrowserError.APP_ELEMENT_NOT_FOUND
        if "assert" in error_str:
            return BrowserError.APP_ASSERTION_FAILED
        return BrowserError.INFRA_UNREACHABLE


class BrowserProvenance:
    """Captures request/response provenance for browser interactions."""

    def __init__(self):
        self.entries = []

    def record(self, action, target, result, error, duration_ms):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "target": target,
            "result_hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest() if result else None,
            "error": error,
            "error_class": BrowserError.classify(error),
            "duration_ms": duration_ms,
            "browser_target": BROWSER_TARGET,
        }
        self.entries.append(entry)
        return entry

    def to_json(self):
        return json.dumps(self.entries, indent=2)


def check_health():
    """Check if Playwright is available and browser can be launched."""
    try:
        result = subprocess.run(
            ["npx", "playwright", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, {"playwright_version": version, "status": "ok"}
        return False, {"error": result.stderr, "status": "failed"}
    except Exception as e:
        return False, {"error": str(e), "status": "failed"}


def run_playwright_script(script_content, timeout=30):
    """Run a Playwright script and return (result, error, duration_ms)."""
    start = time.monotonic()
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script_content)
            f.flush()
            script_path = f.name

        result = subprocess.run(
            ["npx", "playwright", "test", "--config=-", script_path],
            capture_output=True, text=True, timeout=timeout
        )
        duration_ms = (time.monotonic() - start) * 1000

        os.unlink(script_path)

        if result.returncode == 0:
            return {"output": result.stdout}, None, duration_ms
        else:
            return None, result.stderr or result.stdout, duration_ms
    except subprocess.TimeoutExpired:
        duration_ms = (time.monotonic() - start) * 1000
        return None, "Timeout", duration_ms
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        return None, str(e), duration_ms


def navigate_and_eval(url, script="document.title"):
    """Navigate to URL and evaluate a JavaScript expression."""
    import tempfile
    js_script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
    const browser = await chromium.launch({{ headless: true }});
    const page = await browser.newPage();
    await page.goto('{url}');
    const result = await page.evaluate(() => {script});
    console.log(JSON.stringify({{ result, url: page.url(), title: await page.title() }}));
    await browser.close();
}})();
"""
    start = time.monotonic()
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_script)
            f.flush()
            script_path = f.name

        result = subprocess.run(
            ["node", script_path],
            capture_output=True, text=True, timeout=30
        )
        duration_ms = (time.monotonic() - start) * 1000
        os.unlink(script_path)

        if result.returncode == 0:
            try:
                output = json.loads(result.stdout.strip().split('\n')[-1])
                return output, None, duration_ms
            except:
                return {"raw": result.stdout}, None, duration_ms
        else:
            return None, result.stderr, duration_ms
    except subprocess.TimeoutExpired:
        return None, "Timeout", (time.monotonic() - start) * 1000
    except Exception as e:
        return None, str(e), (time.monotonic() - start) * 1000


def main():
    parser = argparse.ArgumentParser(description="QA-Pilot Browser Interaction Capability")
    parser.add_argument("--health", action="store_true", help="Check Playwright availability")
    parser.add_argument("--navigate", type=str, help="Navigate to URL and return page info")
    parser.add_argument("--eval", type=str, help="JavaScript expression to evaluate")
    parser.add_argument("--target", type=str, help="Override browser target URL")
    parser.add_argument("--provenance-file", type=str, help="Write provenance log to file")

    args = parser.parse_args()

    if args.target:
        global BROWSER_TARGET
        BROWSER_TARGET = args.target

    provenance = BrowserProvenance()

    if args.health:
        healthy, details = check_health()
        result = {
            "healthy": healthy,
            "target": BROWSER_TARGET,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if healthy else 1)

    if args.navigate:
        script = args.eval or "document.title"
        output, error, duration_ms = navigate_and_eval(args.navigate, script)
        provenance.record("navigate", args.navigate, output, error, duration_ms)

        result = {
            "action": "navigate",
            "url": args.navigate,
            "result": output,
            "error": error,
            "error_class": BrowserError.classify(error),
            "duration_ms": duration_ms,
            "target": BROWSER_TARGET,
        }
        print(json.dumps(result, indent=2))

        if args.provenance_file:
            with open(args.provenance_file, "w") as f:
                json.dump(provenance.entries, f, indent=2)

        sys.exit(0 if error is None else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
