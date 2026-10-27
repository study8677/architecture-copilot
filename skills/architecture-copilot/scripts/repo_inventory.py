#!/usr/bin/env python3
"""Produce a read-only, evidence-oriented inventory of a repository.

The inventory intentionally relies on file and directory names instead of
executing project code.  It is therefore safe to use as the reconnaissance
step of an architecture review.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Union


JSONDict = Dict[str, Any]

IGNORED_DIRECTORY_NAMES: Set[str] = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".next",
    ".playwright-cli",
    ".pytest_cache",
    ".ruff_cache",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "out",
    "target",
    "vendor",
}

LANGUAGE_EXTENSIONS: Mapping[str, str] = {
    ".adoc": "AsciiDoc",
    ".astro": "Astro",
    ".bash": "Shell",
    ".c": "C",
    ".cc": "C++",
    ".clj": "Clojure",
    ".cljs": "Clojure",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".cxx": "C++",
    ".dart": "Dart",
    ".eex": "Elixir",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".fish": "Shell",
    ".fs": "F#",
    ".fsx": "F#",
    ".go": "Go",
    ".h": "C/C++ Header",
    ".hpp": "C/C++ Header",
    ".hrl": "Erlang",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".json": "JSON",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".less": "Less",
    ".lua": "Lua",
    ".md": "Markdown",
    ".mjs": "JavaScript",
    ".mm": "Objective-C++",
    ".m": "Objective-C",
    ".php": "PHP",
    ".pl": "Perl",
    ".pm": "Perl",
    ".proto": "Protocol Buffers",
    ".py": "Python",
    ".r": "R",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".rst": "reStructuredText",
    ".sass": "Sass",
    ".scala": "Scala",
    ".scss": "SCSS",
    ".sh": "Shell",
    ".sol": "Solidity",
    ".sql": "SQL",
    ".svelte": "Svelte",
    ".swift": "Swift",
    ".tf": "Terraform",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".vue": "Vue",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".zsh": "Shell",
}

MANIFEST_FILES: Mapping[str, str] = {
    "build.gradle": "Gradle",
    "build.gradle.kts": "Gradle",
    "cargo.toml": "Rust",
    "cmakelists.txt": "C/C++",
    "composer.json": "PHP",
    "deno.json": "Deno",
    "deno.jsonc": "Deno",
    "environment.yml": "Python",
    "environment.yaml": "Python",
    "gemfile": "Ruby",
    "go.mod": "Go",
    "mix.exs": "Elixir",
    "package.json": "Node.js",
    "package.swift": "Swift",
    "pipfile": "Python",
    "podfile": "CocoaPods",
    "pom.xml": "Maven",
    "pubspec.yaml": "Dart",
    "pyproject.toml": "Python",
    "setup.cfg": "Python",
    "setup.py": "Python",
}

LOCK_FILES: Mapping[str, str] = {
    "bun.lock": "Bun",
    "bun.lockb": "Bun",
    "cargo.lock": "Rust",
    "composer.lock": "PHP",
    "gemfile.lock": "Ruby",
    "go.sum": "Go",
    "gradle.lockfile": "Gradle",
    "mix.lock": "Elixir",
    "package-lock.json": "npm",
    "package.resolved": "Swift",
    "packages.lock.json": ".NET",
    "pipfile.lock": "Python",
    "pnpm-lock.yaml": "pnpm",
    "podfile.lock": "CocoaPods",
    "poetry.lock": "Python",
    "pubspec.lock": "Dart",
    "uv.lock": "Python",
    "yarn.lock": "Yarn",
}

ENTRY_FILE_REASONS: Mapping[str, str] = {
    "__main__.py": "Python module entry point",
    "app.js": "common application entry filename",
    "app.py": "common application entry filename",
    "app.ts": "common application entry filename",
    "asgi.py": "ASGI application entry point",
    "cli.py": "command-line entry filename",
    "index.html": "web application document entry",
    "index.js": "common JavaScript entry filename",
    "index.ts": "common TypeScript entry filename",
    "main.go": "Go executable entry filename",
    "main.java": "Java application entry filename",
    "main.js": "common JavaScript entry filename",
    "main.jsx": "common React entry filename",
    "main.py": "common Python entry filename",
    "main.rs": "Rust executable entry filename",
    "main.ts": "common TypeScript entry filename",
    "main.tsx": "common React entry filename",
    "manage.py": "framework management entry point",
    "program.cs": ".NET application entry filename",
    "server.js": "common server entry filename",
    "server.py": "common server entry filename",
    "server.ts": "common server entry filename",
    "wsgi.py": "WSGI application entry point",
}

INDEX_ENTRY_PARENTS: Set[str] = {
    ".",
    "app",
    "client",
    "frontend",
    "public",
    "server",
    "src",
    "web",
}

DATA_DIRECTORY_NAMES: Set[str] = {
    "alembic",
    "data",
    "database",
    "db",
    "fixtures",
    "migration",
    "migrations",
    "prisma",
    "schema",
    "schemas",
    "seed",
    "seeds",
}

DATA_FILE_NAMES: Mapping[str, str] = {
    "alembic.ini": "Alembic migration configuration",
    "database.yml": "database configuration",
    "database.yaml": "database configuration",
    "drizzle.config.js": "Drizzle schema/migration configuration",
    "drizzle.config.ts": "Drizzle schema/migration configuration",
    "knexfile.js": "Knex migration configuration",
    "knexfile.ts": "Knex migration configuration",
    "schema.prisma": "Prisma data schema",
    "schema.sql": "SQL data schema",
}

TEST_DIRECTORY_NAMES: Set[str] = {
    "__tests__",
    "e2e",
    "integration",
    "spec",
    "specs",
    "test",
    "tests",
}

TEST_CONFIG_NAMES: Set[str] = {
    "conftest.py",
    "jest.config.js",
    "jest.config.mjs",
    "jest.config.ts",
    "playwright.config.js",
    "playwright.config.ts",
    "pytest.ini",
    "tox.ini",
    "vitest.config.js",
    "vitest.config.ts",
}

DOCUMENTATION_DIRECTORY_NAMES: Set[str] = {
    "adr",
    "adrs",
    "architecture",
    "doc",
    "docs",
    "documentation",
}

DOCUMENTATION_FILE_PREFIXES: Tuple[str, ...] = (
    "agents",
    "architecture",
    "changelog",
    "contributing",
    "design",
    "readme",
    "security",
    "skill",
)


@dataclass(frozen=True)
class RepositoryScan:
    """Filesystem paths discovered without crossing ignored directories."""

    root: Path
    files: Tuple[Path, ...]
    directories: Tuple[Path, ...]
    ignored_directories: Tuple[str, ...]


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def scan_repository(root: Union[str, Path]) -> RepositoryScan:
    """Walk *root* without following symlinks or entering generated trees."""

    root_path = Path(root).expanduser().resolve()
    if not root_path.exists():
        raise ValueError("repository root does not exist: {0}".format(root_path))
    if not root_path.is_dir():
        raise ValueError("repository root is not a directory: {0}".format(root_path))

    files: List[Path] = []
    directories: List[Path] = []
    ignored: Set[str] = set()

    def ignore_walk_error(_error: OSError) -> None:
        return None

    for current, dirnames, filenames in os.walk(
        str(root_path), topdown=True, onerror=ignore_walk_error, followlinks=False
    ):
        current_path = Path(current)
        kept_directories: List[str] = []

        for name in sorted(dirnames, key=str.casefold):
            candidate = current_path / name
            relative = _relative(candidate, root_path)
            if name.casefold() in IGNORED_DIRECTORY_NAMES:
                ignored.add(relative)
                continue
            if candidate.is_symlink():
                continue
            kept_directories.append(name)
            directories.append(candidate)

        dirnames[:] = kept_directories

        for name in sorted(filenames, key=str.casefold):
            candidate = current_path / name
            if candidate.is_symlink():
                continue
            try:
                if candidate.is_file():
                    files.append(candidate)
            except OSError:
                continue

    return RepositoryScan(
        root=root_path,
        files=tuple(sorted(files, key=lambda path: _relative(path, root_path).casefold())),
        directories=tuple(
            sorted(directories, key=lambda path: _relative(path, root_path).casefold())
        ),
        ignored_directories=tuple(sorted(ignored, key=str.casefold)),
    )


def _safe_size(path: Path) -> int:
    try:
        return path.lstat().st_size
    except OSError:
        return 0


def _top_level_structure(scan: RepositoryScan) -> List[JSONDict]:
    file_counts: Counter[str] = Counter()
    byte_counts: Counter[str] = Counter()
    for path in scan.files:
        relative = path.relative_to(scan.root)
        top_name = relative.parts[0]
        file_counts[top_name] += 1
        byte_counts[top_name] += _safe_size(path)

    entries: List[JSONDict] = []
    try:
        children = sorted(scan.root.iterdir(), key=lambda path: path.name.casefold())
    except OSError:
        children = []

    for child in children:
        if child.name.casefold() in IGNORED_DIRECTORY_NAMES:
            continue
        if child.is_symlink():
            kind = "symlink"
        elif child.is_dir():
            kind = "directory"
        elif child.is_file():
            kind = "file"
        else:
            kind = "other"
        entries.append(
            {
                "path": child.name,
                "type": kind,
                "files": file_counts.get(child.name, 0),
                "bytes": byte_counts.get(child.name, 0),
            }
        )
    return entries


def _language_for_path(path: Path) -> Optional[str]:
    name = path.name.casefold()
    if name == "makefile" or name.startswith("makefile."):
        return "Makefile"
    if name == "dockerfile" or name.startswith("dockerfile."):
        return "Dockerfile"
    return LANGUAGE_EXTENSIONS.get(path.suffix.casefold())


def _language_distribution(scan: RepositoryScan) -> List[JSONDict]:
    file_counts: Counter[str] = Counter()
    byte_counts: Counter[str] = Counter()

    for path in scan.files:
        language = _language_for_path(path)
        if language is None:
            continue
        file_counts[language] += 1
        byte_counts[language] += _safe_size(path)

    total = sum(file_counts.values())
    distribution = [
        {
            "language": language,
            "files": count,
            "bytes": byte_counts[language],
            "share_percent": round((count / total) * 100, 1) if total else 0.0,
        }
        for language, count in file_counts.items()
    ]
    return sorted(
        distribution,
        key=lambda item: (-item["files"], -item["bytes"], item["language"].casefold()),
    )


def _manifest_kind(path: Path) -> Optional[Tuple[str, str]]:
    name = path.name.casefold()
    if name in MANIFEST_FILES:
        return "manifest", MANIFEST_FILES[name]
    if name in LOCK_FILES:
        return "lockfile", LOCK_FILES[name]
    if name.startswith("requirements") and path.suffix.casefold() in {".in", ".txt"}:
        return "manifest", "Python"
    if path.suffix.casefold() in {".csproj", ".fsproj", ".sln", ".vbproj"}:
        return "manifest", ".NET"
    return None


def _dependency_evidence(scan: RepositoryScan) -> Tuple[List[JSONDict], List[JSONDict]]:
    manifests: List[JSONDict] = []
    lockfiles: List[JSONDict] = []
    for path in scan.files:
        kind = _manifest_kind(path)
        if kind is None:
            continue
        item = {"path": _relative(path, scan.root), "ecosystem": kind[1]}
        if kind[0] == "manifest":
            manifests.append(item)
        else:
            lockfiles.append(item)
    return manifests, lockfiles


def _normalise_manifest_target(manifest_path: str, target: str) -> Optional[str]:
    target = target.strip().replace("\\", "/")
    if not target or target.startswith("/"):
        return None
    parent = posixpath.dirname(manifest_path)
    normalised = posixpath.normpath(posixpath.join(parent, target))
    if normalised == ".." or normalised.startswith("../"):
        return None
    return normalised.removeprefix("./")


def _package_entry_targets(path: Path, scan: RepositoryScan) -> Iterable[Tuple[str, str]]:
    """Yield existing files referenced by simple package.json entry fields."""

    try:
        if _safe_size(path) > 1_000_000:
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict):
        return []

    raw_targets: List[Tuple[str, str]] = []
    for field in ("main", "module"):
        value = payload.get(field)
        if isinstance(value, str):
            raw_targets.append((field, value))

    bin_value = payload.get("bin")
    if isinstance(bin_value, str):
        raw_targets.append(("bin", bin_value))
    elif isinstance(bin_value, dict):
        for value in bin_value.values():
            if isinstance(value, str):
                raw_targets.append(("bin", value))

    manifest_relative = _relative(path, scan.root)
    existing = {_relative(candidate, scan.root) for candidate in scan.files}
    results: List[Tuple[str, str]] = []
    for field, raw_target in raw_targets:
        target = _normalise_manifest_target(manifest_relative, raw_target)
        if target is None:
            continue
        candidates = (
            target,
            target + ".js",
            target + ".ts",
            posixpath.join(target, "index.js"),
            posixpath.join(target, "index.ts"),
        )
        for candidate in candidates:
            if candidate in existing:
                results.append(
                    (
                        candidate,
                        "referenced by {0} field in {1}".format(field, manifest_relative),
                    )
                )
                break
    return results


def _entry_candidates(scan: RepositoryScan) -> List[JSONDict]:
    candidates: Dict[str, Tuple[int, str]] = {}

    def add(path: str, score: int, reason: str) -> None:
        current = candidates.get(path)
        if current is None or score > current[0]:
            candidates[path] = (score, reason)

    for path in scan.files:
        relative = _relative(path, scan.root)
        name = path.name.casefold()
        reason = ENTRY_FILE_REASONS.get(name)
        if reason is not None:
            parent_name = path.parent.name.casefold() if path.parent != scan.root else "."
            if name.startswith("index.") and parent_name not in INDEX_ENTRY_PARENTS:
                continue
            score = 90 if name in {"__main__.py", "manage.py", "wsgi.py", "asgi.py"} else 70
            add(relative, score, reason)

        relative_parts = tuple(part.casefold() for part in path.relative_to(scan.root).parts)
        if len(relative_parts) >= 2 and relative_parts[0] == "bin":
            add(relative, 75, "file in top-level bin directory")
        if name == "main.go" and "cmd" in relative_parts:
            add(relative, 85, "Go command entry under cmd directory")
        if relative_parts == ("src", "main.rs"):
            add(relative, 85, "Rust binary entry at src/main.rs")
        if len(relative_parts) >= 2 and relative_parts[-2:] in {
            ("app", "page.jsx"),
            ("app", "page.tsx"),
            ("pages", "index.jsx"),
            ("pages", "index.tsx"),
        }:
            add(relative, 85, "framework web route entry")

        if name == "package.json":
            for target, package_reason in _package_entry_targets(path, scan):
                add(target, 100, package_reason)

    return [
        {"path": path, "evidence": score_and_reason[1]}
        for path, score_and_reason in sorted(
            candidates.items(), key=lambda item: (-item[1][0], item[0].casefold())
        )
    ]


def _data_and_migrations(scan: RepositoryScan) -> List[JSONDict]:
    evidence: Dict[str, JSONDict] = {}

    for path in scan.directories:
        if path.name.casefold() in DATA_DIRECTORY_NAMES:
            relative = _relative(path, scan.root)
            evidence[relative] = {
                "path": relative,
                "type": "directory",
                "evidence": "data, schema, seed, or migration directory name",
            }

    for path in scan.files:
        relative = _relative(path, scan.root)
        name = path.name.casefold()
        reason = DATA_FILE_NAMES.get(name)
        if reason is None and path.suffix.casefold() in {".db", ".prisma", ".sql", ".sqlite", ".sqlite3"}:
            reason = "database, schema, or migration file extension"
        if reason is not None:
            evidence[relative] = {"path": relative, "type": "file", "evidence": reason}

    return [evidence[path] for path in sorted(evidence, key=str.casefold)]


def _deployment_and_ci(scan: RepositoryScan) -> List[JSONDict]:
    evidence: Dict[str, JSONDict] = {}
    infrastructure_directories = {
        "charts",
        "deploy",
        "deployment",
        "helm",
        "infra",
        "infrastructure",
        "k8s",
        "kubernetes",
        "terraform",
    }

    for path in scan.directories:
        if path.name.casefold() in infrastructure_directories:
            relative = _relative(path, scan.root)
            evidence[relative] = {
                "path": relative,
                "category": "deployment",
                "evidence": "infrastructure or deployment directory name",
            }

    for path in scan.files:
        relative = _relative(path, scan.root)
        parts = tuple(part.casefold() for part in path.relative_to(scan.root).parts)
        name = path.name.casefold()
        suffix = path.suffix.casefold()
        item: Optional[JSONDict] = None

        if len(parts) >= 3 and parts[0:2] == (".github", "workflows"):
            item = {"path": relative, "category": "ci", "evidence": "GitHub Actions workflow"}
        elif ".circleci" in parts:
            item = {"path": relative, "category": "ci", "evidence": "CircleCI configuration"}
        elif name in {
            ".gitlab-ci.yml",
            ".gitlab-ci.yaml",
            "azure-pipelines.yml",
            "azure-pipelines.yaml",
            "bitbucket-pipelines.yml",
            "buildkite.yml",
            "jenkinsfile",
        }:
            item = {"path": relative, "category": "ci", "evidence": "CI configuration filename"}
        elif name == "dockerfile" or name.startswith("dockerfile."):
            item = {"path": relative, "category": "deployment", "evidence": "container build file"}
        elif name.startswith("docker-compose.") or name.startswith("compose."):
            item = {"path": relative, "category": "deployment", "evidence": "container composition file"}
        elif suffix == ".tf":
            item = {"path": relative, "category": "deployment", "evidence": "Terraform configuration"}
        elif name in {
            "app.yaml",
            "cloudbuild.yaml",
            "cloudbuild.yml",
            "fly.toml",
            "netlify.toml",
            "nixpacks.toml",
            "procfile",
            "railway.json",
            "render.yaml",
            "render.yml",
            "serverless.yaml",
            "serverless.yml",
            "vercel.json",
            "wrangler.toml",
        }:
            item = {"path": relative, "category": "deployment", "evidence": "deployment platform configuration"}
        elif any(part in infrastructure_directories for part in parts[:-1]) and suffix in {
            ".json",
            ".toml",
            ".yaml",
            ".yml",
        }:
            item = {"path": relative, "category": "deployment", "evidence": "configuration under infrastructure directory"}

        if item is not None:
            evidence[relative] = item

    return [evidence[path] for path in sorted(evidence, key=str.casefold)]


def _is_test_filename(name: str) -> bool:
    lower = name.casefold()
    stem = Path(lower).stem
    return (
        lower.startswith("test_")
        or stem.endswith("_test")
        or ".test." in lower
        or ".spec." in lower
        or lower.endswith("_spec.rb")
        or (lower.startswith("test") and lower.endswith(".java"))
    )


def _test_evidence(scan: RepositoryScan) -> List[JSONDict]:
    evidence: Dict[str, JSONDict] = {}

    for path in scan.directories:
        if path.name.casefold() in TEST_DIRECTORY_NAMES:
            relative = _relative(path, scan.root)
            evidence[relative] = {
                "path": relative,
                "type": "directory",
                "evidence": "test directory name",
            }

    for path in scan.files:
        relative = _relative(path, scan.root)
        parts = tuple(part.casefold() for part in path.relative_to(scan.root).parts[:-1])
        if path.name.casefold() in TEST_CONFIG_NAMES:
            reason = "test framework configuration"
        elif any(part in TEST_DIRECTORY_NAMES for part in parts):
            reason = "file under test directory"
        elif _is_test_filename(path.name):
            reason = "test filename pattern"
        else:
            continue
        evidence[relative] = {"path": relative, "type": "file", "evidence": reason}

    return [evidence[path] for path in sorted(evidence, key=str.casefold)]


def _documentation_evidence(scan: RepositoryScan) -> List[JSONDict]:
    evidence: Dict[str, JSONDict] = {}

    for path in scan.directories:
        if path.name.casefold() in DOCUMENTATION_DIRECTORY_NAMES:
            relative = _relative(path, scan.root)
            evidence[relative] = {
                "path": relative,
                "type": "directory",
                "evidence": "documentation or architecture directory name",
            }

    for path in scan.files:
        relative = _relative(path, scan.root)
        lower_name = path.name.casefold()
        parent_parts = tuple(part.casefold() for part in path.relative_to(scan.root).parts[:-1])
        reason: Optional[str] = None
        if any(part in DOCUMENTATION_DIRECTORY_NAMES for part in parent_parts):
            reason = "file under documentation or architecture directory"
        elif lower_name.startswith(DOCUMENTATION_FILE_PREFIXES):
            reason = "well-known project documentation filename"
        elif path.suffix.casefold() in {".adoc", ".md", ".rst"}:
            reason = "documentation markup file"
        elif lower_name in {"docusaurus.config.js", "mkdocs.yml", "mkdocs.yaml"}:
            reason = "documentation site configuration"
        if reason is not None:
            evidence[relative] = {"path": relative, "type": "file", "evidence": reason}

    return [evidence[path] for path in sorted(evidence, key=str.casefold)]


def build_inventory(root: Union[str, Path]) -> JSONDict:
    """Return a JSON-serialisable repository inventory."""

    scan = scan_repository(root)
    manifests, lockfiles = _dependency_evidence(scan)
    return {
        "schema_version": 1,
        "root": str(scan.root),
        "summary": {
            "files_scanned": len(scan.files),
            "directories_scanned": len(scan.directories),
            "ignored_directories": len(scan.ignored_directories),
        },
        "top_level_structure": _top_level_structure(scan),
        "language_distribution": _language_distribution(scan),
        "manifests": manifests,
        "lockfiles": lockfiles,
        "entry_candidates": _entry_candidates(scan),
        "data_and_migrations": _data_and_migrations(scan),
        "deployment_and_ci": _deployment_and_ci(scan),
        "tests": _test_evidence(scan),
        "documentation": _documentation_evidence(scan),
        "ignored_directories": list(scan.ignored_directories),
        "ignored_directory_names": sorted(IGNORED_DIRECTORY_NAMES, key=str.casefold),
    }


def render_json(inventory: Mapping[str, Any]) -> str:
    """Render an inventory as stable, human-readable JSON."""

    return json.dumps(inventory, ensure_ascii=False, indent=2)


def _markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _markdown_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    rendered_rows = list(rows)
    if not rendered_rows:
        return "_None detected._"
    lines = [
        "| " + " | ".join(_markdown_escape(header) for header in headers) + " |",
        "| " + " | ".join("---" for _header in headers) + " |",
    ]
    for row in rendered_rows:
        lines.append("| " + " | ".join(_markdown_escape(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown(inventory: Mapping[str, Any]) -> str:
    """Render an inventory as a compact evidence report."""

    summary = inventory["summary"]
    sections = [
        "# Repository inventory",
        "",
        "- Root: `{0}`".format(inventory["root"]),
        "- Files scanned: {0}".format(summary["files_scanned"]),
        "- Directories scanned: {0}".format(summary["directories_scanned"]),
        "- Ignored directories encountered: {0}".format(summary["ignored_directories"]),
        "",
        "## Top-level structure",
        "",
        _markdown_table(
            ("Path", "Type", "Files", "Bytes"),
            (
                (item["path"], item["type"], item["files"], item["bytes"])
                for item in inventory["top_level_structure"]
            ),
        ),
        "",
        "## Language distribution",
        "",
        _markdown_table(
            ("Language", "Files", "Bytes", "Share"),
            (
                (
                    item["language"],
                    item["files"],
                    item["bytes"],
                    "{0:.1f}%".format(item["share_percent"]),
                )
                for item in inventory["language_distribution"]
            ),
        ),
        "",
        "## Manifests and lockfiles",
        "",
        _markdown_table(
            ("Path", "Kind", "Ecosystem"),
            [
                (item["path"], "manifest", item["ecosystem"])
                for item in inventory["manifests"]
            ]
            + [
                (item["path"], "lockfile", item["ecosystem"])
                for item in inventory["lockfiles"]
            ],
        ),
        "",
        "## Entry candidates",
        "",
        _markdown_table(
            ("Path", "Evidence"),
            ((item["path"], item["evidence"]) for item in inventory["entry_candidates"]),
        ),
        "",
        "## Data and migrations",
        "",
        _markdown_table(
            ("Path", "Type", "Evidence"),
            (
                (item["path"], item["type"], item["evidence"])
                for item in inventory["data_and_migrations"]
            ),
        ),
        "",
        "## Deployment and CI",
        "",
        _markdown_table(
            ("Path", "Category", "Evidence"),
            (
                (item["path"], item["category"], item["evidence"])
                for item in inventory["deployment_and_ci"]
            ),
        ),
        "",
        "## Tests",
        "",
        _markdown_table(
            ("Path", "Type", "Evidence"),
            ((item["path"], item["type"], item["evidence"]) for item in inventory["tests"]),
        ),
        "",
        "## Documentation",
        "",
        _markdown_table(
            ("Path", "Type", "Evidence"),
            (
                (item["path"], item["type"], item["evidence"])
                for item in inventory["documentation"]
            ),
        ),
        "",
        "## Ignored directories",
        "",
        "\n".join("- `{0}`".format(path) for path in inventory["ignored_directories"])
        if inventory["ignored_directories"]
        else "_None encountered._",
    ]
    return "\n".join(sections) + "\n"


def _directory_argument(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.exists():
        raise argparse.ArgumentTypeError("root does not exist: {0}".format(path))
    if not path.is_dir():
        raise argparse.ArgumentTypeError("root is not a directory: {0}".format(path))
    return path


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only repository inventory for architecture reconnaissance."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=Path("."),
        type=_directory_argument,
        help="repository root to inspect (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format (default: markdown)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    inventory = build_inventory(args.root)
    if args.format == "json":
        print(render_json(inventory))
    else:
        print(render_markdown(inventory), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
