#!/usr/bin/env python3
"""Deterministic quality gates for the architecture-copilot repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing required file: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


required_files = [
    "skills/architecture-copilot/SKILL.md",
    "skills/architecture-copilot/agents/openai.yaml",
    "skills/architecture-copilot/references/repository-review.md",
    "skills/architecture-copilot/assets/architecture-review-template.md",
    "skills/architecture-copilot/assets/adr-template.md",
    "skills/architecture-copilot/scripts/repo_inventory.py",
    "evals/cases.json",
    "evals/rubric.md",
    ".github/workflows/quality.yml",
    "AGENTS.md",
    ".cursor/rules/architecture-copilot.mdc",
]
for required in required_files:
    read(required)


skill = read("skills/architecture-copilot/SKILL.md")
if not skill.startswith("---\n"):
    errors.append("SKILL.md must start with YAML frontmatter")
else:
    parts = skill.split("---", 2)
    if len(parts) < 3:
        errors.append("SKILL.md frontmatter is not closed")
    else:
        frontmatter = parts[1]
        keys = set(re.findall(r"^([A-Za-z][A-Za-z0-9_-]*):", frontmatter, re.MULTILINE))
        if keys != {"name", "description"}:
            errors.append(
                "SKILL.md frontmatter must contain only name and description; "
                f"found {sorted(keys)}"
            )
        if not re.search(r'^name:\s*architecture-copilot\s*$', frontmatter, re.MULTILINE):
            errors.append("SKILL.md name must be architecture-copilot")


surfaces = {
    "SKILL.md": skill,
    "AGENTS.md": read("AGENTS.md"),
    "Cursor rule": read(".cursor/rules/architecture-copilot.mdc"),
}
shared_anchors = [
    "现有仓库架构体检",
    "已观察",
    "推断",
    "未知",
    "高杠杆",
    "可落地规格",
    "eval 门禁",
    "升级架构必须由信号触发",
    "八个阶段",
]
for surface_name, content in surfaces.items():
    for anchor in shared_anchors:
        if anchor not in content:
            errors.append(f"{surface_name} is missing shared capability anchor: {anchor}")
    if "修 bug" not in content or "不要" not in content:
        errors.append(f"{surface_name} must preserve the non-architecture implementation boundary")


openai_yaml = read("skills/architecture-copilot/agents/openai.yaml")
for field in ("display_name:", "short_description:", "default_prompt:"):
    if field not in openai_yaml:
        errors.append(f"agents/openai.yaml is missing {field}")
if "$architecture-copilot" not in openai_yaml:
    errors.append("agents/openai.yaml default_prompt must mention $architecture-copilot")


repository_review = read("skills/architecture-copilot/references/repository-review.md")
for anchor in ("先检查，后提问", "已观察", "推断", "未知", "主数据流", "杠杆参考值"):
    if anchor not in repository_review:
        errors.append(f"repository-review.md is missing workflow anchor: {anchor}")
if "scripts/repo_inventory.py" not in skill:
    errors.append("SKILL.md must route repository audits through the bundled inventory script")


catalog: dict[str, str] = {}
for line in skill.splitlines():
    if not line.startswith("|"):
        continue
    columns = [part.strip() for part in line.strip().strip("|").split("|")]
    if len(columns) != 4:
        continue
    slug, reference_pack = columns[1], columns[3]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        continue
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", reference_pack):
        errors.append(f"catalog row {slug} has invalid reference pack: {reference_pack}")
        continue
    if slug in catalog:
        errors.append(f"duplicate catalog slug: {slug}")
    catalog[slug] = reference_pack

if len(catalog) < 30:
    errors.append(f"expected at least 30 system catalog entries, found {len(catalog)}")

for slug, reference_pack in sorted(catalog.items()):
    relative = f"skills/architecture-copilot/references/{reference_pack}.md"
    reference = read(relative)
    if f"(`{slug}`)" not in reference:
        errors.append(f"catalog entry {slug} is not present in {reference_pack}.md")


try:
    cases = json.loads(read("evals/cases.json"))
except json.JSONDecodeError as exc:
    errors.append(f"evals/cases.json is invalid JSON: {exc}")
    cases = []

if not isinstance(cases, list):
    errors.append("evals/cases.json must contain a top-level list")
    cases = []
if len(cases) < 10:
    errors.append(f"expected at least 10 behavior eval cases, found {len(cases)}")

case_ids: set[str] = set()
categories: list[str] = []
for index, case in enumerate(cases):
    label = f"eval case #{index + 1}"
    if not isinstance(case, dict):
        errors.append(f"{label} must be an object")
        continue
    missing = {"id", "category", "prompt", "expected", "forbidden"} - set(case)
    if missing:
        errors.append(f"{label} is missing fields: {sorted(missing)}")
        continue
    case_id = case["id"]
    if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", case_id):
        errors.append(f"{label} has an invalid id: {case_id!r}")
    elif case_id in case_ids:
        errors.append(f"duplicate eval case id: {case_id}")
    else:
        case_ids.add(case_id)
    if not isinstance(case["category"], str):
        errors.append(f"{label} category must be a string")
    else:
        categories.append(case["category"])
    if not isinstance(case["prompt"], str) or not case["prompt"].strip():
        errors.append(f"{label} prompt must be a non-empty string")
    for field in ("expected", "forbidden"):
        value = case[field]
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{label} {field} must be a non-empty list of strings")

required_category_prefixes = [
    "trigger.forward-design",
    "trigger.review",
    "trigger.repository-audit",
    "trigger.evolution",
    "trigger.direct-solution",
    "non-trigger.implementation",
]
for prefix in required_category_prefixes:
    if not any(category.startswith(prefix) for category in categories):
        errors.append(f"behavior evals are missing category prefix: {prefix}")


rubric = read("evals/rubric.md")
for anchor in ("通过门槛", "失败", "证据", "独立"):
    if anchor not in rubric:
        errors.append(f"evals/rubric.md is missing rubric anchor: {anchor}")


stale_patterns = {
    "fixed Chinese tutorial count": r"26\s*章",
    "fixed Chinese template count": r"25\s*个模板",
    "fixed English tutorial count": r"26-chapter",
    "fixed English template count": r"25\s+templates",
}
readmes = read("README.md") + "\n" + read("README_en.md") + "\n" + read("INSTALL.md")
for label, pattern in stale_patterns.items():
    if re.search(pattern, readmes, re.IGNORECASE):
        errors.append(f"user-facing docs contain {label}; use upstream-relative wording")


if errors:
    print("quality checks failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    "quality checks passed: "
    f"{len(catalog)} catalog entries, {len(cases)} behavior eval cases, "
    f"{len(shared_anchors)} cross-surface anchors"
)
