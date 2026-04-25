import unittest
import subprocess
import json
import os
import sys

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
venv_bin = os.path.dirname(sys.executable)

class TestMCPServer(unittest.TestCase):
    """
    TDD Phase 19: GREEN PHASE
    Verifies that the A.I.M. MCP Server tools and resources are correctly exposed.
    """
    
    def test_mcp_exposure(self):
        """Verifies search_engram tool and project-context resource are live."""
        server_script = os.path.join(aim_root, "aim_core/mcp_server.py")
        fastmcp_bin = os.path.join(venv_bin, "fastmcp")
        
        try:
            # Use fastmcp inspect to get structured data
            result = subprocess.run(
                [fastmcp_bin, "inspect", server_script, "--format", "mcp"],
                capture_output=True, text=True, check=True
            )
            
            # Clean raw newlines inside JSON strings (bug in some fastmcp outputs)
            raw_output = result.stdout
            # This is a bit of a hack to handle invalid control characters
            clean_output = raw_output.replace('\n', '\\n').replace('\r', '\\r')
            # But wait, we only want to replace newlines INSIDE strings. 
            # Real JSON newlines (formatting) should stay.
            # A simpler way is to use strict=False or regex.
            
            try:
                data = json.loads(raw_output)
            except json.JSONDecodeError:
                # Retry with a more aggressive cleanup if first pass fails
                # Remove actual control characters (non-printable)
                import re
                processed = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', raw_output)
                data = json.loads(processed)
            
            # 1. Verify Tool
            tools = data.get("tools", [])
            tool_names = [t["name"] for t in tools]
            self.assertIn("search_engram", tool_names, "Tool 'search_engram' not found")
            
            # 2. Verify Resource
            resources = data.get("resources", [])
            resource_uris = [r["uri"] for r in resources]
            self.assertIn("aim://project-context", resource_uris, "Resource 'aim://project-context' not found")
            
        except Exception as e:
            self.fail(f"MCP Exposure test failed: {e}")

if __name__ == "__main__":
    unittest.main()
