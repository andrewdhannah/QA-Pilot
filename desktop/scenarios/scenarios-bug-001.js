// Ensure the registry exists — safe to call even if another scenario file
// already created it. Each scenario file is responsible for its own safety.
window.SCENARIOS = window.SCENARIOS || {};

window.SCENARIOS["bug-001"] = {
  id: "bug-001",
  type: "bug",
  title: "[Payments] Checkout fails at confirmation step",
  severity: "2 - High",
  reproSteps: [
    "Sign in as a customer",
    "Add items to cart",
    "Proceed to checkout",
    "Enter valid payment details",
    "Click 'Confirm and Pay'",
  ],
  linkedCase: "case-001",

  acceptanceCriteriaGlobal: [
    "Bug title clearly describes the failure.",
    "Repro steps are complete and deterministic.",
  ],

  acceptanceCriteriaScenario: [
    "Bug references the correct environment and build.",
    "Expected vs actual behaviour is clearly documented.",
  ],
};
