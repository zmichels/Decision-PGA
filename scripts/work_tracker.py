"""Validate and summarize a repo-native Markdown/YAML work tracker."""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in environments without PyYAML
    yaml = None


DEFAULT_CONFIG = {
    "project_prefix": "PROJ",
    "project_name": "Project",
    "statuses": ["proposed", "ready", "active", "blocked", "done", "deferred", "superseded"],
    "priorities": ["P0", "P1", "P2", "P3"],
    "types": {
        "epic": {"folder": "epics", "id_letter": "E", "parent": None},
        "feature": {"folder": "features", "id_letter": "F", "parent": "epic"},
        "story": {"folder": "stories", "id_letter": "S", "parent": "feature"},
        "task": {"folder": "tasks", "id_letter": "T", "parent": "story"},
    },
}
CHECKBOX_PATTERN = re.compile(r"^- \[[ xX]\] .+", re.MULTILINE)


class TrackerValidationError(ValueError):
    """Raised when tracker markdown is structurally invalid."""


@dataclass(frozen=True)
class WorkItem:
    path: Path
    metadata: dict[str, Any]
    body: str


@dataclass(frozen=True)
class WorkTracker:
    root: Path
    config: dict[str, Any]
    items: dict[str, WorkItem]

    def by_type(self, item_type: str) -> list[WorkItem]:
        return sorted(
            [item for item in self.items.values() if item.metadata["type"] == item_type],
            key=lambda item: item.metadata["id"],
        )


def load_tracker(work_root: Path | str) -> WorkTracker:
    root = Path(work_root)
    config = _load_config(root)
    items: dict[str, WorkItem] = {}

    for item_type, type_config in config["types"].items():
        folder = root / type_config["folder"]
        if not folder.exists():
            raise TrackerValidationError(f"Missing tracker folder: {folder}")
        for path in sorted(folder.glob("*.md")):
            metadata, body = _parse_frontmatter(path)
            item = WorkItem(path=path, metadata=metadata, body=body)
            _validate_basic_item(item, expected_type=item_type, config=config)
            item_id = metadata["id"]
            if item_id in items:
                raise TrackerValidationError(f"Duplicate work item id: {item_id}")
            items[item_id] = item

    _validate_relationships(items, config)
    return WorkTracker(root=root, config=config, items=items)


def format_summary(tracker: WorkTracker) -> str:
    statuses = tracker.config["statuses"]
    lines = [
        "# Work Tracker Summary",
        "",
        "| Type | " + " | ".join(_title(status) for status in statuses) + " | Total |",
        "| --- | " + " | ".join("---:" for _ in statuses) + " | ---: |",
    ]
    for item_type in tracker.config["types"]:
        items = tracker.by_type(item_type)
        counts = {status: 0 for status in statuses}
        for item in items:
            counts[item.metadata["status"]] += 1
        lines.append(
            "| "
            + item_type
            + " | "
            + " | ".join(str(counts[status]) for status in statuses)
            + f" | {len(items)} |"
        )

    lines.extend(["", "## Active And Ready Work", ""])
    visible_statuses = {"active", "ready", "blocked"}
    visible_items = [
        item
        for item in sorted(tracker.items.values(), key=lambda item: item.metadata["id"])
        if item.metadata["status"] in visible_statuses
    ]
    if not visible_items:
        lines.append("No active, ready, or blocked work items.")
    else:
        lines.extend(["| ID | Type | Status | Priority | Title |", "| --- | --- | --- | --- | --- |"])
        for item in visible_items:
            metadata = item.metadata
            lines.append(
                f"| {metadata['id']} | {metadata['type']} | {metadata['status']} | "
                f"{metadata['priority']} | {metadata['title']} |"
            )
    return "\n".join(lines) + "\n"


