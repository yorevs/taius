"""Module for test skill management."""
import shutil
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))
SKILLS_DIR = PROJECT_DIR / "main" / "taius" / "skills"
SKILLS_MODEL_DIR = PROJECT_DIR / "main" / "resources" / "model" / "skills"


class SkillManagementTest(unittest.TestCase):

    """Tests for skill lifecycle helpers."""
    def setUp(self):
        """Prepare the test fixture."""
        self.skill_name = "unit_temp_skill"
        self.renamed_skill_name = "unit_renamed_skill"

        for name in [self.skill_name, self.renamed_skill_name]:
            shutil.rmtree(SKILLS_DIR / name, ignore_errors=True)
            shutil.rmtree(SKILLS_MODEL_DIR / name, ignore_errors=True)

    def tearDown(self):
        """Clean up after the test."""
        self.setUp()

    def test_create_rename_delete_skill(self):
        """Verify the skill lifecycle helpers."""
        from taius.core.skill_management import (
            create_new_skill,
            delete_skill,
            rename_skill,
        )
        from taius.core.validation import validate_skill_name

        created = create_new_skill(self.skill_name, str(SKILLS_DIR))
        self.assertTrue(Path(created).exists())

        renamed = rename_skill(
            self.skill_name,
            self.renamed_skill_name,
            str(SKILLS_DIR),
            str(SKILLS_MODEL_DIR),
            validate_skill_name,
        )

        self.assertTrue(Path(renamed["source_dir"]).exists())
        self.assertFalse((SKILLS_DIR / self.skill_name).exists())

        removed = delete_skill(
            self.renamed_skill_name,
            str(SKILLS_DIR),
            str(SKILLS_MODEL_DIR),
            validate_skill_name,
        )

        self.assertIn(str(SKILLS_DIR / self.renamed_skill_name), removed)
        self.assertFalse((SKILLS_DIR / self.renamed_skill_name).exists())

    def test_invalid_skill_name_rejected(self):
        """Verify invalid skill names are rejected."""
        from taius.core.validation import validate_skill_name

        with self.assertRaises(ValueError):
            validate_skill_name("../bad")

        with self.assertRaises(ValueError):
            validate_skill_name("_reserved")


if __name__ == "__main__":
    unittest.main()
