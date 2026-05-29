import builtins
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))


class FakeConsole:
    """Capture console output produced by the runtime loop."""

    def __init__(self):
        self.messages = []

    def print(self, *args, **kwargs):
        self.messages.append(" ".join(str(arg) for arg in args))


class RuntimeTest(unittest.TestCase):
    """Verify runtime prompt behavior."""

    def test_run_taius_loop_restores_terminal_before_prompt(self):
        """The terminal must be restored before the first input prompt."""
        from taius.core import runtime

        calls = []

        def fake_input(prompt):
            calls.append(("input", prompt))
            raise EOFError

        with patch.object(runtime, "restore_terminal_state", side_effect=lambda: calls.append(("restore", None))):
            with patch.object(builtins, "input", side_effect=fake_input):
                runtime.run_taius_loop(
                    console=FakeConsole(),
                    load_skills=lambda: [],
                    train_router_if_needed=lambda skills: None,
                    is_command=lambda input_data: False,
                    handle_command=lambda input_data, context: ("handled", context["skills"]),
                    route_to_skill=lambda input_data, skills: (None, "none", 0.0),
                    get_routing_threshold=lambda: 0.60,
                    teach_router=lambda input_data, skill_name, skills: None,
                    forget_router=lambda input_data: None,
                    build_command_context=lambda skills: {"skills": skills},
                )

        self.assertEqual(calls, [("restore", None), ("input", "Taius> ")])


if __name__ == "__main__":
    unittest.main()
