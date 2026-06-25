# Event-Sufficient Replay Model

The model fixes the firmware image, initial architectural state, core implementation, and deterministic memory state. It treats MMIO read values, external inputs, and interrupt timing as nondeterministic boundary events. Time is primarily commit-index based, so replay remains robust to cycle-level implementation variation when the architectural commit order is unchanged.

The theorem states that, under the documented assumptions, a capsule containing all nondeterministic MMIO input values, interrupt timing events, and property-relevant evidence reproduces the same supported safety-property violation.

Full details are in `docs/event_model.md` and `formal/replay_sufficiency_theorem.md`.

Current model-level ablations write `results/processed/event_sufficiency.csv`, which identifies the event classes whose removal breaks replay for each benchmark model. These rows are evidence for the benchmark models only; they do not yet prove RTL-level minimality.
