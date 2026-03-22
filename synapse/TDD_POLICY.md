# A.I.M. Test-Driven Development (TDD) Policy

## 1. THE MANDATE
Every functional change, bug fix, or new feature **MUST** be governed by the TDD lifecycle. No code enters the `src/` directory without a corresponding verification script. Verification is not just "running code"; it is the empirical proof of correctness.

## 2. THE LIFECYCLE (RED-GREEN-REFACTOR)
1.  **RED (Reproduction):** Create a reproduction script or unit test that fails. This defines the "Current Broken State."
2.  **GREEN (Fix):** Apply the minimal surgical code change required to make the test pass.
3.  **REFACTOR (Polish):** Clean up the implementation for idiomatic quality and performance while ensuring the test remains green.

## 3. VERIFICATION STANDARDS
- **Unit Tests:** Preferred for utility functions and logic-heavy modules (using `pytest` or `unittest`).
- **Reproduction Scripts:** Mandatory for bug fixes. Prove the bug exists, then prove it's gone.
- **Protocol Isolation (Phase 19):** For MCP and cross-tool features, use mock clients to verify interface compliance without environmental bloat.
- **Zero-Token Validation:** Tests must be fast and autonomous. Avoid external API calls during testing unless the API itself is the target.

## 4. ARCHITECTURAL TRACE
- **Librarian Requirement:** Every session summary must explicitly identify the TDD stages completed.
- **Retriever Priority:** This document is indexed as a `foundation_knowledge` mandate and ranks above general technical documentation.

---
"I believe I've made my point." — **A.I.M.**
