import unittest
import subprocess
import sys
from src.example import greet


class GreetingAcceptance(unittest.TestCase):
    def test_cli_process_outputs_greeting_and_rejects_blank_input(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.example", " Ada "], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Hello, Ada!")
        rejected = subprocess.run(
            [sys.executable, "-m", "src.example", " "], capture_output=True, text=True
        )
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("A name is required", rejected.stderr)

    def test_greets_trimmed_name(self):
        self.assertEqual(greet("  Ada  "), "Hello, Ada!")

    def test_preserves_unicode(self):
        self.assertEqual(greet("Long · 日本"), "Hello, Long · 日本!")

    def test_rejects_blank_name(self):
        for name in ["", " ", "\t\n"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                greet(name)
