import unittest
import json
import os
import tempfile
from scripts.extract_signal import extract_signal

class TestExtractSignal(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

    def create_temp_json(self, data):
        path = os.path.join(self.test_dir.name, "test.json")
        with open(path, 'w') as f:
            json.dump(data, f)
        return path

    def test_user_message_string_content(self):
        data = {
            "messages": [
                {"role": "user", "timestamp": "2023-10-27T10:00:00", "content": "Hello world"}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'user')
        self.assertEqual(result[0]['text'], 'Hello world')

    def test_user_message_list_content(self):
        data = {
            "messages": [
                {
                    "role": "user",
                    "timestamp": "2023-10-27T10:00:01",
                    "content": [{"text": "Part 1 "}, {"text": "Part 2"}]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['text'], 'Part 1  Part 2')

    def test_model_message_with_thoughts_and_tools(self):
        data = {
            "session_history": [
                {
                    "role": "model",
                    "timestamp": "2023-10-27T10:00:02",
                    "content": "I will help you.",
                    "thoughts": ["thinking..."],
                    "toolCalls": [
                        {"name": "test_tool", "args": {"key": "value"}}
                    ]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'model')
        self.assertEqual(result[0]['text'], 'I will help you.')
        self.assertEqual(result[0]['thoughts'], ["thinking..."])
        self.assertEqual(len(result[0]['actions']), 1)
        self.assertEqual(result[0]['actions'][0]['tool'], "test_tool")
        self.assertEqual(result[0]['actions'][0]['intent'], "{'key': 'value'}")

    def test_model_message_alternative_fields(self):
        data = {
            "messages": [
                {
                    "type": "gemini",
                    "timestamp": "2023-10-27T10:00:03",
                    "content": "Alternative fields test.",
                    "tool_calls": [
                        {
                            "function": {"name": "alt_tool", "arguments": {"foo": "bar"}}
                        }
                    ]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['role'], 'gemini')
        self.assertEqual(result[0]['actions'][0]['tool'], "alt_tool")
        self.assertEqual(result[0]['actions'][0]['intent'], "{'foo': 'bar'}")

    def test_invalid_json(self):
        path = os.path.join(self.test_dir.name, "invalid.json")
        with open(path, 'w') as f:
            f.write("not a json")
        result = extract_signal(path)
        self.assertTrue(result.startswith("Extraction Error"))

    def test_missing_messages_key(self):
        data = {"foo": "bar"}
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result, [])

    def test_tool_truncation(self):
        long_args = "a" * 300
        data = {
            "messages": [
                {
                    "role": "model",
                    "toolCalls": [{"name": "long_tool", "args": long_args}]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(len(result[0]['actions'][0]['intent']), 200)

    def test_none_messages(self):
        data = {"messages": None}
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result, [])

    def test_system_message(self):
        data = {
            "messages": [
                {"role": "system", "timestamp": "2023-10-27T10:00:04", "content": "You are a helpful assistant."}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'system')
        self.assertEqual(result[0]['text'], "You are a helpful assistant.")

    def test_tool_result_message_skipped(self):
        data = {
            "messages": [
                {"role": "tool", "timestamp": "2023-10-27T10:00:05", "content": "Success"}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(len(result), 0)

    def test_missing_role_and_type_skipped(self):
        data = {
            "messages": [
                {"timestamp": "2023-10-27T10:00:06", "content": "Ghost message"}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(len(result), 0)

    def test_missing_tool_call_fields(self):
        data = {
            "messages": [
                {
                    "role": "model",
                    "tool_calls": [{}]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['actions'][0]['tool'], None)
        self.assertEqual(result[0]['actions'][0]['intent'], 'None')

    def test_empty_messages_list(self):
        data = {"messages": []}
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result, [])

    def test_non_dict_message_skipped(self):
        data = {"messages": ["not a dict"]}
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result, [])

    def test_missing_timestamp_defaults_to_unknown(self):
        data = {
            "messages": [
                {"role": "user", "content": "hello"}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['timestamp'], 'Unknown')

    def test_none_content_returns_empty_string(self):
        data = {
            "messages": [
                {"role": "user", "content": None}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['text'], "")

    def test_non_dict_tool_call_skipped(self):
        data = {
            "messages": [
                {
                    "role": "model",
                    "tool_calls": ["not a dict"]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['actions'], [])

    def test_list_content_with_non_dict_items(self):
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "hello"}, "not a dict", {"other": "field"}]
                }
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['text'], "hello")


    def test_strip_excess_newlines(self):
        data = {
            "messages": [
                {"role": "user", "timestamp": "2023-10-27T10:00:00", "content": "Hello\n\n\n\nworld\n\ntest"}
            ]
        }
        path = self.create_temp_json(data)
        result = extract_signal(path)
        self.assertEqual(result[0]['text'], "Hello\n\nworld\n\ntest")

if __name__ == '__main__':

    unittest.main()

