import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestAgentToolkitAdoptionArtifacts(unittest.TestCase):
    def test_agent_examples_are_cli_diagnosable_and_cover_expected_states(self):
        expected = {
            "tool_action_ambiguity.json": "binary_ambiguity",
            "rag_evidence_conflict.json": "binary_ambiguity",
            "document_extraction_routing.json": "diffuse_uncertainty",
            "multi_step_agent_drift.json": "regime_shift",
            "abstain_defer_decision.json": "stable",
        }

        for filename, expected_state in expected.items():
            with self.subTest(filename=filename):
                path = Path("examples/agent") / filename
                payload = json.loads(path.read_text(encoding="utf-8"))
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "decision_pga.cli",
                        "diagnose",
                        "--pretty",
                        str(path),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                output = json.loads(result.stdout)

                self.assertEqual(result.returncode, 0)
                self.assertEqual(output["diagnostic"]["state"], expected_state)
                self.assertIn("source", payload)
                self.assertIn("label", payload)

    def test_kinematic_trajectory_example_runs_through_cli(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "decision_pga.cli",
                "diagnose",
                "examples/agent/kinematic_trajectory_rag_tool_whiplash.json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "kinematic_trajectory")
        self.assertGreater(output["diagnostic"]["systemic_jerk"], 0.0)

    def test_agent_toolkit_doc_has_five_minute_agent_path(self):
        text = Path("docs/agent-toolkit.md").read_text(encoding="utf-8")

        for phrase in [
            "Use Decision-PGA In 5 Minutes",
            "CLI diagnosis",
            "Python API diagnosis",
            "Local MCP server",
            "What the input means",
            "Calling from an agent loop",
            "Interpreting states and actions",
            "not a production safety layer",
            "examples/agent/tool_action_ambiguity.json",
            "examples/agent/rag_evidence_conflict.json",
            "examples/agent/document_extraction_routing.json",
            "examples/agent/multi_step_agent_drift.json",
            "examples/agent/abstain_defer_decision.json",
        ]:
            self.assertIn(phrase, text)

    def test_mcp_registry_metadata_and_quickstart_are_prepared_not_submitted(self):
        metadata = json.loads(Path("docs/mcp-registry/server.json").read_text(encoding="utf-8"))
        quickstart = Path("docs/mcp-server.md").read_text(encoding="utf-8")

        self.assertEqual(metadata["name"], "io.github.zmichels/decision-pga")
        self.assertEqual(metadata["repository"]["url"], "https://github.com/zmichels/Decision-PGA")
        self.assertEqual(metadata["packages"][0]["registryType"], "pypi")
        self.assertIn("decision-pga-mcp", json.dumps(metadata))
        self.assertIn("mcp-name: io.github.zmichels/decision-pga", Path("README.md").read_text(encoding="utf-8"))
        self.assertIn("Draft MCP Registry Metadata", quickstart)
        self.assertIn("Why MCP", quickstart)
        self.assertIn("npx @modelcontextprotocol/inspector decision-pga-mcp", quickstart)
        self.assertIn("The metadata is prepared but not submitted", quickstart)

    def test_release_and_community_adoption_files_are_present(self):
        release_checklist = Path("docs/release-checklist.md").read_text(encoding="utf-8")
        community = Path("docs/community-engagement.md").read_text(encoding="utf-8")
        workflow = Path(".github/workflows/pypi-publish.yml").read_text(encoding="utf-8")

        self.assertIn("Release Readiness Checklist", release_checklist)
        self.assertIn("pip install git+https://github.com/zmichels/Decision-PGA", release_checklist)
        self.assertIn("Trusted Publishing", release_checklist)
        self.assertIn("Hugging Face Space", release_checklist)
        self.assertIn("GitHub Discussions", community)
        self.assertIn("agent integration", community)
        self.assertIn("document extraction workflows", community)
        self.assertIn("workflow_dispatch", workflow)
        self.assertNotIn("release:", workflow)
        self.assertNotIn("push:", workflow)

    def test_issue_discussion_templates_and_outreach_drafts_exist(self):
        required_paths = [
            ".github/ISSUE_TEMPLATE/adapter_request.md",
            ".github/ISSUE_TEMPLATE/diagnostic_scenario.md",
            ".github/ISSUE_TEMPLATE/mcp_integration_issue.md",
            ".github/ISSUE_TEMPLATE/example_contribution.md",
            ".github/DISCUSSION_TEMPLATE/use-cases.yml",
            ".github/DISCUSSION_TEMPLATE/agent-integration.yml",
            ".github/DISCUSSION_TEMPLATE/uncertainty-metrics.yml",
            ".github/DISCUSSION_TEMPLATE/document-extraction-workflows.yml",
            "docs/outreach/developer-essay-mirror.md",
            "docs/outreach/launch-posts.md",
            "examples/huggingface-space/README.md",
            "examples/huggingface-space/app.py",
            "examples/huggingface-space/requirements.txt",
        ]

        for relative in required_paths:
            with self.subTest(path=relative):
                path = Path(relative)
                self.assertTrue(path.exists(), relative)
                self.assertGreater(path.stat().st_size, 0, relative)


if __name__ == "__main__":
    unittest.main()
