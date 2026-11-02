# Inert helper/controller protocol

Status: source-only prototype, not released. Nothing on the Mac is protected by this module.

`helper_protocol.py` now connects a controller-side message encoder, strict deny-rule compiler and durable state receiver in one executable offline path. It is a new implementation, not a recovered or integrated copy of the earlier standalone prototype. It is intentionally disconnected from all app launchers, native Start, Santa and privileged services.

## Implemented

- Bounded, exact-schema messages with version, session epoch, increasing sequence, short expiry, operation and body covered by an injected-key HMAC. Duplicate JSON keys, malformed messages, invalid types, mutations and replay are refused.
- A narrow compiler accepts only explicit lowercase binary SHA256 deny rules. No path, certificate, allow, delete or arbitrary-command interface exists.
- SQLite transactions persist consumed sequences and state changes before returning a result. Semantic refusals consume their sequence. Concurrent duplicates have one winner.
- One unresolved policy at a time. Stage binds a deterministic policy digest and expiry. Begin records simulation intent; only a separate acknowledgement can record simulated application. Cancellation cannot erase an active intent.
- A new receiver fences older instances, invalidates staged work and marks interrupted or previously simulated application unknown. Unknown state blocks replacement until explicit simulated rollback.
- A transactional hash-linked simulation journal records exact transition identities, sequence/epoch, refusals and restart recovery without command bodies, keys or arbitrary error text. Journal failure rolls back the transition and sequence together; accidental interior edits/gaps refuse further transitions. This is not a signed audit log: malicious rewriting, tail truncation or database replacement is not detected without an independent anchor.
- Database failure raises rather than claiming completion. There is no automatic retry, dispatcher or OS adapter.

## What this does not establish

HMAC proves possession of an injected test key, not the caller's macOS identity or the user's approval. A same-user attacker can read or change test state. The caller-provided private temporary directory is not a qualified privileged filesystem boundary. Epoch fencing does not recover actual OS rules. Simulated rollback changes only a database row.

A signed message alone must never authorize privileged work. No real key distribution, audit-token/code-signing verification, authenticated local IPC, Santa transport, installed-rule readback, OS event handling, reboot recovery, uninstall, egress enforcement or privileged helper installation exists here. Whole-computer protection remains unproven. `NATIVE_LIVE_RELEASED=False` and existing runtime paths are unchanged.

## Reproduce

From the repository with the disposable offline environment described in `tests/OFFLINE_TESTING.md`:

```sh
python -m unittest discover -s tests -p test_helper_protocol.py -v
```

Tests use synthetic hashes/keys and owner-only temporary directories. No script in a fixture executes. No provider, network, host policy, installer or paid operation is used.

## Next implementation boundary

A real adapter must independently bind caller identity and approval to the exact policy, preserve previous installed policy for recovery, apply through the supported Santa interface, read back actual installed rules and report uncertainty without retrying an unknown effect. That work needs the separately authorized macOS lab. This source-only prototype is not permission to install anything, and lab proof will not itself establish everyday-Mac protection.
