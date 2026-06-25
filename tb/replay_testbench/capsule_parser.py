"""Parse lightweight replay capsule fixtures.

The parser intentionally accepts only simple, inspectable input:

JSON:
    {
      "property_id": "rv32i.irq.mmio",
      "failure_signature": "store_mismatch",
      "events": [
        {"kind": "pc", "cycle": 8, "commit": 3, "pc": "0x80000010"}
      ]
    }

Text:
    property_id rv32i.irq.mmio
    failure_signature store_mismatch
    pc cycle=8 commit=3 pc=0x80000010
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import shlex
from typing import Any, Iterable, Mapping


class CapsuleParseError(ValueError):
    """Raised when a capsule fixture cannot be parsed."""


_METADATA_KEYS = {
    "property",
    "property_id",
    "prop",
    "failure",
    "failure_signature",
    "signature",
}

_INT_FIELDS = {
    "cycle",
    "cycle_index",
    "commit",
    "commit_index",
    "retire",
    "order",
    "event_seq",
    "seq",
    "pc",
    "program_counter",
    "addr",
    "address",
    "value",
    "data",
    "rdata",
    "wdata",
    "irq_value",
    "byte_en",
    "be",
    "width",
    "size",
    "resp",
    "response",
    "cause",
    "source_id",
}

_CYCLE_ALIASES = ("cycle", "cycle_index", "cycle_idx", "c")
_COMMIT_ALIASES = ("commit", "commit_index", "commit_idx", "retire", "retire_index")
_ORDER_ALIASES = ("order", "event_seq", "seq", "ordinal", "tag")
_PC_ALIASES = ("pc", "program_counter")
_ADDR_ALIASES = ("addr", "address", "mmio_addr")
_VALUE_ALIASES = ("value", "data", "mmio_value", "rdata", "wdata", "irq_value", "payload")
_IRQ_ALIASES = ("irq", "interrupt", "interrupt_id", "line", "source_id")
_STATE_ALIASES = ("state", "level", "edge", "action", "phase")
_DIRECTION_ALIASES = ("direction", "dir", "op", "access")
_INPUT_ID_ALIASES = ("input_id", "input", "id", "source", "port")
_BYTE_EN_ALIASES = ("byte_en", "be", "byte_enable", "byte_lanes")
_WIDTH_ALIASES = ("width", "size")
_RESP_ALIASES = ("resp", "response", "status")
_CAUSE_ALIASES = ("cause", "trap_cause")


@dataclass(frozen=True)
class CapsuleEvent:
    """A normalized replay evidence event."""

    kind: str
    cycle: int | None = None
    commit: int | None = None
    order: int | None = None
    pc: int | None = None
    addr: int | None = None
    value: int | str | None = None
    byte_en: int | None = None
    width: int | None = None
    resp: int | str | None = None
    cause: int | str | None = None
    irq: str | None = None
    state: str | None = None
    direction: str | None = None
    input_id: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)

    def index(self, mode: str) -> int | None:
        """Return the cycle or commit index used for matching."""

        normalized = normalize_match_mode(mode)
        if normalized == "cycle":
            return self.cycle
        if normalized == "commit":
            return self.commit
        raise ValueError(f"unknown match mode: {mode}")


@dataclass(frozen=True)
class ReplayCapsule:
    """A property failure capsule plus replay evidence events."""

    property_id: str | None
    failure_signature: str | None
    events: tuple[CapsuleEvent, ...]
    source: str = "<memory>"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def events_of_kind(self, kind: str) -> tuple[CapsuleEvent, ...]:
        canonical = normalize_event_kind(kind)
        return tuple(event for event in self.events if event.kind == canonical)


def normalize_match_mode(mode: str) -> str:
    """Normalize public match mode names."""

    normalized = mode.lower().replace("_", "-")
    if normalized in {"cycle", "cycle-index", "cycle-indexed"}:
        return "cycle"
    if normalized in {"commit", "commit-index", "commit-indexed", "retire"}:
        return "commit"
    raise ValueError("match mode must be 'cycle' or 'commit'")


def normalize_event_kind(kind: str | None) -> str:
    """Map friendly fixture names onto the evidence kinds used by compare."""

    normalized = (kind or "event").strip().lower().replace("-", "_")
    if normalized.startswith("evt_"):
        normalized = normalized[4:]
    if normalized in {
        "pc",
        "pc_evidence",
        "program_counter",
        "instruction",
        "commit_pc",
        "sync",
    }:
        return "pc"
    if normalized in {
        "mmio",
        "mmio_read",
        "mmio_write",
        "mmio_write_observed",
        "bus",
    }:
        return "mmio"
    if normalized in {"store", "data_store", "protected_store"}:
        return "store"
    if normalized in {"load", "data_load"}:
        return "load"
    if normalized in {"branch", "context_branch", "taken_branch"}:
        return "branch"
    if normalized in {"jump", "context_jump", "taken_jump"}:
        return "jump"
    if normalized in {"checkpoint", "hash", "checkpoint_hash", "hash_checkpoint"}:
        return "checkpoint"
    if normalized in {
        "irq",
        "irq_level",
        "irq_taken",
        "interrupt",
        "interrupt_line",
        "interrupt_delivery",
        "trap",
        "exception",
    }:
        return "interrupt"
    if normalized in {
        "input",
        "input_consumed",
        "consume",
        "stimulus",
        "external_input",
        "reset_input",
        "external_memory_write",
    }:
        return "input"
    return normalized


def parse_capsule_file(path: str | Path) -> ReplayCapsule:
    """Parse a replay capsule from a JSON or text file."""

    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CapsuleParseError(f"cannot read {file_path}: {exc}") from exc
    return parse_capsule(text, source=str(file_path))


def parse_capsule(text: str, source: str = "<memory>") -> ReplayCapsule:
    """Parse a replay capsule from JSON or line-oriented text."""

    stripped = text.strip()
    if not stripped:
        raise CapsuleParseError(f"{source}: empty capsule")

    if stripped[0] in "[{":
        try:
            return _parse_json_capsule(json.loads(stripped), source)
        except json.JSONDecodeError as exc:
            raise CapsuleParseError(f"{source}: invalid JSON at line {exc.lineno}") from exc

    return _parse_text_capsule(stripped.splitlines(), source)


def _parse_json_capsule(data: Any, source: str) -> ReplayCapsule:
    if isinstance(data, list):
        payload: dict[str, Any] = {"events": data}
    elif isinstance(data, dict):
        payload = dict(data)
    else:
        raise CapsuleParseError(f"{source}: JSON capsule must be an object or event array")

    events: list[CapsuleEvent] = []
    for item in _iter_event_payloads(payload):
        events.append(_event_from_mapping(item, source))

    property_id = _as_optional_str(_first_present(payload, ("property_id", "property", "prop")))
    failure_signature = _as_optional_str(
        _first_present(payload, ("failure_signature", "failure", "signature"))
    )

    if property_id is None:
        property_id = _first_event_metadata(events, ("property_id", "property", "prop"))
    if failure_signature is None:
        failure_signature = _first_event_metadata(
            events, ("failure_signature", "failure", "signature")
        )

    metadata = {key: value for key, value in payload.items() if key != "events"}
    return ReplayCapsule(
        property_id=property_id,
        failure_signature=failure_signature,
        events=tuple(events),
        source=source,
        metadata=metadata,
    )


def _iter_event_payloads(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    grouped_keys = (
        ("events", None),
        ("pc_evidence", "pc"),
        ("pcs", "pc"),
        ("mmio_evidence", "mmio"),
        ("mmio", "mmio"),
        ("interrupts", "interrupt"),
        ("irqs", "interrupt"),
        ("inputs", "input"),
    )
    for key, default_kind in grouped_keys:
        value = payload.get(key)
        if value is None:
            continue
        if not isinstance(value, list):
            raise CapsuleParseError(f"{key} must be a list")
        for item in value:
            if isinstance(item, str):
                parsed = _parse_event_line(item, f"{key} item")
            elif isinstance(item, dict):
                parsed = dict(item)
            else:
                raise CapsuleParseError(f"{key} entries must be objects or strings")
            if (
                default_kind
                and "kind" not in parsed
                and "type" not in parsed
                and "event_type" not in parsed
            ):
                parsed["kind"] = default_kind
            yield parsed


def _parse_text_capsule(lines: Iterable[str], source: str) -> ReplayCapsule:
    metadata: dict[str, Any] = {}
    events: list[CapsuleEvent] = []

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue

        fields = _parse_event_line(line, f"{source}:{lineno}")
        if _is_metadata_line(fields):
            metadata.update(_metadata_from_fields(fields))
            continue
        events.append(_event_from_mapping(fields, f"{source}:{lineno}"))

    return ReplayCapsule(
        property_id=_as_optional_str(_first_present(metadata, ("property_id", "property", "prop"))),
        failure_signature=_as_optional_str(
            _first_present(metadata, ("failure_signature", "failure", "signature"))
        ),
        events=tuple(events),
        source=source,
        metadata=metadata,
    )


def _parse_event_line(line: str, source: str) -> dict[str, Any]:
    try:
        tokens = shlex.split(line, comments=False, posix=True)
    except ValueError as exc:
        raise CapsuleParseError(f"{source}: cannot parse line: {line}") from exc

    if not tokens:
        return {}

    fields: dict[str, Any] = {}
    bare_tokens: list[str] = []
    for token in tokens:
        if token.startswith("@") and len(token) > 1:
            fields["cycle"] = token[1:]
        elif token.startswith("#") and len(token) > 1:
            fields["commit"] = token[1:]
        elif "=" in token:
            key, value = token.split("=", 1)
            fields[key.strip().lower()] = _coerce_scalar(key, value)
        else:
            bare_tokens.append(token)

    if bare_tokens:
        if len(bare_tokens) == 2 and bare_tokens[0].lower() in _METADATA_KEYS:
            fields[bare_tokens[0].lower()] = bare_tokens[1]
        elif "kind" not in fields and "type" not in fields:
            fields["kind"] = bare_tokens[0]
            for extra in bare_tokens[1:]:
                fields.setdefault("label", extra)
        else:
            fields.setdefault("label", " ".join(bare_tokens))

    return fields


def _event_from_mapping(mapping: Mapping[str, Any], source: str) -> CapsuleEvent:
    lower = {str(key).strip().lower(): value for key, value in mapping.items()}
    kind = normalize_event_kind(
        _as_optional_str(_first_present(lower, ("kind", "type", "event", "event_type")))
    )
    direction = _as_optional_str(_first_present(lower, _DIRECTION_ALIASES))

    raw_kind = _as_optional_str(_first_present(lower, ("kind", "type", "event", "event_type")))
    if kind == "mmio" and direction is None and raw_kind:
        lowered = raw_kind.lower().replace("-", "_")
        if lowered.startswith("evt_"):
            lowered = lowered[4:]
        if lowered.endswith("_read") or lowered == "load":
            direction = "read"
        elif lowered.endswith("_write") or lowered in {"store", "mmio_write_observed"}:
            direction = "write"

    return CapsuleEvent(
        kind=kind,
        cycle=_as_optional_int(_first_present(lower, _CYCLE_ALIASES), source, "cycle"),
        commit=_as_optional_int(_first_present(lower, _COMMIT_ALIASES), source, "commit"),
        order=_as_optional_int(_first_present(lower, _ORDER_ALIASES), source, "order"),
        pc=_as_optional_int(_first_present(lower, _PC_ALIASES), source, "pc"),
        addr=_as_optional_int(_first_present(lower, _ADDR_ALIASES), source, "addr"),
        value=_normalize_value(_first_present(lower, _VALUE_ALIASES), source),
        byte_en=_as_optional_int(_first_present(lower, _BYTE_EN_ALIASES), source, "byte_en"),
        width=_as_optional_int(_first_present(lower, _WIDTH_ALIASES), source, "width"),
        resp=_normalize_value(_first_present(lower, _RESP_ALIASES), source),
        cause=_normalize_value(_first_present(lower, _CAUSE_ALIASES), source),
        irq=_as_optional_str(_first_present(lower, _IRQ_ALIASES)),
        state=_as_optional_str(_first_present(lower, _STATE_ALIASES)),
        direction=_normalize_direction(direction),
        input_id=_as_optional_str(_first_present(lower, _INPUT_ID_ALIASES)),
        raw=dict(mapping),
    )


def _is_metadata_line(fields: Mapping[str, Any]) -> bool:
    if not fields:
        return False
    keys = {str(key).lower() for key in fields}
    return bool(keys & _METADATA_KEYS) and "kind" not in keys and "type" not in keys


def _metadata_from_fields(fields: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in fields.items():
        normalized = "property_id" if key in {"property", "prop"} else key
        normalized = "failure_signature" if normalized in {"failure", "signature"} else normalized
        result[normalized] = value
    return result


def _first_present(mapping: Mapping[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _first_event_metadata(events: Iterable[CapsuleEvent], keys: Iterable[str]) -> str | None:
    for event in events:
        lower = {str(key).lower(): value for key, value in event.raw.items()}
        value = _first_present(lower, keys)
        if value is not None:
            return _as_optional_str(value)
    return None


def _coerce_scalar(key: str, value: str) -> int | str:
    if key.lower() in _INT_FIELDS:
        return _parse_int(value, key)
    return value


def _as_optional_int(value: Any, source: str, field_name: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return _parse_int(value, field_name)
    raise CapsuleParseError(f"{source}: {field_name} must be an integer")


def _parse_int(value: str, field_name: str) -> int:
    try:
        return int(value.replace("_", ""), 0)
    except ValueError as exc:
        raise CapsuleParseError(f"{field_name} must be an integer, got {value!r}") from exc


def _normalize_value(value: Any, source: str) -> int | str | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return _parse_int(value, "value")
        except CapsuleParseError:
            return value
    raise CapsuleParseError(f"{source}: value must be an integer or string")


def _normalize_direction(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.lower()
    if normalized in {"r", "read", "load"}:
        return "read"
    if normalized in {"w", "write", "store"}:
        return "write"
    return normalized


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
