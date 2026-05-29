"""Module for test taius smoke."""
import importlib.util
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))
SKILLS_DIR = PROJECT_DIR / "main" / "taius" / "skills"


class NullConsole:

    """Test double that discards printed output."""
    def print(self, *args, **kwargs):
        """Execute print."""
        pass

    def rule(self, *args, **kwargs):
        """Execute rule."""
        pass


def load_skill_module(path):
    """Load a skill module from a file path."""
    spec = importlib.util.spec_from_file_location("test_skill_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TaiusSmokeTest(unittest.TestCase):

    """Smoke tests for packaged skills and router state."""
    def test_load_skills_ignores_template(self):
        """Verify template skills are ignored."""
        from taius.core.skills import load_skills

        skills = load_skills(NullConsole(), show_disabled=False)
        names = {skill["name"] for skill in skills}

        self.assertIn("echo_skill", names)
        self.assertIn("sentiment_skill", names)
        self.assertNotIn("_template", names)

    def test_skills_source_dir_points_to_packaged_skills(self):
        """Verify the packaged skills path."""
        from taius.core.paths import SKILLS_SOURCE_DIR

        self.assertEqual(Path(SKILLS_SOURCE_DIR).resolve(), SKILLS_DIR.resolve())

    def test_echo_skill_contract_and_predict(self):
        """Verify the echo skill contract and prediction."""
        module = load_skill_module(SKILLS_DIR / "echo_skill" / "skill.py")
        description = module.describe()

        self.assertEqual(description["id"], "core.echo")
        self.assertEqual(description["contract_version"], "1.0")
        self.assertEqual(description["input_type"], "text")
        self.assertEqual(description["output_type"], "text")
        self.assertEqual(module.predict("echo hello"), "hello")

    def test_skill_contract_fields(self):
        """Verify all skill contracts expose the required fields."""
        required_fields = {
            "id",
            "version",
            "contract_version",
            "input_type",
            "output_type",
        }

        for skill_path in SKILLS_DIR.glob("*/skill.py"):
            module = load_skill_module(skill_path)
            description = module.describe()

            for field in required_fields:
                self.assertIn(field, description, f"{skill_path} missing {field}")

    def test_router_threshold_config(self):
        """Verify the router threshold is within range."""
        import taius

        threshold = taius.get_routing_threshold()

        self.assertGreaterEqual(threshold, 0.0)
        self.assertLessEqual(threshold, 1.0)

    def test_template_contract(self):
        """Verify the template skill contract."""
        module = load_skill_module(SKILLS_DIR / "_template" / "skill.py")
        description = module.describe()

        self.assertEqual(description["contract_version"], "1.0")
        self.assertFalse(module.can_handle("anything"))


if __name__ == "__main__":
    unittest.main()
