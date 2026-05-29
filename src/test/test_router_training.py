"""Module for test router training."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))


class NullConsole:

    """Test double that discards printed output."""
    def print(self, *args, **kwargs):
        """Execute print."""
        pass

    def rule(self, *args, **kwargs):
        """Execute rule."""
        pass


class RouterTrainingTest(unittest.TestCase):

    """Tests for router training updates."""
    def test_teach_and_forget_router_example(self):
        """Verify router teach and forget behavior."""
        import taius

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            train_path = temp_path / "router.csv"
            model_path = temp_path / "router.json"

            with train_path.open("w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["input", "skill_name"])
                writer.writeheader()
                writer.writerow({
                    "input": "echo hello",
                    "skill_name": "echo_skill",
                })

            skills = [
                {
                    "name": "echo_skill",
                    "description": {
                        "id": "core.echo",
                        "version": "0.1.0",
                        "contract_version": "1.0",
                        "input_type": "text",
                        "output_type": "text",
                    },
                }
            ]

            with patch.object(taius, "ROUTER_TRAIN_PATH", str(train_path)), \
                 patch.object(taius, "ROUTER_MODEL_PATH", str(model_path)), \
                 patch.object(taius, "console", NullConsole()):

                taius.train_router_from_existing_file()
                self.assertTrue(model_path.exists())

                taius.teach_router("echo unit test", "echo_skill", skills)

                with train_path.open("r", newline="") as file:
                    rows = list(csv.DictReader(file))

                self.assertIn(
                    {
                        "input": "echo unit test",
                        "skill_name": "echo_skill",
                    },
                    rows,
                )

                taius.forget_router("echo unit test")

                with train_path.open("r", newline="") as file:
                    rows = list(csv.DictReader(file))

                self.assertNotIn(
                    {
                        "input": "echo unit test",
                        "skill_name": "echo_skill",
                    },
                    rows,
                )


if __name__ == "__main__":
    unittest.main()
