# MuseSwarm // ZERO — Win Plan
**Goal:** Place as high as possible in the Meta Global AI Developer Hackathon (Indie Track).
**Deadline:** Wednesday, Nov 4, 2026 · 9:00 PM Eastern / 8:00 PM America/Chicago. Target submission: Tuesday, Nov 3.
**Last planning update:** Sunday, Nov 1, 2026. Earlier sections below are historical strategy where superseded by section 0.

Product name **MuseSwarm**; **ZERO** is the edition tagline (use sparingly). Brand mark + tokens: [`assets/brand/BRAND.md`](./assets/brand/BRAND.md) · mark: [`assets/brand/swarmguard-mark.png`](./assets/brand/swarmguard-mark.png).

This file is the single “make it make sense” plan. Everything else supports it:

| Doc | Job |
|-----|-----|
| `WIN_PLAN.md` (this) | Strategy + calendar + decisions |
| `assets/brand/BRAND.md` | Logo, color tokens, do/don’t |
| `swarmguard_zero_meta_hackathon_blueprint.md` | Product + threat research + do/don’t |
| `meta_model_api_muse_code_expert_guide.md` | How to use Meta stack at full capacity |
| `meta_hackathon_rules_daily_tracker.md` | Live rules / dates / credits |
| `README.md` | How a stranger runs the demo |

---

## 0. Stream guidance integrated on Nov 1, 2026

This section takes precedence over older scope, timing, scoring and submission advice below. It distills four participant-supplied Granola summaries of the kickoff, Agents 101, Agents 102, and Fireworks workshops. These are secondary notes, not verbatim recordings, official rules, or proof that a product feature works. Raw notes, personal details and access-bearing share links are deliberately omitted.

### Current product truth and build gate

The product goal remains autonomous whole-computer protection, macOS first, with Windows/Linux later. Project hooks, an MCP wrapper, a selected-task workspace and a convincing attack demo are narrower evidence, not substitutes for that goal. Current shipped source proves scoped controls only. Whole-Mac enforcement, authenticated privileged helper boundaries, reboot recovery, uninstall safety and egress coverage remain unproven. Native live execution is disabled (`NATIVE_LIVE_RELEASED=False`). Do not change that gate, install a host helper, request new permissions or spend credits as a consequence of these notes.

### Workshop lessons turned into work

| Source session | Useful lesson | MuseSwarm action and proof needed |
|---|---|---|
| Kickoff (Oct 26) | Original work, real impact, Meta tooling, technical depth and a working demo matter more than a generic wrapper. | Show the specific event-built contribution, a real blocked action and the evidence behind the result. Separate existing dependencies from original code. Do not imply broad protection from a narrow harness. |
| Agents 101 (Oct 27) | Plan / act / observe loops need a checklist, recorded tool evidence and resumable progress. A plausible final answer is not verification. | Preserve action intent, approved scope, tool output, before/after state and cleanup in the incident trail. Test interrupted runs and recovery before claiming resumability. |
| Agents 102 (Oct 28) | Verification must be unavoidable, with deterministic checks before model judgment. Critical checks block the next action; retries need a hard bound. Restrict tool access and separate builder/reviewer permissions. | Keep schema, allowlist, manifest, budget and exact-readback checks in the execution path. A model verdict must never override a deny or expand authority. Test malformed proposals, missing evidence, denied tools, changed inputs, uncertain stop and recovery. Reviewer output is evidence, not permission. |
| Fireworks (Oct 30) | Evaluate on the actual task. More reasoning and more models can be worse or cost more. Routing/fine-tuning need held-out evaluation. | Start with offline, non-secret fixtures. Compare false allows, false denies, pass@1, latency and measured cost. Keep present bounded reasoning/retry settings until evidence supports a change. Routing, fan-out and training are optional experiments, not pre-submission work or approved spend. |

The legal-agent workshop's three retries and 80% checklist threshold were demo settings, not security acceptance criteria. Do not copy them into enforcement: a single unauthorized effect is a failure. Current provider paths intentionally have no automatic retry. A reviewer model cannot prove OS containment or inspect a missing helper boundary.

### Remaining sequence

1. Preserve the known-good offline suite and scoped deny proofs. Add negative-case and recovery evidence for any changed control before describing it as complete.
2. Finish the real macOS enforcement boundary only within an approved isolated test setup. Keep host permissions, installs, paid calls and release gates unchanged until separately authorized. If that proof is unavailable, name the gap in the demo and submission rather than declaring the whole-computer product finished.
3. Prepare the three-minute submission video and answers now. Use one coherent incident, show actual Meta contribution and deterministic enforcement separately, then close with measured results and honest limits. A shorter core sequence can fit inside the three-minute artifact, but two minutes is not the official requirement.
4. Complete a clean-clone run check, original-work/dependency/asset provenance audit and final owner review of submission terms, license choice and subjective answers. Do not treat this documentation update as terms acceptance, a license grant or submission approval.

