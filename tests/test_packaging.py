import re
import unittest
from pathlib import Path


class TestPackagingMetadata(unittest.TestCase):
    def test_optional_extras_include_dev_and_mcp(self):
        text = Path("pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("[project.optional-dependencies]", text)
        self.assertRegex(text, r"(?m)^dev\s*=")
        self.assertRegex(text, r"(?m)^mcp\s*=")
        self.assertRegex(text, r'"mcp[^"]*"')

    def test_mcp_console_script_is_declared(self):
        text = Path("pyproject.toml").read_text(encoding="utf-8")

        self.assertIsNotNone(
            re.search(
                r'(?m)^decision-pga-mcp\s*=\s*"decision_pga\.mcp_server:main"',
                text,
            )
        )


if __name__ == "__main__":
    unittest.main()
