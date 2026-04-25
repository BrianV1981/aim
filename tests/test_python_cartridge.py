import os
import unittest
import zipfile
import json

class TestPythonTroubleshootingCartridge(unittest.TestCase):
    def test_cartridge_exists_and_valid(self):
        # The cartridge should be located in the engrams/ directory
        aim_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Adjust for worktree if necessary
        if 'workspace' in aim_root:
            aim_root = os.path.dirname(os.path.dirname(aim_root))
            
        cartridge_path = os.path.join(aim_root, 'engrams', 'cpython_troubleshooting.engram')
        
        self.assertTrue(os.path.exists(cartridge_path), f'Cartridge not found at {cartridge_path}')
        
        # Validate it is a valid zip file and contains metadata.json
        self.assertTrue(zipfile.is_zipfile(cartridge_path), 'Cartridge is not a valid ZIP archive')
        
        with zipfile.ZipFile(cartridge_path, 'r') as zf:
            files = zf.namelist()
            self.assertIn('metadata.json', files, 'metadata.json is missing from the engram')
            
            # Verify the manifest structure
            with zf.open('metadata.json') as f:
                metadata = json.load(f)
                manifest = metadata.get('manifest', {})
                self.assertEqual(manifest.get('author'), 'A.I.M. System')
                self.assertEqual(manifest.get('version'), '1.0')
