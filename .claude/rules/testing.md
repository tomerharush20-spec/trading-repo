# Testing Requirements

## Coverage

- Minimum 80% overall
- 100% branch coverage for risk management and order execution code

Test types:
1. **Unit tests** - signals, indicators, risk checks, utilities
2. **Integration tests** - broker client against a fake/sandbox, data pipelines
3. **Backtests** - strategy on a fixed historical dataset with a known, checked result

## Test-Driven Development

Mandatory workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage

## Rules

- Never hit a live broker or paid data API from tests
- Fixed seeds and fixture data; tests must be reproducible
- Fix the implementation, not the test (unless the test is wrong)

## Troubleshooting Test Failures

1. Use the **tdd-guide** agent
2. Check test isolation (shared state, global config, time)
3. Verify mocks match the real API's behavior
