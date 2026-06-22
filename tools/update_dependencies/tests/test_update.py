"""Unit tests for the update script that runs all updater scripts."""

import unittest
from unittest.mock import Mock, call, patch

from update import PARALLEL_SCRIPTS, SEQUENTIAL_SCRIPTS, run_script, update_dependencies


@patch("subprocess.run")
class UpdateTest(unittest.TestCase):
    """Unit tests for the update_dependencies function."""

    def test_run_script(self, mock_run: Mock):
        """Test that a script is run and its exit code is returned."""
        mock_run.return_value = Mock(returncode=0)
        self.assertEqual(0, run_script("dockerfile_base_image"))
        args = mock_run.call_args.args[0]
        self.assertEqual("update_dockerfile_base_image.py", args[-1].split("/")[-1])

    def test_all_scripts_are_run(self, mock_run: Mock):
        """Test that all updater scripts are run, the parallel ones before the sequential ones."""
        mock_run.return_value = Mock(returncode=0)
        self.assertEqual(0, update_dependencies())
        scripts_run = [run_call.args[0][-1].split("/")[-1] for run_call in mock_run.call_args_list]
        expected = [f"update_{name}.py" for name in (*PARALLEL_SCRIPTS, *SEQUENTIAL_SCRIPTS)]
        self.assertEqual(sorted(expected), sorted(scripts_run))
        self.assertEqual([f"update_{name}.py" for name in SEQUENTIAL_SCRIPTS], scripts_run[-len(SEQUENTIAL_SCRIPTS) :])

    def test_sequential_scripts_run_in_order(self, mock_run: Mock):
        """Test that the sequential scripts run after the parallel ones, node_engine before package_json."""
        mock_run.return_value = Mock(returncode=0)
        update_dependencies()
        self.assertEqual(
            [call("update_node_engine.py"), call("update_package_json.py")],
            [call(run_call.args[0][-1].split("/")[-1]) for run_call in mock_run.call_args_list[-2:]],
        )

    def test_highest_exit_code_is_returned(self, mock_run: Mock):
        """Test that the highest exit code of all scripts is returned."""
        mock_run.return_value = Mock(returncode=1)
        self.assertEqual(1, update_dependencies())
