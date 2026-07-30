import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "manifest-generator.py"
SPEC = importlib.util.spec_from_file_location("manifest_generator", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load manifest generator")
manifest_generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest_generator)


class ManifestGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.skills_directory = self.root / "skills"
        self.registry_directory = self.root / "_registry"
        self.manifest_path = self.registry_directory / "manifest.yaml"

        self.original_paths = (
            manifest_generator.SKILLS_DIR,
            manifest_generator.REGISTRY_DIR,
            manifest_generator.MANIFEST_PATH,
        )
        manifest_generator.SKILLS_DIR = self.skills_directory
        manifest_generator.REGISTRY_DIR = self.registry_directory
        manifest_generator.MANIFEST_PATH = self.manifest_path

    def tearDown(self):
        (
            manifest_generator.SKILLS_DIR,
            manifest_generator.REGISTRY_DIR,
            manifest_generator.MANIFEST_PATH,
        ) = self.original_paths
        self.temp_directory.cleanup()

    def write_skill(self, directory_name, skill_id):
        skill_directory = self.skills_directory / "tools" / directory_name
        skill_directory.mkdir(parents=True)
        (skill_directory / "SKILL.md").write_text(
            "---\n"
            f"id: {skill_id}\n"
            f"name: {directory_name}\n"
            "category: tools\n"
            "tags: []\n"
            "goals:\n"
            "  - Keep the manifest unambiguous for consumers.\n"
            "---\n"
            f"# {directory_name}\n",
            encoding="utf-8",
        )

    def test_duplicate_ids_stop_generation_before_manifest_write(self):
        self.write_skill("first-skill", "shared-id")
        self.write_skill("second-skill", "shared-id")
        self.registry_directory.mkdir()
        self.manifest_path.write_text("existing manifest\n", encoding="utf-8")
        output = io.StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            manifest_generator.generate_manifest()

        self.assertEqual(1, raised.exception.code)
        self.assertEqual(
            "existing manifest\n",
            self.manifest_path.read_text(encoding="utf-8"),
        )
        self.assertIn("Duplicate skill id 'shared-id'", output.getvalue())
        self.assertIn("skills/tools/first-skill", output.getvalue())
        self.assertIn("skills/tools/second-skill", output.getvalue())

    def test_falsey_non_mapping_frontmatter_is_rejected(self):
        skill_directory = self.skills_directory / "tools" / "invalid-skill"
        skill_directory.mkdir(parents=True)
        skill_path = skill_directory / "SKILL.md"

        for frontmatter in ("[]", "false", "0", '""', "null"):
            with self.subTest(frontmatter=frontmatter):
                skill_path.write_text(
                    f"---\n{frontmatter}\n---\n# Invalid\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    TypeError,
                    "Frontmatter must be a mapping",
                ):
                    manifest_generator.parse_skill_file(skill_path)


if __name__ == "__main__":
    unittest.main()
