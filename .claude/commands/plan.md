---
description: Restate requirements, assess risks, and create step-by-step implementation plan. WAIT for user CONFIRM before touching any code.
---

# Plan Command

Use the **planner** agent to create a comprehensive implementation plan before writing any code.

Request: $ARGUMENTS

## What This Command Does

1. **Restate Requirements** - Clarify what needs to be built
2. **Identify Risks** - Surface potential issues and blockers, including trading risks (see planner's trading checks)
3. **Create Step Plan** - Break down implementation into phases
4. **Wait for Confirmation** - MUST receive user approval before proceeding

## When to Use

- Starting a new feature or strategy
- Changes to risk management, order execution, or broker integration
- Significant architectural changes or complex refactoring
- Requirements are unclear or ambiguous

## Output

Follow the planner agent's plan format. End with:

**WAITING FOR CONFIRMATION**: Proceed with this plan? (yes/no/modify)

## Important

Do **NOT** write any code until the user explicitly confirms the plan.

## Next Steps

After the plan is approved:
- `/tdd` to implement test-first
- `/verify` to run quality gates
- `/trade-review` to review the completed change
