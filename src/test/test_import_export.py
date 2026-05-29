import shutil
import sys
import unittest
import taius.taius as taius
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))


class ImportExportTest(unittest.TestCase):

    def test_echo_skill_export_import(self):

        skills = taius.load_skills(show_disabled=False)
        echo_skill = None

        for skill in skills:
            if skill["name"] == "echo_skill":
                echo_skill = skill
                break

        self.assertIsNotNone(echo_skill)

        export_path = Path(taius.export_skill("echo_skill", skills))
        self.assertTrue(export_path.exists())

        import_path = Path(taius.import_skill("echo_skill", skills))
        self.assertTrue(import_path.exists())
        self.assertEqual(export_path, import_path)

    def test_backup_all_exports_router_and_skills(self):

        skills = taius.load_skills(show_disabled=False)
        exported = taius.backup_all(skills)

        self.assertTrue(exported)
        self.assertTrue(any(path.endswith("router.export.json") for path in exported))
        self.assertTrue(any("echo_skill" in path for path in exported))

        for exported_path in exported:
            self.assertTrue(Path(exported_path).exists())

    def test_snapshot_backup_creates_snapshot_folder(self):

        skills = taius.load_skills(show_disabled=False)
        snapshot_dir, exported = taius.backup_all_snapshot(skills)

        snapshot_path = Path(snapshot_dir)
        self.assertTrue(snapshot_path.exists())
        self.assertTrue((snapshot_path / "core" / "router.export.json").exists())
        self.assertTrue(exported)

        shutil.rmtree(snapshot_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
