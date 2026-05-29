"""Module for test commands."""
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))


class FakeConsole:

    """Test double that captures printed output."""
    def __init__(self):
        """Initialize the instance."""
        self.messages = []

    def print(self, *args, **kwargs):
        """Execute print."""
        self.messages.append(" ".join(str(arg) for arg in args))


class CommandsTest(unittest.TestCase):

    """Tests for command handling."""
    def make_context(self):
        """Build the test command handler context."""
        console = FakeConsole()
        calls = []

        context = {
            "console": console,
            "skills": [],
            "print_help": lambda: calls.append("help"),
            "print_version_info": lambda skills: calls.append("version"),
            "print_status": lambda skills: calls.append("status"),
            "print_doctor": lambda skills: calls.append("doctor"),
            "print_loaded_skills": lambda skills: calls.append("skills"),
            "reload_skills": lambda: calls.append("reload") or [],
            "print_router_examples": lambda: calls.append("router_examples"),
            "print_router_stats": lambda: calls.append("router_stats"),
            "print_routing_threshold": lambda: calls.append("get_threshold"),
            "set_routing_threshold": lambda value: calls.append(("set_threshold", value)) or float(value),
            "export_router": lambda: "router.export.json",
            "import_router": lambda: "router.export.json",
            "backup_all": lambda skills: ["router.export.json"],
            "backup_all_snapshot": lambda skills: ("snapshot", ["router.export.json"]),
            "restore_all": lambda skills: ["router.export.json"],
            "restore_all_snapshot": lambda snapshot, skills: (snapshot, ["router.export.json"]),
            "print_snapshot_list": lambda: calls.append("list_snapshots"),
            "print_skill_examples": lambda skill_name, skills: calls.append(("skill_examples", skill_name)),
            "print_skill_stats": lambda skill_name, skills: calls.append(("skill_stats", skill_name)),
            "print_skill_log": lambda skill_name, skills, line_count=20: calls.append(("skill_log", skill_name, line_count)),
            "print_tail_log": lambda skills, line_count=20: calls.append(("tail_log", line_count)),
            "print_validate_skill": lambda skill_name, skills: calls.append(("validate_skill", skill_name)),
            "disable_skill": lambda skill_name, skills: f"disabled:{skill_name}",
            "enable_skill": lambda skill_name: f"enabled:{skill_name}",
            "create_new_skill": lambda skill_name: f"skills/{skill_name}/skill.py",
            "delete_skill": lambda skill_name: [f"skills/{skill_name}"],
            "rename_skill": lambda old_name, new_name: {
                "source_dir": f"skills/{new_name}",
                "model_dir": f"resources/model/skills/{new_name}",
            },
            "export_skill": lambda skill_name, skills: f"resources/model/skills/{skill_name}/export.json",
            "import_skill": lambda skill_name, skills: f"resources/model/skills/{skill_name}/export.json",
            "teach_router": lambda input_text, skill_name, skills: calls.append(("teach_router", skill_name, input_text)),
            "forget_router": lambda input_text: calls.append(("forget_router", input_text)),
            "log_skill_event": lambda skill, message: calls.append(("log_skill_event", message)),
        }

        return console, calls, context

    def test_basic_commands(self):
        """Verify common command handling."""
        from taius.core.commands import handle_command

        _, calls, context = self.make_context()

        for command, expected in [
            ("/help", "help"),
            ("/version", "version"),
            ("/status", "status"),
            ("/doctor", "doctor"),
            ("/skills", "skills"),
            ("/router-examples", "router_examples"),
            ("/router-stats", "router_stats"),
            ("/get-routing-threshold", "get_threshold"),
            ("/list-snapshots", "list_snapshots"),
        ]:
            status, _ = handle_command(command, context)
            self.assertEqual(status, "handled")
            self.assertIn(expected, calls)

    def test_threshold_command(self):
        """Verify the routing threshold command."""
        from taius.core.commands import handle_command

        _, calls, context = self.make_context()
        status, _ = handle_command("/set-routing-threshold 0.68", context)

        self.assertEqual(status, "handled")
        self.assertIn(("set_threshold", "0.68"), calls)

    def test_skill_view_commands(self):
        """Verify the skill view commands."""
        from taius.core.commands import handle_command

        _, calls, context = self.make_context()

        handle_command("/skill-stats echo_skill", context)
        handle_command("/skill-log sentiment_skill 5", context)
        handle_command("/tail-log 7", context)
        handle_command("/validate-skill echo_skill", context)

        self.assertIn(("skill_stats", "echo_skill"), calls)
        self.assertIn(("skill_log", "sentiment_skill", "5"), calls)
        self.assertIn(("tail_log", "7"), calls)
        self.assertIn(("validate_skill", "echo_skill"), calls)

    def test_quit_commands(self):
        """Verify quit and exit commands."""
        from taius.core.commands import handle_command

        _, _, context = self.make_context()

        status, _ = handle_command("/quit", context)
        self.assertEqual(status, "quit")

        status, _ = handle_command("/exit", context)
        self.assertEqual(status, "quit")


if __name__ == "__main__":
    unittest.main()
