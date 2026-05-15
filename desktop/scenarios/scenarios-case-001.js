// Ensure the registry exists — safe to call even if another scenario file
// already created it. Each scenario file is responsible for its own safety.
window.SCENARIOS = window.SCENARIOS || {};

window.SCENARIOS["case-001"] = {
  id: "case-001",
  type: "case",
  title: "Customer unable to complete online payment",
  priority: "Medium",
  summary: "Customer reports that payment fails at final confirmation step.",
  linkedBug: "bug-001",

  acceptanceCriteriaGlobal: [
    "Case contains customer impact description.",
    "Case is linked to the correct ADO bug.",
  ],

  acceptanceCriteriaScenario: [
    "Case status is Escalated when payment fails.",
    "Resolution notes reference the ADO bug ID.",
  ],
};
