import unittest
import json
import os
import sys
import tempfile
from unittest.mock import patch

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))

from extract_signal import extract_signal, skeleton_to_markdown


class TestFormatDetection(unittest.TestCase):
    """Phase 2, Issue #3: Extract Signal Format Auto-Detection — TDD tests."""

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

    # ── Gemini JSONL format tests (backward compat) ──

    def _write_jsonl(self, messages):
        path = os.path.join(self.test_dir.name, "test.jsonl")
        with open(path, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg) + "\n")
        return path

    def test_gemini_jsonl_still_works(self):
        """Backward compat: Gemini JSONL extraction unchanged."""
        path = self._write_jsonl([
            {"role": "user", "timestamp": "T1", "content": "Hello"},
            {"type": "gemini", "timestamp": "T2", "content": "Reply", "thoughts": ["thinking"]},
        ])
        result = extract_signal(path)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[1]["role"], "gemini")
        self.assertEqual(result[1]["thoughts"], ["thinking"])

    # ── OpenCode export JSON format tests ──

    def _write_opencode_json(self, messages):
        path = os.path.join(self.test_dir.name, "test.json")
        data = {
            "info": {
                "id": "ses_test",
                "title": "Test Session",
                "directory": "/home/user/project",
                "version": "1.14.31",
                "time": {"created": 1700000000000, "updated": 1700000100000},
            },
            "messages": messages,
        }
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def _make_oc_msg(self, role, content, **kwargs):
        """Build a message in real OpenCode export format using parts array."""
        parts = []
        if role == "assistant" and kwargs.get("reasoning"):
            parts.append({"type": "reasoning", "text": kwargs["reasoning"]})
        if content:
            parts.append({"type": "text", "text": content})
        if kwargs.get("tool_calls"):
            for tc in kwargs["tool_calls"]:
                parts.append({
                    "type": "tool",
                    "tool": {
                        "name": tc.get("name", tc.get("function", {}).get("name", "unknown")),
                        "args": tc.get("args", tc.get("function", {}).get("arguments", {})),
                    },
                })
        msg = {
            "info": {
                "role": role,
                "time": {"created": kwargs.get("ts", 1700000000000)},
            },
            "id": kwargs.get("msg_id", "msg_test"),
            "parts": parts,
        }
        return msg

    def test_opencode_user_message(self):
        """OpenCode user message: role from msg.info.role, content extracted."""
        path = self._write_opencode_json([
            self._make_oc_msg("user", "What is the issue?"),
        ])
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[0]["text"], "What is the issue?")

    def test_opencode_assistant_message(self):
        """OpenCode assistant role is recognized as agent turn."""
        path = self._write_opencode_json([
            self._make_oc_msg("assistant", "I found the bug."),
        ])
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "assistant")
        self.assertEqual(result[0]["text"], "I found the bug.")

    def test_opencode_mixed_conversation(self):
        """OpenCode stream with interleaved user/assistant turns."""
        path = self._write_opencode_json([
            self._make_oc_msg("user", "Q1"),
            self._make_oc_msg("assistant", "A1"),
            self._make_oc_msg("user", "Q2"),
            self._make_oc_msg("assistant", "A2"),
        ])
        result = extract_signal(path)
        self.assertEqual(len(result), 4)
        roles = [m["role"] for m in result]
        self.assertEqual(roles, ["user", "assistant", "user", "assistant"])

    def test_opencode_timestamp_format(self):
        """OpenCode timestamp from msg.info.time.created (milliseconds epoch)."""
        path = self._write_opencode_json([
            self._make_oc_msg("user", "Hello", ts=1701234567890),
        ])
        result = extract_signal(path)
        self.assertIn("timestamp", result[0])
        self.assertNotEqual(result[0]["timestamp"], "Unknown")

    def test_opencode_tool_calls(self):
        """OpenCode tool calls extracted from parts array for agent turns."""
        path = self._write_opencode_json([
            self._make_oc_msg("assistant", "Let me check.", tool_calls=[
                {"name": "read_file", "args": {"path": "/src/main.py"}},
            ]),
        ])
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "assistant")
        self.assertEqual(len(result[0].get("actions", [])), 1)
        self.assertEqual(result[0]["actions"][0]["tool"], "read_file")

    def test_opencode_user_list_content(self):
        """OpenCode user message with multiple text parts."""
        path = self._write_opencode_json([
            {
                "info": {"role": "user", "time": {"created": 1700000000000}},
                "id": "msg_abc",
                "parts": [
                    {"type": "text", "text": "Part A "},
                    {"type": "text", "text": "Part B"},
                ],
            },
        ])
        result = extract_signal(path)
        self.assertEqual(result[0]["text"], "Part A  Part B")

    # ── skeleton_to_markdown with assistant / AGENT label ──

    def test_skeleton_to_markdown_agent_label_for_assistant(self):
        """Assistant turns labelled 'AGENT' in markdown heading."""
        skeleton = [
            {"role": "user", "text": "Hello", "timestamp": "T1"},
            {
                "role": "assistant",
                "text": "Hi there",
                "timestamp": "T2",
                "thoughts": ["Let me assist."],
                "actions": [{"tool": "search", "intent": "find bugs"}],
            },
        ]
        md = skeleton_to_markdown(skeleton, "ses_test")
        self.assertIn("## 🤖 AGENT (T2)", md)
        self.assertIn("Hi there", md)
        self.assertIn("Internal Monologue", md)
        self.assertIn("Tools Executed", md)
        self.assertIn("search", md)

    def test_skeleton_to_markdown_gemini_still_aim(self):
        """Gemini turns still labelled 'A.I.M.' (backward compat)."""
        skeleton = [
            {"role": "user", "text": "Q", "timestamp": "T1"},
            {"role": "gemini", "text": "A", "timestamp": "T2"},
            {"role": "model", "text": "A2", "timestamp": "T3"},
        ]
        md = skeleton_to_markdown(skeleton, "ses_test")
        self.assertIn("## 🤖 A.I.M. (T2)", md)
        self.assertIn("## 🤖 A.I.M. (T3)", md)
        self.assertNotIn("AGENT", md)

    def test_skeleton_to_markdown_user_still_user(self):
        """User turns unchanged in markdown."""
        skeleton = [{"role": "user", "text": "Hello", "timestamp": "T1"}]
        md = skeleton_to_markdown(skeleton, "ses_test")
        self.assertIn("## 👤 USER (T1)", md)

    def test_opencode_system_message_skipped(self):
        """System messages from OpenCode format still recognized."""
        path = self._write_opencode_json([
            {
                "info": {"role": "system", "time": {"created": 1700000000000}},
                "id": "msg_sys",
                "content": "You are a coding assistant.",
            },
        ])
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "system")


if __name__ == "__main__":
    unittest.main()
