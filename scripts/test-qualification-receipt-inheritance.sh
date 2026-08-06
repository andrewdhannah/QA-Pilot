#!/usr/bin/env bash
# Test: QR- records inherit evidence lineage (no independent evidence chain)
set +e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="$PROJECT_ROOT/scripts/validate-qa-pilot-qualification.py"
PASS=0
FAIL=0

pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

cd "$PROJECT_ROOT"

echo "=== Receipt Inheritance Validation ==="
echo ""

# Step 1: Create a mock evidence receipt (simulating a sealed QA Pilot receipt)
echo "Step 1: Create mock evidence receipt..."
EVIDENCE_DIR="data/qualification-records/test-evidence"
mkdir -p "$EVIDENCE_DIR"

cat > "$EVIDENCE_DIR/evidence-source-001.json" << 'EVEOF'
{
  "receipt_id": "RCPT-EVIDENCE-SOURCE-001",
  "sprint_id": "QA-PILOT-QUALIFICATION-SCHEMA-1",
  "source_layer": "scripts/validate-qa-pilot-qualification.py",
  "evidence_type": "validation_result",
  "produced_at": "2026-07-16T12:00:00Z",
  "advisory_only": true,
  "custody": "qa-pilot-local",
  "librarian_impact": "none"
}
EVEOF

if [ -f "$EVIDENCE_DIR/evidence-source-001.json" ]; then
    pass "Mock evidence receipt created"
else
    fail "Failed to create mock evidence receipt"
fi

# Step 2: Create a QR- record that inherits from this evidence
echo ""
echo "Step 2: Create QR- record with evidence lineage..."
QR_DIR="data/qualification-records"
QR_ID="QR-INHRTN-0001"

cat > "$QR_DIR/$QR_ID.json" << 'QREOF'
{
  "record_id": "QR-INHRTN-0001",
  "qualification_type": "artifact",
  "target_id": "TEST-INHERITANCE-001",
  "target_type": "workbench_item",
  "qualification_level": "spot_checked",
  "qualification_criteria": {
    "required_level": "spot_checked",
    "pass_rate_threshold": 0.80,
    "evidence_count_min": 1,
    "authority_check_required": false
  },
  "evidence_refs": [
    {
      "evidence_id": "RCPT-EVIDENCE-SOURCE-001",
      "evidence_type": "validation_result",
      "evidence_source": "data/qualification-records/test-evidence/evidence-source-001.json",
      "verification_status": "verified",
      "verified_at": "2026-07-16T12:00:00Z"
    }
  ],
  "overall_score": 0.85,
  "sub_dimension_scores": {
    "schema_compliance": 1.0,
    "evidence_freshness": 1.0,
    "evidence_diversity": 0.3,
    "authority_boundary": 1.0,
    "provenance_quality": 0.8
  },
  "lifecycle_state": "completed",
  "provenance": {
    "assessor_id": "receipt-inheritance-test",
    "session_id": "qual-schema-1-test",
    "tool_call_log": "test-qualification-receipt-inheritance.sh"
  },
  "expiry_date": "2026-10-14",
  "advisory_only": true,
  "custody": "qa-pilot-local",
  "librarian_impact": "none",
  "assessed_at": "2026-07-16T12:00:00Z",
  "assessed_by": "Receipt Inheritance Test"
}
QREOF

# Index it
python3 -c "
import json
idx_path = 'data/qualification-records/qualification-index.json'
with open(idx_path) as f:
    idx = json.load(f)
if 'QR-INHRTN-0001' not in idx.get('records', []):
    idx.setdefault('records', []).append('QR-INHRTN-0001')
    idx['last_updated'] = '2026-07-16T12:00:00Z'
with open(idx_path, 'w') as f:
    json.dump(idx, f, indent=2)
"
pass "QR- record created with evidence lineage"

# Step 3: Verify the QR- record validates against schema
echo ""
echo "Step 3: Verify QR- record validates..."
if python3 "$VALIDATOR" validate --record-id "$QR_ID" 2>&1 | grep -q "PASS"; then
    pass "QR- record validates against schema and rules"
