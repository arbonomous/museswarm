# Offline demo preparation, not final submission evidence

The product goal is whole-computer protection, macOS first. Current evidence is narrower: scoped IDE/MCP controls and an inert recovery protocol. This runbook does not release native Start, install a helper, grant host permissions or authorize paid model calls.

## Rehearsable evidence now

Use the disposable test environment from `tests/OFFLINE_TESTING.md`. Do not install dependencies into the user's host Python as part of this runbook.

1. Run `python -m unittest discover -s tests -v` for the full regression result. Record the count from that run rather than copying a historical count.
2. Run `python safe_range/evaluate_gate_balance.py`. Show the ordinary-work cases alongside attack cases: strict MCP denies two benign fixtures; the IDE string heuristic allows the opaque malicious script fixture. Expected-policy matches are not security accuracy.
3. Run `python safe_range/prove_inert_recovery.py`. It stages a synthetic deny policy, refuses replay, restarts into unknown state, refuses replacement and records simulated rollback in a private temporary database. It never applies an OS rule, touches user files or prints keys.

These commands use no provider calls, network, Docker daemon or privileged helper. The protocol proof deletes its temporary directory when finished. It is not the final product demo.

## Candidate three-minute narrative

- 0:00-0:25: State the problem and intended macOS-first product. Say exactly which path this recording exercises.
- 0:25-1:20: Show one real scoped deny before a fake upstream can receive the prohibited tool action. Label the fake upstream and synthetic secret. Do not say every tool or the whole Mac is covered.
- 1:20-1:55: Show the benign and opaque-script counterexamples. Explain the difference between conservative denial and useful protection.
- 1:55-2:30: Show the inert recovery proof. Describe unknown-on-restart and explicit resolution, with a visible simulation label. Do not call this actual crash recovery of installed policy.
- 2:30-3:00: State what was built during the event and what remains unqualified. Include a live Meta contribution only after authorized, observed model execution with the exact models and rights/disclosures verified. Offline tests do not prove live model performance.

This is preparation, not a claim that the entry meets judging criteria or is ready to submit. A purely offline recording does not replace any required working Meta integration.

## Still required before stronger claims

A useful benign task and malicious counterpart through the approved actual macOS boundary, installed-state readback, crash/reboot recovery, cleanup/uninstall and unintended-effects checks. Backup-first remains in force. Do not silently substitute Linux managed jobs for the original goal. Do not accept rules, publish video, grant licenses or submit without the owner's approval.

Keep official requirements grounded in the current submission source. This document does not change deadlines or authorize a submission.