### Verified submission facts and note corrections

Checked against the fully loaded official guide, rules and form on Nov 1, 2026:

- Deadline: Wednesday Nov 4, 9:00 PM Eastern, equivalent to 8:00 PM Chicago. Nov 3 is the project submission target, not the official cutoff.
- Both guide and form call for a **three-minute demo video**. Public GitHub repository and an accessible video link are required; identify the functionality built during the event.
- Rubric: Impact 30%, Meta AI Tooling 25%, Technical Depth & Execution 20%, Demo 25%. These are now confirmed in the formal rules, not speculative weights.
- Teams may have up to four participants; solo is allowed. Do not add unapproved participants or infer personal eligibility from these notes.
- Third-party technical assistance and licensed open source are permitted subject to the formal ownership and license conditions. Audit what is included; do not redistribute Santa or add a source license without the relevant rights and owner decision.
- Current official Fireworks offer is **$100 for selected teams**, not the kickoff note's $25. Partner credits are conditional, not a balance or spending authorization. Meta credit claims are individual and require a payment method; a notification is not a hard spending cap.
- The kickoff notes' fixed bonus categories/amounts and Fireworks notes' model sizes, free-training dates, retention claims, reasoning defaults and benchmark gains are workshop recollections. They are not required features or verified current vendor guarantees. Verify vendor documentation and actual account terms before relying on any of them.
- Rules acceptance, final license/rights review and submission remain separate gates. Discord announcements are not verified by reading these pages.

Official sources: [Participant guide](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details), [Official rules](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/waiver), [Submission form](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit). Educational provenance: participant-supplied Granola summaries of the four named sessions above, received Nov 1; summaries can contain transcription errors. No raw transcript or share credential is committed.

---

## 1. The winning idea in one breath

**Problem:** Developers now give AI agents terminals, files, and MCP tools. Traditional antivirus cannot see a prompt injection that says “steal `.env`.” That attack class is documented in the wild (Unit 42, HiddenLayer, OWASP MCP).

**Product:** MuseSwarm is **autonomous antivirus for agents** — fail-closed **IDE PreToolUse hook + MCP policy proxy on the wire**, plus Muse Spark *sees* poisoned artifacts, Muse Wonder *explains*, SAM *isolates*, then the swarm **quarantines without asking** and **reports**.

**Claim line:** *fail-closed on the wire + Meta multimodal forensics.*

```
Cursor / Claude Code → IDE hook (policy.py) ─┐
Agent MCP tools      → MCP proxy (policy.py) ─┴─ deny → threat_bus + protector UI
```

**Why Meta judges should care:**
- **Build for Your World** — firsthand builder pain (Cursor/agent + secrets).
- **Push the Frontier** — new control surface: runtime defense for agentic systems.
- **Meta tooling** — not one model bolted on; a *composed* Spark + Wonder + SAM pipeline on Model API.

**Indie track filter:** creativity + ambition + **it works**. Demo = **IDE + MCP hard deny** + **Attack 01 Meta path**.

---

## 2. How judging actually works (and how we score)

Public Indie framing: creativity, technical ambition, whether it works.
Formal rules weights (verified Nov 1; see section 0):

| Bucket | ~Weight | Our weapon | Must show on video |
|--------|---------|------------|--------------------|
| Impact | 30% | “AV is blind to agent hijacks” + real attack citations | Problem → consequence → MuseSwarm |
| Meta tooling | 25% | Spark multimodal + Wonder high + SAM on same artifact | Say model IDs out loud; chips on screen |
| Demo | 25% | Autonomous inject → chain → auto-quarantine → report | One continuous real run |
| Execution | 20% | Clean happy path, honest safety, readable repo | No crashes, no Tk detour |

**Winning formula:**
`Clear stakes` × `Unexpected Meta combo` × `Flawless 90s demo` × `Honest scope`

**Losing formula:**
`Feature zoo` × `Fragile desktop widget` × `LLM-only vibes with no action` × `Claims we can’t defend`

---

## 3. What we already have (assets, not homework)

Treat these as **done foundation**:

