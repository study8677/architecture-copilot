import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "architecture-copilot"
    / "scripts"
    / "repo_inventory.py"
)
SPEC = importlib.util.spec_from_file_location("repo_inventory", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load repo_inventory.py")
repo_inventory = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = repo_inventory
SPEC.loader.exec_module(repo_inventory)


def write_file(root, relative_path, content=""):
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def evidence_paths(inventory, key):
    return {item["path"] for item in inventory[key]}


class RepositoryInventoryTests(unittest.TestCase):
    def test_detects_repository_architecture_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_file(root, "src/main.py", "print('hello')\n")
            write_file(root, "src/app.ts", "export const app = true;\n")
            write_file(root, "apps/web/app/page.tsx", "export default function Page() {}\n")
            write_file(
                root,
                "package.json",
                json.dumps({"name": "fixture", "main": "src/app.ts"}),
            )
            write_file(root, "package-lock.json", "{}\n")
            write_file(root, "pyproject.toml", "[project]\nname = 'fixture'\n")
            write_file(root, "migrations/001_init.sql", "create table example(id int);\n")
            write_file(root, ".github/workflows/ci.yml", "name: CI\n")
            write_file(root, "Dockerfile", "FROM scratch\n")
            write_file(root, "tests/test_app.py", "def test_app():\n    assert True\n")
            write_file(root, "README.md", "# Fixture\n")
            write_file(root, "docs/architecture.md", "# Architecture\n")

            inventory = repo_inventory.build_inventory(root)

            top_level = {item["path"] for item in inventory["top_level_structure"]}
            self.assertIn("src", top_level)
            self.assertIn("migrations", top_level)

            languages = {
                item["language"]: item["files"]
                for item in inventory["language_distribution"]
            }
            self.assertEqual(languages["Python"], 2)
            self.assertEqual(languages["TypeScript"], 2)
            self.assertEqual(languages["SQL"], 1)

            self.assertEqual(
                evidence_paths(inventory, "manifests"),
                {"package.json", "pyproject.toml"},
            )
            self.assertEqual(
                evidence_paths(inventory, "lockfiles"), {"package-lock.json"}
            )
            self.assertIn("src/main.py", evidence_paths(inventory, "entry_candidates"))
            self.assertIn("src/app.ts", evidence_paths(inventory, "entry_candidates"))
            self.assertIn(
                "apps/web/app/page.tsx", evidence_paths(inventory, "entry_candidates")
            )
            self.assertIn("migrations", evidence_paths(inventory, "data_and_migrations"))
            self.assertIn(
                "migrations/001_init.sql",
                evidence_paths(inventory, "data_and_migrations"),
            )
            self.assertIn(
                ".github/workflows/ci.yml",
                evidence_paths(inventory, "deployment_and_ci"),
            )
            self.assertIn("Dockerfile", evidence_paths(inventory, "deployment_and_ci"))
            self.assertIn("tests/test_app.py", evidence_paths(inventory, "tests"))
            self.assertIn("README.md", evidence_paths(inventory, "documentation"))
            self.assertIn(
                "docs/architecture.md", evidence_paths(inventory, "documentation")
            )

    def test_ignored_directories_are_pruned_from_all_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_file(root, "src/main.py", "print('kept')\n")
            ignored_files = (
                ".next/server/app.js",
                ".git/config",
                ".venv/lib/ghost.py",
                "build/generated.py",
                "dist/bundle.js",
                "node_modules/pkg/index.js",
                "vendor/library.rb",
            )
            for relative_path in ignored_files:
                write_file(root, relative_path, "ignored\n")

            inventory = repo_inventory.build_inventory(root)
            serialised = repo_inventory.render_json(inventory)

            for relative_path in ignored_files:
                self.assertNotIn(relative_path, serialised)
            self.assertEqual(inventory["summary"]["files_scanned"], 1)
            self.assertEqual(
                set(inventory["ignored_directories"]),
                {".next", ".git", ".venv", "build", "dist", "node_modules", "vendor"},
            )
            self.assertEqual(
                inventory["language_distribution"][0]["language"], "Python"
            )
            self.assertEqual(inventory["language_distribution"][0]["files"], 1)

    def test_cli_supports_json_and_markdown_output(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_file(root, "README.md", "# Fixture\n")

            json_stdout = io.StringIO()
            with redirect_stdout(json_stdout):
                exit_code = repo_inventory.main([str(root), "--format", "json"])
            self.assertEqual(exit_code, 0)
            json_payload = json.loads(json_stdout.getvalue())
            self.assertEqual(json_payload["root"], str(root.resolve()))
            self.assertIn("documentation", json_payload)

            markdown_stdout = io.StringIO()
            with redirect_stdout(markdown_stdout):
                exit_code = repo_inventory.main(
                    [str(root), "--format", "markdown"]
                )
            self.assertEqual(exit_code, 0)
            markdown = markdown_stdout.getvalue()
            self.assertIn("# Repository inventory", markdown)
            self.assertIn("## Language distribution", markdown)
            self.assertIn("## Deployment and CI", markdown)
            self.assertIn("README.md", markdown)


if __name__ == "__main__":
    unittest.main()
