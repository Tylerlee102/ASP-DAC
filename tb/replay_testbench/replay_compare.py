"""Deterministic replay comparison rules for lightweight capsules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from .capsule_parser import CapsuleEvent, ReplayCapsule, normalize_match_mode
except ImportError:  # pragma: no cover - script-friendly fallback
    from capsule_parser import CapsuleEvent, ReplayCapsule, normalize_match_mode


MappingSummary = dict[str, int]


@dataclass(frozen=True)
class ReplayResult:
    """Structured replay comparison result."""

    success: bool
    mode: str
    errors: tuple[str, ...] = ()
    matched: MappingSummary = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "mode": self.mode,
            "errors": list(self.errors),
            "matched": dict(self.matched),
        }

    def format(self) -> str:
        if self.success:
            parts = [f"PASS replay matched using {self.mode}-index mode"]
        else:
            parts = [f"FAIL replay mismatch using {self.mode}-index mode"]
        for kind, count in self.matched.items():
            parts.append(f"  matched {kind}: {count}")
        for error in self.errors:
            parts.append(f"  - {error}")
        return "\n".join(parts)


_MATCH_FIELDS = {
    "pc": ("pc", "order"),
    "mmio": ("addr", "value", "direction", "byte_en", "width", "resp", "order"),
    "interrupt": ("irq", "state", "value", "cause", "order"),
    "input": ("input_id", "addr", "value", "width", "order"),
    "store": ("pc", "addr", "value", "byte_en", "width", "order"),
    "branch": ("pc", "value", "order"),
    "checkpoint": ("value", "order"),
}


def compare_capsules(
    expected: ReplayCapsule,
    observed: ReplayCapsule,
    mode: str = "cycle",
) -> ReplayResult:
    """Compare expected capsule evidence against an observed replay trace.

    A pass requires:
    * identical property IDs
    * identical failure signatures
    * at least one PC evidence event and one MMIO evidence event in the capsule
    * matching PC and MMIO evidence at the selected cycle or commit index
    * exact input-consumption evidence
    * exact interrupt timing evidence
    """

    normalized_mode = normalize_match_mode(mode)
    errors: list[str] = []
    matched: MappingSummary = {}

    _compare_metadata(expected, observed, errors)

    expected_pc = expected.events_of_kind("pc")
    expected_mmio = expected.events_of_kind("mmio")
    expected_store = expected.events_of_kind("store")
    expected_branch = expected.events_of_kind("branch")
    expected_input = expected.events_of_kind("input")
    expected_interrupt = expected.events_of_kind("interrupt")
    if not expected_pc:
        errors.append("expected capsule has no PC evidence events")
    if not (expected_mmio or expected_store or expected_branch or expected_input or expected_interrupt):
        errors.append("expected capsule has no replay-relevant evidence events")

    _match_event_set(
        "pc",
        expected_pc,
        observed.events_of_kind("pc"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=True,
    )
    _match_event_set(
        "mmio",
        expected_mmio,
        observed.events_of_kind("mmio"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=False,
    )
    _match_event_set(
        "input",
        expected_input,
        observed.events_of_kind("input"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=False,
    )
    _match_event_set(
        "interrupt",
        expected_interrupt,
        observed.events_of_kind("interrupt"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=False,
    )
    _match_event_set(
        "store",
        expected_store,
        observed.events_of_kind("store"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=False,
    )
    _match_event_set(
        "branch",
        expected_branch,
        observed.events_of_kind("branch"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=False,
    )
    _match_event_set(
        "checkpoint",
        expected.events_of_kind("checkpoint"),
        observed.events_of_kind("checkpoint"),
        normalized_mode,
        errors,
        matched,
        allow_extra_observed=False,
    )

    return ReplayResult(
        success=not errors,
        mode=normalized_mode,
        errors=tuple(errors),
        matched=matched,
    )


def _compare_metadata(
    expected: ReplayCapsule,
    observed: ReplayCapsule,
    errors: list[str],
) -> None:
    if not expected.property_id:
        errors.append("expected capsule is missing property_id")
    if not observed.property_id:
        errors.append("observed trace is missing property_id")
    if expected.property_id and observed.property_id and expected.property_id != observed.property_id:
        errors.append(
            f"property_id mismatch: expected {expected.property_id!r}, observed {observed.property_id!r}"
        )

    if not expected.failure_signature:
        errors.append("expected capsule is missing failure_signature")
    if not observed.failure_signature:
        errors.append("observed trace is missing failure_signature")
    if (
        expected.failure_signature
        and observed.failure_signature
        and expected.failure_signature != observed.failure_signature
    ):
        errors.append(
            "failure_signature mismatch: "
            f"expected {expected.failure_signature!r}, observed {observed.failure_signature!r}"
        )


def _match_event_set(
    kind: str,
    expected_events: tuple[CapsuleEvent, ...],
    observed_events: tuple[CapsuleEvent, ...],
    mode: str,
    errors: list[str],
    matched: MappingSummary,
    allow_extra_observed: bool,
) -> None:
    used_observed: set[int] = set()
    count = 0

    for expected in expected_events:
        expected_index = expected.index(mode)
        if expected_index is None:
            errors.append(f"expected {kind} event missing {mode} index: {_describe_event(expected, mode)}")
            continue

        match_index = _find_matching_event(expected, observed_events, used_observed, kind, mode)
        if match_index is None:
            errors.append(
                f"missing {kind} event at {mode} {expected_index}: "
                f"{_describe_signature(expected, kind)}"
            )
            continue
        used_observed.add(match_index)
        count += 1

    if not allow_extra_observed:
        for index, observed in enumerate(observed_events):
            if index in used_observed:
                continue
            observed_index = observed.index(mode)
            errors.append(
                f"extra observed {kind} event at {mode} {observed_index}: "
                f"{_describe_signature(observed, kind)}"
            )

    matched[kind] = count


def _find_matching_event(
    expected: CapsuleEvent,
    observed_events: tuple[CapsuleEvent, ...],
    used_observed: set[int],
    kind: str,
    mode: str,
) -> int | None:
    expected_index = expected.index(mode)
    for index, observed in enumerate(observed_events):
        if index in used_observed:
            continue
        if observed.index(mode) != expected_index:
            continue
        if _event_fields_match(expected, observed, kind):
            return index
    return None


def _event_fields_match(expected: CapsuleEvent, observed: CapsuleEvent, kind: str) -> bool:
    for field_name in _MATCH_FIELDS[kind]:
        expected_value = getattr(expected, field_name)
        if expected_value is None:
            continue
        if getattr(observed, field_name) != expected_value:
            return False
    return True


def _describe_event(event: CapsuleEvent, mode: str) -> str:
    index = event.index(mode)
    return f"{event.kind}@{mode}={index} {_describe_signature(event, event.kind)}"


def _describe_signature(event: CapsuleEvent, kind: str) -> str:
    fields = []
    for field_name in _MATCH_FIELDS.get(kind, ()):
        value = getattr(event, field_name)
        if value is None:
            continue
        fields.append(f"{field_name}={_format_value(value)}")
    return " ".join(fields) if fields else "<no fields>"


def _format_value(value: object) -> str:
    if isinstance(value, int):
        return hex(value)
    return repr(value)