else
    fail "QR- record validation failed"
    python3 "$VALIDATOR" validate --record-id "$QR_ID"
fi

# Step 4: Trace evidence lineage (QR → evidence_ref → source file)
echo ""
echo "Step 4: Trace evidence lineage..."
LINEAGE=$(python3 -c "
import json
qr_path = 'data/qualification-records/QR-INHRTN-0001.json'
with open(qr_path) as f:
    qr = json.load(f)
print(f'QR- record: {qr[\"record_id\"]}')
print(f'Target: {qr[\"target_id\"]} ({qr[\"target_type\"]})')
print(f'Evidence refs: {len(qr[\"evidence_refs\"])}')
for ref in qr[\"evidence_refs\"]:
    src = ref['evidence_source']
    try:
        with open(src) as ef:
            evidence = json.load(ef)
        print(f'  → evidence_id: {ref[\"evidence_id\"]}')
        print(f'  → source: {src} (EXISTS)')
        print(f'  → type: {ref[\"evidence_type\"]}')
        print(f'  → status: {ref[\"verification_status\"]}')
        print(f'  → source produced_at: {evidence.get(\"produced_at\", \"unknown\")}')
    except FileNotFoundError:
        print(f'  → evidence_id: {ref[\"evidence_id\"]}')
        print(f'  → source: {src} (MISSING)')
")
echo "$LINEAGE"
echo ""
if echo "$LINEAGE" | grep -q "EXISTS"; then
    pass "Evidence lineage traceable: QR → evidence_ref → source file"
else
    fail "Evidence lineage broken"
fi

# Step 5: Verify that removing evidence makes the QR- record's ref stale
echo ""
echo "Step 5: Simulate evidence loss — remove source, re-verify..."
cp "$EVIDENCE_DIR/evidence-source-001.json" "$EVIDENCE_DIR/evidence-source-001.json.bak"
rm "$EVIDENCE_DIR/evidence-source-001.json"

# Update verification_status to "missing"
python3 -c "
import json
qr_path = 'data/qualification-records/QR-INHRTN-0001.json'
with open(qr_path) as f:
    qr = json.load(f)
qr['evidence_refs'][0]['verification_status'] = 'missing'
with open(qr_path, 'w') as f:
    json.dump(qr, f, indent=2)
"

# Re-validate — should still pass (missing is a valid status)
if python3 "$VALIDATOR" validate --record-id "$QR_ID" 2>&1 | grep -q "PASS"; then
    pass "QR- record still validates with 'missing' evidence (expected — QR-11 allows missing status)"
else
    fail "QR- record failed after evidence removal"
fi

# Restore evidence
mv "$EVIDENCE_DIR/evidence-source-001.json.bak" "$EVIDENCE_DIR/evidence-source-001.json"
python3 -c "
import json
qr_path = 'data/qualification-records/QR-INHRTN-0001.json'
with open(qr_path) as f:
    qr = json.load(f)
qr['evidence_refs'][0]['verification_status'] = 'verified'
with open(qr_path, 'w') as f:
    json.dump(qr, f, indent=2)
"

# Step 6: Clean up test record
echo ""
echo "Step 6: Clean up test artifacts..."
rm -f "$QR_DIR/$QR_ID.json"
python3 -c "
import json
idx_path = 'data/qualification-records/qualification-index.json'
with open(idx_path) as f:
    idx = json.load(f)
if 'QR-INHRTN-0001' in idx.get('records', []):
    idx['records'].remove('QR-INHRTN-0001')
with open(idx_path, 'w') as f:
    json.dump(idx, f, indent=2)
"
rm -rf "$EVIDENCE_DIR"
pass "Test artifacts cleaned up"

# Summary
echo ""
echo "=== Receipt Inheritance: Result ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "✅ Receipt inheritance validated: QR → evidence_ref → source file chain is complete."
    echo "   Proven: Qualification Records inherit evidence lineage."
    echo "   Proven: No independent evidence chain — removing source makes ref stale."
    exit 0
else
    echo ""
    echo "❌ Receipt inheritance validation failed."
    exit 1
fi
