# Verification Agent Notes

## Role

The verification agent owns the ReplayCapsule-RV verification strategy,
assertion checklist, and test planning documents for deterministic replay of
RV32I interrupt and MMIO behavior.

Owned files:

- `docs/verification_plan.md`
- `formal/sv_assertions/README.md`
- `formal/yosys_smtbmc_scripts/README.md`
- `tb/cocotb/README.md`
- `tb/verilator/README.md`
- `tb/property_tests/README.md`
- `tb/randomized_interrupt_tests/README.md`
- `docs/subagents/verification_agent.md`

Do not revert or rewrite files owned by other agents. If another agent adds RTL,
interfaces, signal names, or test harness code, update these docs to reference
the real names without changing their work.

## Verification Focus

The verification agent treats event sufficiency as the central requirement:

- recorded events are complete enough to replay nondeterministic behavior
- event order is stable by `(commit_index, order)` and replay-visible
- frozen capsules are immutable
- overflow invalidates replay rather than silently truncating data
- interrupt delivery during replay is paired with recorded delivery
- MMIO read data is captured and replayed instead of sampled from live devices
- checkers have negative tests proving they catch bad capsules
- randomized tests are seed-reproducible

## Collaboration Points

Coordinate with RTL owners for:

- recorder and replay interface signal names
- exact event payload fields
- freeze and clear semantics
- overflow status semantics
- interrupt boundary definition
- MMIO determinism policy for writes
- replay behavior when live interrupts arrive

Coordinate with testbench owners for:

- trace format
- seed artifact path
- scoreboard API
- corruption fixture format
- CI regression grouping

## Definition of Done

Documentation is ready when:

- every required risk has a formal, simulation, or property-test strategy
- each strategy includes at least one positive and one negative check where
  applicable
- seeded replay requirements are explicit
- open architectural assumptions are called out instead of hidden in harness code
- future implementers can translate checklist items into properties or tests

## Open Assumptions To Resolve

- Whether the first implementation needs cycle-level diagnostics in addition to
  commit-index replay semantics.
- Whether MMIO writes are recorded, ignored, or constrained as deterministic.
- Whether nested interrupts are supported by the target RV32I integration.
- Whether live interrupts are masked or arbitrated during replay.
- Which fields participate in the frozen capsule digest.
- How freeze interacts with an event accepted but not yet committed.