def format_mermaid(tracker: WorkTracker, focus_id: str | None = None) -> str:
    items = _focused_items(tracker, focus_id)
    lines = [
        "flowchart TD",
        "    classDef proposed fill:#f8f8f8,stroke:#999,color:#333;",
        "    classDef ready fill:#e9f5ff,stroke:#2f78c4,color:#10233f;",
        "    classDef active fill:#fff4d6,stroke:#b58100,color:#2f2300;",
        "    classDef blocked fill:#ffe0e0,stroke:#b00020,color:#3d0009;",
        "    classDef done fill:#e8f6ec,stroke:#207a3a,color:#0d2f17;",
        "    classDef deferred fill:#efebff,stroke:#6b4fc4,color:#24194f;",
        "    classDef superseded fill:#eeeeee,stroke:#666,color:#222;",
        "",
    ]
    for item in sorted(items, key=lambda item: item.metadata["id"]):
        metadata = item.metadata
        node_id = _node_id(metadata["id"])
        label = _escape_mermaid_label(f"{metadata['id']}\\n{metadata['title']}")
        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    class {node_id} {metadata['status']};")

    lines.append("")
    item_ids = {item.metadata["id"] for item in items}
    for item in sorted(items, key=lambda item: item.metadata["id"]):
        parent_id = item.metadata.get("parent")
        if isinstance(parent_id, str) and parent_id in item_ids:
            lines.append(f"    {_node_id(parent_id)} --> {_node_id(item.metadata['id'])}")
    return "\n".join(lines) + "\n"


