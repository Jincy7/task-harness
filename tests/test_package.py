"""Offline package checks; run with python3 -m unittest discover -s tests -v."""
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/task-harness"
NAMES = {"task-scope", "task-build", "task-verify", "task-docs", "task-agents"}


class PackageTests(unittest.TestCase):
    def test_marketplace_resolves_the_declared_plugin(self):
        catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(catalog["name"], "jincy7-tools")
        self.assertEqual(len(catalog["plugins"]), 1)
        entry = catalog["plugins"][0]
        self.assertEqual(entry["source"]["source"], "local")
        target = (ROOT / entry["source"]["path"]).resolve()
        self.assertEqual(target, PLUGIN)
        manifest = json.loads((target / "plugin.json").read_text())
        self.assertEqual(manifest["name"], entry["name"])
        self.assertEqual(manifest["name"], "task-harness")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(set(manifest) - {"$schema", "name", "version", "description", "license"}, set())

    def test_five_explicit_skills(self):
        self.assertEqual({p.name for p in (PLUGIN / "skills").iterdir()}, NAMES)
        for name in NAMES:
            with self.subTest(skill=name):
                directory = PLUGIN / "skills" / name
                text = (directory / "SKILL.md").read_text()
                self.assertTrue(text.startswith("---\n"))
                frontmatter = text.split("---", 2)[1]
                self.assertIn(f"name: {name}\n", frontmatter)
                self.assertRegex(frontmatter, r"\ndescription: .+")
                policy = (directory / "agents/openai.yaml").read_text()
                self.assertRegex(policy, r"policy:\s*\n  allow_implicit_invocation: false\s*$")

    def test_each_copied_skill_has_all_its_references(self):
        for name in NAMES:
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as tmp:
                directory = (Path(tmp) / name).resolve()
                shutil.copytree(PLUGIN / "skills" / name, directory)
                for doc in directory.rglob("*.md"):
                    for link in re.findall(r"\]\(([^)]+)\)", doc.read_text()):
                        self.assertNotIn("://", link, "Skills must not need remote references")
                        path = (doc.parent / link.split("#")[0]).resolve()
                        self.assertTrue(path.is_relative_to(directory), link)
                        self.assertTrue(path.is_file(), link)

    def test_distribution_is_instructions_only(self):
        files = list(PLUGIN.rglob("*"))
        self.assertTrue(files)
        self.assertEqual((PLUGIN / "LICENSE").read_text(), (ROOT / "LICENSE").read_text())
        for path in files:
            self.assertFalse(path.is_symlink(), path)
            if path.is_file():
                if path.name != "LICENSE":
                    self.assertIn(path.suffix, {".md", ".yaml", ".json", ".svg"})
                self.assertNotIn(path.name, {"mcp.json", "hooks.json"})
                self.assertNotRegex(path.read_text(), r"시험|응시|예선|skhynix|mail\.google\.com")

    def test_readme_local_links_resolve(self):
        text = (ROOT / "README.md").read_text()
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((ROOT / link.split("#")[0]).is_file(), link)
        self.assertNotRegex(text, r"시험|응시|예선|skhynix|mail\.google\.com")

    def test_svg_is_standalone_without_active_content(self):
        paths = list((PLUGIN / "skills/task-docs/assets").glob("*.svg"))
        self.assertTrue(paths)
        for path in paths:
            root = ET.parse(path).getroot()
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("viewBox", root.attrib)
            for element in root.iter():
                tag = element.tag.split("}")[-1]
                self.assertNotIn(tag, {"script", "foreignObject", "image", "style"})
                for name, value in element.attrib.items():
                    local_name = name.split("}")[-1]
                    self.assertFalse(local_name.lower().startswith("on"))
                    if local_name == "href":
                        self.assertTrue(value.startswith("#"))
                    self.assertNotRegex(value, r"https?://|@import|url\(")


if __name__ == "__main__":
    unittest.main()
