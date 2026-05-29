import shutil
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))


class SkillManagementTest(unittest.TestCase):

    def setUp(self):
        self.skill_name = "unit_temp_skill"
        self.renamed_skill_name = "unit_renamed_skill"

        for name in [self.skill_name, self.renamed_skill_name]:
            shutil.rmtree(PROJECT_DIR / "skills" / name, ignore_errors=True)
            shutil.rmtree(PROJECT_DIR / "resources" / "model" / "skills" / name, ignore_errors=True)

    def tearDown(self):
        self.setUp()

    def test_create_rename_delete_skill(self):
        from taius.core.skill_management import (
            create_new_skill,
            delete_skill,
            rename_skill,
        )
        from taius.core.validation import validate_skill_name

        created = create_new_skill(self.skill_name, "skills")
        self.assertTrue((PROJECT_DIR / created).exists())

        renamed = rename_skill(
            self.skill_name,
            self.renamed_skill_name,
            "skills",
            "resources/model/skills",
            validate_skill_name,
        )

        self.assertTrue((PROJECT_DIR / renamed["source_dir"]).exists())
        self.assertFalse((PROJECT_DIR / "skills" / self.skill_name).exists())

        removed = delete_skill(
            self.renamed_skill_name,
            "skills",
            "resources/model/skills",
            validate_skill_name,
        )

        self.assertIn(f"skills/{self.renamed_skill_name}", removed)
        self.assertFalse((PROJECT_DIR / "skills" / self.renamed_skill_name).exists())

    def test_invalid_skill_name_rejected(self):
        from taius.core.validation import validate_skill_name

        with self.assertRaises(ValueError):
            validate_skill_name("../bad")

        with self.assertRaises(ValueError):
            validate_skill_name("_reserved")


if __name__ == "__main__":
    unittest.main()