- Protector UI (`dashboard.py` + menu-bar mark) — inject → Muse pipeline → auto-quarantine → incident log + sounds (not a War Room game HUD)
- Brand assets (`assets/brand/`) — shield + swarm mark, menu-bar icon, tokens
- Multi-model brain (`swarm_brain.py`) — Spark guards (Overwatch multimodal), Wonder forensics, SAM boxes
- Autonomy + bus (`autonomy.py`, `threat_bus.py`, `sounds.py`)
- Live verification already proved: Overwatch *read* white-on-white text; Wonder quoted it; SAM boxed; auto-quarantine logged

**Do not rebuild.** Polish and productize the one path.

---

## 4. The north-star demo (this is the product)

**Locked 2-minute story: gate deny + Attack 01.**

```
1. Protector: “Protecting — gate on.”
2. IDE hooks live (Cursor `.cursor/hooks.json`) + start MCP proxy → UI: “MCP gate: wrapping tools.”
3. Agent tries read .env / exfil curl → HARD DENY (policy only; no Muse tokens).
4. Optional / second beat: See it work → Attack 01 poisoned README
       → Spark Overwatch (vision) + Bloodhound
       → Wonder forensics + SAM boxes
       → AUTO-QUARANTINE + activity log
5. Tagline: antivirus for agents — on the wire, with Meta eyes.
```

**Narration spine (≤2:00):**
1. Agents have terminals, files, and MCP tools; classic AV never sees the call.
2. MuseSwarm sits in the IDE hook *and* on the MCP wire — `.env` theft dies at the gate.
3. Meta Spark/Wonder/SAM still catch the *hidden* injection path.
4. Indie track. MuseSwarm Zero.

Prove locally (no API):
`python safe_range/run_mcp_gate_demo.py` · `python safe_range/run_ide_hook_demo.py`

Honest limits: IDE hook soft-allows benign unknown paths/cmds so coding stays usable; MCP proxy remains hard fail-closed. No SIGKILL.

---

## 5. Strategic decisions (locked)

| Decision | Choice | Why |
|----------|--------|-----|
| Track | Indie solo | Matches status; ambition via idea not headcount |
| Theme | Lead **Build for Your World**, nod **Push the Frontier** | Personal agent-security pain + new control capability |
| Primary UI | macOS **menu-bar Protector** (`menubar.py` native NSPanel) | Quiet AV vibes; stay in-app |
| Optional deep console | Streamlit `dashboard.py` | Advanced / demo secondary — not required for core status |
| Primary behavior | IDE hook + MCP proxy deny-before-run + AI inspect + report | Feels like AV, not a SOC toy |
| Meta stack | Spark + Wonder + SAM on Model API | Maximizes tooling score |
| Muse on every tool call | **OFF** by default (`SWARMGUARD_MUSE_ON_AMBIGUOUS=0`) | Token discipline |
| Safety claim | Simulated quarantine; no real SIGKILL | Survives Q&A; still dramatic |
| Scope lock | Gate proof + Attack 01 > five half features | Indie judges punish sprawl |

---

## 6. Gap analysis — only build what moves score

### P0 — historical demo priorities (subject to section 0)
1. **Bulletproof Attack 01** — structured JSON output (`response_format`) so forensics never parse-fail mid-demo.
2. **Visible Muse proof** — on-screen model IDs + optional Wonder `reasoning.summary` line in the chain.
3. **Record 2 takes** of the north-star demo; keep a known-good backup recording.
4. **GitHub + README** that runs in 2 commands; commits inside Oct 26–Nov 4 window.
5. **Submission writeup** mapped to Impact / Tooling / Demo / Execution.
6. Owner must review Official Rules acceptance and rights; no credit claim or spend is authorized by this plan.

### P1 — if ≥1–2 days remain (raises tooling + impact credibility)
1. ~~Fail-closed policy layer~~ **Done** — `policy.py` + `threat_model.py` (16+ gate probes + Muse for injection).
2. ~~MCP stdio policy proxy~~ **Done** — `mcp_proxy.py` + `safe_range/run_mcp_gate_demo.py` (deny before upstream; dashboard heartbeat).
3. ~~IDE PreToolUse hook~~ **Done** — `hooks/swarmguard_pretool.py` + `.cursor/hooks.json` + `.claude/settings.json` + `safe_range/run_ide_hook_demo.py` (deny `.env` / evil curl; `trigger=ide_hook`).
4. **Mission policy banner** — “goal: refactor UI → secrets/egress denied” (ClawGuard-inspired, visible).

### P2 — skip unless ahead of schedule
- Muse Image fixture generator, voice narration, Sunglasses-scale DLP encyclopedia, SSE stream DLP, cross-platform installers, Tk widget revival.

---

## 7. How the Meta stack should be framed (tooling score)

From the expert guide — **compose**, don’t sprinkle:

