import os
import sys
import unittest

# Dynamic Root Discovery for tests
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return current

AIM_ROOT = find_aim_root()
sys.path.append(AIM_ROOT)
sys.path.append(os.path.join(AIM_ROOT, "src"))
sys.path.append(os.path.join(AIM_ROOT, "scripts"))

from src.handoff_pulse_generator import atomic_write

class TestAtomicWrite(unittest.TestCase):
    def test_atomic_write_success(self):
        test_path = "test_file.md"
        content = "Hello Atomic World"
        
        # Ensure file is clean
        if os.path.exists(test_path):
            os.remove(test_path)
            
        atomic_write(test_path, content)
        
        self.assertTrue(os.path.exists(test_path))
        with open(test_path, 'r') as f:
            self.assertEqual(f.read(), content)
            
        os.remove(test_path)

    def test_atomic_write_overwrite(self):
        test_path = "test_file_overwrite.md"
        
        # Create initial file
        with open(test_path, 'w') as f:
            f.write("Original Content")
            
        new_content = "New Atomic Content"
        atomic_write(test_path, new_content)
        
        with open(test_path, 'r') as f:
            self.assertEqual(f.read(), new_content)
            
        os.remove(test_path)

if __name__ == "__main__":
    unittest.main()
