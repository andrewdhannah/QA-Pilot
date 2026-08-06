#!/usr/bin/env python3
"""
QA Pilot Startup Consistency Validator

Checks for contradictions between the generated STARTUP-STATE.md and the script's stdout.

Usage:
    python3 scripts/validate-qa-pilot-startup-consistency.py <startup_state_file> <stdout_file>
"""

import sys
import re
from pathlib import Path

def parse_startup_state(path):
    content = Path(path).read_text()
    
    # Parse operating mode
    mode_match = re.search(r"- \*\*Operating mode:\*\* (\w+)", content)
    mode = mode_match.group(1) if mode_match else None
    
    # Parse blockers
    blockers_match = re.search(r"- \*\*Blockers:\*\* (.*)", content)
    blockers = blockers_match.group(1).strip() if blockers_match else None
    
    # Parse required files
    required_files = []
    # Find the "## Required Files" section and read until the next section
    section_match = re.search(r"## Required Files\n\n(.*?)\n\n##", content, re.DOTALL)
    if section_match:
        lines = section_match.group(1).strip().split('\n')
        for line in lines:
            if "✅" in line:
                filename = line.replace("- ✅", "").strip()
                required_files.append({"file": filename, "status": "present"})
            elif "❌" in line:
                filename = line.replace("- ❌", "").strip().replace(" (MISSING)", "")
                required_files.append({"file": filename, "status": "missing"})
                
    return {
        "mode": mode,
        "blockers": blockers,
        "required_files": required_files
    }

def parse_stdout(path):
    content = Path(path).read_text()
    
    # Parse operating mode
    mode_match = re.search(r"Operating mode: (\w+)", content)
    mode = mode_match.group(1) if mode_match else None
    
    # Parse blockers
    blockers_match = re.search(r"Blockers: (.*)", content)
    blockers = blockers_match.group(1).strip() if blockers_match else None
    
    # Parse missing files from stderr/stdout
    missing_files = []
    for line in content.split('\n'):
        if "MISSING:" in line:
            # Extract filename from "MISSING: /path/to/file"
            filename = line.split("MISSING:")[1].strip()
            # Get just the filename
            filename = filename.split('/')[-1]
            missing_files.append(filename)
            
    return {
        "mode": mode,
        "blockers": blockers,
        "missing_files": missing_files
    }

def validate(state, stdout):
    errors = []
    
    # 1. Check operating mode consistency
    if state["mode"] != stdout["mode"]:
        errors.append(f"Operating mode mismatch: STARTUP-STATE.md says '{state['mode']}', stdout says '{stdout['mode']}'")
        
    # 2. Check blocker count consistency
    # If state says "none detected", stdout should not have any "MISSING:" lines
    if state["blockers"] == "none detected":
        if stdout["missing_files"]:
            errors.append(f"Blocker mismatch: STARTUP-STATE.md says 'none detected', but stdout reports missing files: {stdout['missing_files']}")
    else:
        # If state has blockers, stdout should have missing files (or MCP issues)
        # This is a bit complex because blockers can be MCP issues too.
        # For now, let's just check if the number of missing files matches the blocker count if it's a file issue.
        if "required project files missing" in state["blockers"]:
            # We need to count how many files are marked as missing in the state
            missing_in_state = [f["file"] for f in state["required_files"] if f["status"] == "missing"]
            if len(missing_in_state) != len(stdout["missing_files"]):
                errors.append(f"Missing file count mismatch: STARTUP-STATE.md reports {len(missing_in_state)} missing, stdout reports {len(stdout['missing_files'])}")
            
            # Check if the files match
            for m_file in stdout["missing_files"]:
                if m_file not in missing_in_state:
                    errors.append(f"Missing file mismatch: stdout reports '{m_file}' is missing, but STARTUP-STATE.md says it is present")
            for s_file in missing_in_state:
                if s_file not in stdout["missing_files"]:
                    errors.append(f"Missing file mismatch: STARTUP-STATE.md reports '{s_file}' is missing, but stdout does not report it")

    # 3. Check required files table consistency
    for req in state["required_files"]:
        print(f"DEBUG: Checking {req['file']} (status: {req['status']}) against missing_files: {stdout['missing_files']}")
        if req["status"] == "present" and req["file"] in stdout["missing_files"]:
            errors.append(f"File status mismatch: {req['file']} is marked present in STARTUP-STATE.md but reported missing in stdout")
        if req["status"] == "missing" and req["file"] not in stdout["missing_files"]:
            errors.append(f"File status mismatch: {req['file']} is marked missing in STARTUP-STATE.md but not reported missing in stdout")


    return errors

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 validate-qa-pilot-startup-consistency.py <startup_state_file> <stdout_file>")
        sys.exit(1)
        
    state_path = sys.argv[1]
    stdout_path = sys.argv[2]
    
    try:
        state = parse_startup_state(state_path)
        stdout = parse_stdout(stdout_path)
    except Exception as e:
        print(f"ERROR: Failed to parse files: {e}")
        sys.exit(1)
        
    errors = validate(state, stdout)
    
    if errors:
        print("❌ STARTUP CONSISTENCY VIOLATION DETECTED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ STARTUP CONSISTENCY VERIFIED")
        sys.exit(0)

if __name__ == "__main__":
    main()
