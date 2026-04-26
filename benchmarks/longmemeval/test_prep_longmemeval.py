import unittest
from prep_longmemeval_md import convert_to_markdown, process_content

class TestDataPreparation(unittest.TestCase):
    def test_process_content_string(self):
        self.assertEqual(process_content("Hello  World"), "Hello  World")
        self.assertEqual(process_content("Multiple\n\n\nNewlines"), "Multiple\n\nNewlines")
        
    def test_process_content_list(self):
        c = [{"text": "Part 1."}, {"text": "Part 2."}]
        self.assertEqual(process_content(c), "Part 1. Part 2.")

    def test_convert_to_markdown(self):
        messages = [
            {"speaker": "user", "content": "How do I exit vim?"},
            {"speaker": "assistant", "content": "You press ESC, type :wq, and hit Enter."}
        ]
        expected_md = (
            "# Flight Recorder: test_session_1\n\n"
            "## User\n"
            "How do I exit vim?\n\n"
            "## Assistant\n"
            "You press ESC, type :wq, and hit Enter.\n"
        )
        result = convert_to_markdown("test_session_1", messages)
        self.assertEqual(result, expected_md)

if __name__ == '__main__':
    unittest.main()