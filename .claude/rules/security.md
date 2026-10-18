# Security Guidelines

## Mandatory Security Checks

Before ANY commit:
- [ ] No hardcoded secrets (broker API keys, tokens, passwords, account IDs)
- [ ] `.env` and credential files are git-ignored and not staged
- [ ] Secrets are never logged or included in exception messages
- [ ] All external input (market data, webhooks, config) validated
- [ ] SQL uses parameterized queries; no shell commands built from input
- [ ] Error messages don't leak sensitive data

## Secret Management

```python
# NEVER: Hardcoded secrets
API_KEY = "pk_live_xxxxx"

# ALWAYS: Environment variables, fail fast if missing
import os

API_KEY = os.environ.get("BROKER_API_KEY")
if not API_KEY:
    raise RuntimeError("BROKER_API_KEY not configured")
```

- Use separate keys for paper and live accounts
- Trading API keys must not have withdrawal/transfer permissions
- Prefer IP allow-listing on broker keys when supported

## Security Response Protocol

If a security issue is found:
1. STOP immediately
2. Use the **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets at the broker (deleting from git is not enough)
5. Review the entire codebase for similar issues
