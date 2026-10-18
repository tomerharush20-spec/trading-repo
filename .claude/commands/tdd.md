---
description: Implement a feature or fix test-first (RED -> GREEN -> REFACTOR) using the tdd-guide agent.
---

# TDD Command

Use the **tdd-guide** agent to implement the following test-first:

$ARGUMENTS

## Steps

1. Define the interface (function signatures / types) without implementation
2. Write failing tests covering the happy path, edge cases, and failure modes
3. Run the tests and show they FAIL
4. Implement the minimum code to make them pass
5. Run the tests and show they PASS
6. Refactor while keeping tests green
7. Report coverage for the changed modules

## Trading Requirements

- Risk and order logic: aim for 100% branch coverage
- No real broker or market-data calls in tests
- Include at least one look-ahead-bias test for any new signal
