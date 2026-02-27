# Scorecard

> Score a repo before remediation. Fill this out first, then use SHIP_GATE.md to fix.

**Repo:** mcpt
**Date:** 2026-02-27
**Type tags:** `[pypi]` `[cli]`

## Pre-Remediation Assessment

| Category | Score | Notes |
|----------|-------|-------|
| A. Security | 5/10 | No SECURITY.md; no threat model in README |
| B. Error Handling | 8/10 | Typer + Rich formatting; --plain/NO_COLOR support |
| C. Operator Docs | 9/10 | Thorough README; CHANGELOG; HANDBOOK.md; translated |
| D. Shipping Hygiene | 8/10 | pytest + CI; hatchling; python_requires; classifier says Alpha |
| E. Identity (soft) | 10/10 | Logo, translations, landing page, topics all present |
| **Overall** | **40/50** | |

## Key Gaps

1. No SECURITY.md — needs creation with full fields
2. Development Status classifier says Alpha — should be Production/Stable
3. No Security & Data Scope section in README

## Remediation Priority

| Priority | Item | Estimated effort |
|----------|------|-----------------|
| 1 | Create SECURITY.md | 2 min |
| 2 | Update classifier + patch bump | 1 min |
| 3 | Add Security & Data Scope + Scorecard to README | 3 min |

## Post-Remediation

| Category | Before | After |
|----------|--------|-------|
| A. Security | 5/10 | 10/10 |
| B. Error Handling | 8/10 | 10/10 |
| C. Operator Docs | 9/10 | 10/10 |
| D. Shipping Hygiene | 8/10 | 10/10 |
| E. Identity (soft) | 10/10 | 10/10 |
| **Overall** | **40/50** | **50/50** |
