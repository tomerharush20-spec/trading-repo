# Coding Style

## Immutability

Prefer creating new objects over mutating shared state, especially for positions, orders, and config passed between components.

## File Organization

Many small files over few large files:
- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Organize by domain (e.g. `data/`, `strategies/`, `risk/`, `execution/`, `backtest/`)

## Error Handling

- Handle errors explicitly; never silently swallow exceptions
- Broker/network calls: timeouts, bounded retries with backoff, idempotent retries only
- Fail safe: on unexpected errors in execution code, stop placing orders rather than continue

## Money and Time

- Use `Decimal` (or integer ticks/cents) for prices and quantities where rounding matters
- Round to the instrument's tick size and lot size explicitly
- Use timezone-aware datetimes (UTC internally); respect exchange calendars and sessions

## Input Validation

Validate all external data (prices, signals, config) at the boundary, e.g. with pydantic or zod.

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Proper error handling
- [ ] No leftover debug prints
- [ ] No unexplained magic numbers (thresholds, sizes go in config)