def _load_config(root: Path) -> dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    config_path = root / "tracker.config.yaml"
    if config_path.exists():
        raw = _load_yaml(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise TrackerValidationError(f"{config_path}: config must be a mapping")
        config = _deep_merge(config, raw)
    _validate_config(config)
    return config


def _validate_config(config: dict[str, Any]) -> None:
    if not isinstance(config.get("project_prefix"), str) or not config["project_prefix"]:
        raise TrackerValidationError("project_prefix must be a non-empty string")
    if not isinstance(config.get("statuses"), list) or not config["statuses"]:
        raise TrackerValidationError("statuses must be a non-empty list")
    if not isinstance(config.get("priorities"), list) or not config["priorities"]:
        raise TrackerValidationError("priorities must be a non-empty list")
    if not isinstance(config.get("types"), dict) or not config["types"]:
        raise TrackerValidationError("types must be a non-empty mapping")


def _parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise TrackerValidationError(f"{path}: missing YAML frontmatter")
    try:
        _, raw_frontmatter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise TrackerValidationError(f"{path}: malformed YAML frontmatter") from exc
    metadata = _load_yaml(raw_frontmatter)
    if not isinstance(metadata, dict):
        raise TrackerValidationError(f"{path}: YAML frontmatter must be a mapping")
    return metadata, body


def _load_yaml(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text)
    return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> Any:
    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        return None
    value, index = _parse_mapping(lines, 0, _indent(lines[0]))
    if index != len(lines):
        raise TrackerValidationError("unsupported YAML structure")
    return value


def _parse_mapping(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        line_indent = _indent(line)
        stripped = line.strip()
        if line_indent < indent or stripped.startswith("- "):
            break
        if line_indent != indent or ":" not in stripped:
            raise TrackerValidationError(f"unsupported YAML line: {line}")
        key, raw_value = stripped.split(":", 1)
        raw_value = raw_value.strip()
        if raw_value:
            result[key] = _parse_scalar(raw_value)
            index += 1
            continue
        next_index = index + 1
        if next_index >= len(lines) or _indent(lines[next_index]) <= line_indent:
            result[key] = None
            index += 1
            continue
        next_indent = _indent(lines[next_index])
        if lines[next_index].strip().startswith("- "):
            result[key], index = _parse_list(lines, next_index, next_indent)
        else:
            result[key], index = _parse_mapping(lines, next_index, next_indent)
    return result, index


def _parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        line = lines[index]
        line_indent = _indent(line)
        stripped = line.strip()
        if line_indent < indent or not stripped.startswith("- "):
            break
        if line_indent != indent:
            raise TrackerValidationError(f"unsupported YAML list line: {line}")
        result.append(_parse_scalar(stripped[2:].strip()))
        index += 1
    return result, index


def _parse_scalar(raw: str) -> Any:
    if raw in {"", "null", "Null", "NULL", "~"}:
        return None
    if raw in {"true", "True", "TRUE"}:
        return True
    if raw in {"false", "False", "FALSE"}:
        return False
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    return raw


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _validate_basic_item(item: WorkItem, expected_type: str, config: dict[str, Any]) -> None:
    for field_name in ["id", "type", "title", "status", "parent", "created", "priority"]:
        if field_name not in item.metadata:
            raise TrackerValidationError(f"{item.path}: missing required field '{field_name}'")

    item_id = item.metadata["id"]
    type_config = config["types"][expected_type]
    expected_prefix = f"{config['project_prefix']}-{type_config['id_letter']}"
    if not isinstance(item_id, str) or not item_id.startswith(expected_prefix):
        raise TrackerValidationError(f"{item.path}: id must start with {expected_prefix}")
    if item.metadata["type"] != expected_type:
        raise TrackerValidationError(f"{item.path}: type must be {expected_type}")
    if item.metadata["status"] not in config["statuses"]:
        raise TrackerValidationError(f"{item.path}: invalid status {item.metadata['status']}")
    if item.metadata["priority"] not in config["priorities"]:
        raise TrackerValidationError(f"{item.path}: invalid priority {item.metadata['priority']}")
    if not item.metadata["title"]:
        raise TrackerValidationError(f"{item.path}: title cannot be empty")
    if "## Description" not in item.body:
        raise TrackerValidationError(f"{item.path}: missing Description section")
    if "## Acceptance Criteria" not in item.body:
        raise TrackerValidationError(f"{item.path}: missing Acceptance Criteria section")
    acceptance_body = item.body.split("## Acceptance Criteria", 1)[1]
    if not CHECKBOX_PATTERN.search(acceptance_body):
        raise TrackerValidationError(f"{item.path}: Acceptance Criteria section must contain checkboxes")
    if type_config.get("parent") is not None and not item.metadata["parent"]:
        raise TrackerValidationError(f"{item.path}: parent is required")
    if type_config.get("parent") is None and item.metadata["parent"] not in (None, ""):
        raise TrackerValidationError(f"{item.path}: parent must be empty")
    if expected_type != list(config["types"].keys())[-1] and "children" not in item.metadata:
        raise TrackerValidationError(f"{item.path}: non-leaf items must list children")


def _validate_relationships(items: dict[str, WorkItem], config: dict[str, Any]) -> None:
    parent_type_by_type = {item_type: type_config.get("parent") for item_type, type_config in config["types"].items()}

    for item in items.values():
        item_type = item.metadata["type"]
        item_id = item.metadata["id"]
        parent_type = parent_type_by_type[item_type]
        parent_id = item.metadata.get("parent")
        if parent_type is None:
            continue
        if not isinstance(parent_id, str) or parent_id not in items:
            raise TrackerValidationError(f"{item.path}: parent {parent_id!r} does not exist")
        parent = items[parent_id]
        if parent.metadata["type"] != parent_type:
            raise TrackerValidationError(f"{item.path}: parent {parent_id} must be a {parent_type}")
        if item_id not in (parent.metadata.get("children", []) or []):
            raise TrackerValidationError(f"{item.path}: parent {parent_id} does not list child {item_id}")

    for item in items.values():
        item_id = item.metadata["id"]
        children = item.metadata.get("children", []) or []
        if not isinstance(children, list):
            raise TrackerValidationError(f"{item.path}: children must be a list")
        for child_id in children:
            if child_id not in items:
                raise TrackerValidationError(f"{item.path}: child {child_id} does not exist")
            if items[child_id].metadata.get("parent") != item_id:
                raise TrackerValidationError(f"{item.path}: child {child_id} does not point back to {item_id}")


def _focused_items(tracker: WorkTracker, focus_id: str | None) -> list[WorkItem]:
    if focus_id is None:
        return list(tracker.items.values())
    if focus_id not in tracker.items:
        raise TrackerValidationError(f"focus id {focus_id!r} does not exist")

    focused: dict[str, WorkItem] = {}

    def add_descendants(item_id: str) -> None:
        item = tracker.items[item_id]
        focused[item_id] = item
        for child_id in item.metadata.get("children", []) or []:
            add_descendants(child_id)

    add_descendants(focus_id)
    return list(focused.values())


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _node_id(item_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", item_id)


def _escape_mermaid_label(label: str) -> str:
    return label.replace('"', "'")


def _title(value: str) -> str:
    return value.replace("_", " ").title()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize repo-native work tracker files.")
    parser.add_argument("work_root", nargs="?", default="docs/work", help="Path to the work tracker root.")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--summary", action="store_true", help="Print a Markdown status summary.")
    output_group.add_argument("--mermaid", action="store_true", help="Print a Mermaid hierarchy flowchart.")
    parser.add_argument("--focus", help="For Mermaid output, limit the chart to this item and descendants.")
    parser.add_argument("--output", help="Write output to a file instead of stdout.")
    args = parser.parse_args(argv)

    try:
        tracker = load_tracker(args.work_root)
        if args.summary:
            output = format_summary(tracker)
        elif args.mermaid:
            output = format_mermaid(tracker, focus_id=args.focus)
        else:
            output = f"Validated {len(tracker.items)} work items under {Path(args.work_root)}\n"
    except TrackerValidationError as exc:
        print(f"Work tracker validation failed: {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
