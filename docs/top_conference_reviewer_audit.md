# Top-Conference Reviewer Audit

Overall status: **SUBMISSION-READY**

## Hardware architecture reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims

## EDA/synthesis reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims

## Systems/debug reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims

## Formal/replay-model reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims

## Artifact evaluation reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims

## Skeptical novelty reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims

## Quantitative evaluation reviewer

rating: weak accept

top strengths:
- compiler-backed firmware and full RTL replay evidence are strong
- v2 captured-store self-replay and Hazard3 replay matrix evidence are now present
- corrupted-capsule rejection is explicit
- artifact scripts produce traceable CSVs and paper artifacts

top weaknesses:
- diagnostic mapped LUT/FF overhead is high
- broad replay remains harness-orchestrated rather than a board/silicon replay flow
- benchmark and peripheral diversity are limited

fatal blockers: none after scoped wording

likely reviewer questions:
- How does overhead scale beyond the demonstrated FPGA points?
- Which event classes are replay-critical versus diagnostic-only?
- Why is simulator wall time separated from hardware cycle overhead?

required paper wording changes:
- state that captured-store self-replay is controller-driven RTL evidence, not a board/silicon replay engine
- report the selected v2 replay-critical recorder profile separately from diagnostic-rich rows
- keep detailed-route ASIC signoff, tapeout, silicon energy, and multicore/DMA/cache support out of claims

final recommendation: submit main-track with scoped claims
