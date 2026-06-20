"""Data model for lint findings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Finding:
    """A single provider-compatibility violation in a schema.

    Attributes:
        provider: the provider the rule belongs to (openai|anthropic|gemini).
        rule_id: stable identifier of the rule that fired.
        kind: the rule kind (drives auto-repair dispatch).
        node_pointer: JSON Pointer to the subschema the rule applies to.
        json_pointer: JSON Pointer to the precise offending location (keyword).
        keyword: the JSON-Schema keyword / property name involved.
        reason: human-readable explanation.
        severity: "error" (fails CI) or "warning".
        doc_url: primary-source link documenting the constraint.
    """

    provider: str
    rule_id: str
    kind: str
    node_pointer: str
    json_pointer: str
    keyword: str
    reason: str
    severity: str = "error"
    doc_url: str = ""
    auto_repair: str = "manual"  # strip | set_false | fill_required | manual

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