| Layer | Model | Job in the story |
|-------|--------|------------------|
| Perception | `muse-spark-1.3` | Specialist guards; Overwatch multimodal on artifact |
| Judgment | `muse-wonder-1.0` | Chief forensics, evidence quotes, high reasoning |
| Localization | `sam-3.1` | Pixel/box isolation of the trap |
| Build tooling | Muse Code (optional credit) | “We built faster with Muse Code” in writeup, not the demo hero |

**Say on video:** “muse-spark-1.3, muse-wonder-1.0, sam-3.1 on Meta Model API.”

**Protocol note:** Chat Completions is fine for one-shot guards; prefer Responses for Wonder if we add tool loops / reasoning summaries before submit.

---

## 8. Narrative for the written submission (copy base)

**Title:** MuseSwarm // ZERO — Autonomous Antivirus for the Agentic Era

**Problem:** Indirect prompt injection and MCP tool abuse can turn trusted coding/browser agents into credential thieves. Classic AV looks for malware files, not hijacked tool calls. Research from Unit 42, HiddenLayer, and OWASP documents these attacks in the wild.

**Solution:** An IDE **PreToolUse hook** plus MCP stdio **policy proxy** that deny dangerous tool calls before they run, plus a Meta-powered swarm that scores threats with Muse Spark, synthesizes forensics with Muse Wonder, isolates visual traps with SAM 3.1, then **auto-quarantines and reports** without waiting for a human kill click.

**Meta usage:** Multimodal Spark (image+text), high-reasoning Wonder reports, SAM segmentation on the same artifact — one incident, three Meta surfaces.

**Track/theme:** Indie · Build for Your World (and frontier runtime control for agents).

**Safety:** Demo harness simulates rogue agents; host process inspection is read-only; we do not SIGKILL arbitrary OS processes.

---

## 9. Day-by-day calendar (Oct 29 → Nov 4)

| Day | Focus | Done when |
|-----|--------|-----------|
| **Thu Oct 29** | P0 reliability: structured output + demo dry run #1 | Attack 01 succeeds 3× in a row |
| **Fri Oct 30** | Polish protector proof chips / chain clarity; draft writeup | Writeup skeleton filled |
| **Sat Oct 31** | P1 fail-closed rules *or* polish only if tired | Either policy banner ships or consciously skipped |
| **Sun Nov 1** | Record demo takes (2+); pick best; upload draft private | Video file exists |
| **Mon Nov 2** | GitHub cleanup, README, screenshots, final writeup | Repo cloneable by a stranger |
| **Tue Nov 3** | Target submission after final owner review | Submission confirmation saved |
| **Wed Nov 4** | Official deadline buffer only; no unapproved submission action | If still pending, escalate before 9:00 PM Eastern |

Workshops/Discord: only attend if it unblocks credits or Official Rules — do not sacrifice the demo for FOMO.

### API spend discipline
Oct 28 stress runs burned most of a day’s Model API usage (~$1.80 / 225 requests). Remaining week:
- Do **not** re-run `python stress_test.py 3` casually (already proven 18/18).
- Practice/demo: Protector **Attack 01 only**, or `python stress_test.py smoke`.
- Claim partner credits (Fireworks/Modal/Baseten) if Meta Model API budget is tight — keep Meta API for the recorded demo.

---

## 10. Anti-goals (explicit)

- Do not make MuseSwarm a general malware scanner.
- Do not auto-kill real user processes.
- Do not center the Tk widget.
- Menu-bar companion (`./run_menubar.sh`) is optional AV chrome — never call Muse from it; never SIGKILL.
- Do not add dashboards, settings pages, or auth walls before the core loop is cinematic.
- Do not burn API credits on continuous auto-fire during practice unless testing.
- Do not claim “prompt injection solved.”

---

## 11. Submission packet checklist

- [ ] GitHub repo public (or accessible per rules) with hackathon-window commits
- [ ] `README.md` run steps (venv → streamlit)
- [ ] Three-minute demo video on an accessible supported video host — **real product**
- [ ] Written description: problem, Meta architecture, track/theme
- [ ] Disclose any boilerplate
- [ ] Official Rules accepted
- [ ] Submitted ≥3 hours early

---

## 12. If we only do three things from here

1. **Make Attack 01 unbreakable** (structured output + rehearsal).
2. **Record the autonomous demo** with model names spoken.
3. **Ship a clean repo + rubric-shaped writeup.**

That is the highest-probability path to win Indie: one story, Meta-native intelligence, undeniable proof on video.

---

## 13. Operating rule for the remaining week

Every feature request must answer: **Does this make Attack 01 more convincing on a 2-minute judge screen?**
If no → defer.

When uncertain, open this file first — not a new brainstorm.
